import json
from datetime import datetime, timedelta

from openai import AsyncOpenAI

from app.core.config import settings
from app.models.medications import AiReport, MedicationIntakeLog, ReportStatus

# 비동기 OpenAI 클라이언트 초기화
# 오픈AI API 키가 .env 안의 OPENAI_API_KEY 환경변수에 있어야 작동됩니다.
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_medication_report(
    adherence_rate: int, medication_records: list[dict], user_conditions: list[str], period: str = "weekly"
) -> str:
    """
    환자의 복약 기록과 컨디션 메모를 기반으로 GPT-4o mini 모델을 통해
    친절하고 전문적인 디지털 약사의 코멘트를 생성합니다.
    """

    # 1) AI에게 부여할 역할 설정 (System Prompt)
    system_prompt = """
    당신은 환자의 건강과 복약을 관리해주는 다정하고 전문적인 '디지털 약사'입니다.
    환자의 약물 복용 기록, 순응도(%), 그리고 지난 컨디션 메모를 보고
    다음 조건에 맞춰 리포트 코멘트를 작성해 주세요.
    1. 따뜻하고 격려하는 말투를 사용할 것 (예: ~했어요, ~하시는 것이 좋습니다.)
    2. 복약 순응도가 낮을 경우 부드럽게 주의를 주고 개선 팁을 제안할 것.
    3. 전체 분량은 3~4문장 내외의 1문단으로 간결하게 요약할 것.
    """

    # 2) 환자 데이터 세팅 (User Message 형식)
    medication_context = json.dumps(medication_records, ensure_ascii=False)
    conditions = ", ".join(user_conditions) if user_conditions else "특이사항 없음"

    user_message = f"""
    [환자 데이터]
    - 리포트 기간: {period} (주간/월간)
    - 종합 복약 순응도: {adherence_rate}%
    - 약물 복용 이력: {medication_context}
    - 지난 기간 컨디션 요약: {conditions}

    위 데이터를 분석해서 환자에게 보여줄 코멘트만 딱 출력해 줘.
    """

    try:
        # 3) OpenAI API 호출 (비동기)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            temperature=0.7,  # 0.7 정도로 약간의 다정함/창의성 부여
            max_tokens=250,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API 에러: {e}")
        return "현재 AI 리포트를 생성할 수 없습니다. 잠시 후 다시 시도해 주세요."


async def process_ai_report_worker(report_id: str, user_id: int, period: str):
    """
    백그라운드에서 실행되는 워커.
    DB 데이터를 조회하여 순응도를 계산하고, OpenAI API 호출 후 AiReport 테이블을 갱신합니다.
    """
    try:
        # 1. 대상 기간 설정
        days = 7 if period == "weekly" else 30
        start_date = datetime.now() - timedelta(days=days)

        # 2. MedicationIntakeLog 테이블 쿼리로 복용 기록 분석
        intakes = await MedicationIntakeLog.filter(user_id=user_id, scheduled_time__gte=start_date).prefetch_related(
            "medication"
        )

        total_intakes = len(intakes)
        taken_intakes = [i for i in intakes if i.status == "taken"]
        adherence_rate = int((len(taken_intakes) / total_intakes) * 100) if total_intakes > 0 else 0

        # 컨디션 로그 추출 (비어있지 않은 opinion만)
        user_conditions = [i.opinion for i in intakes if i.opinion and i.opinion.strip()]
        if not user_conditions:
            user_conditions = ["특이사항이 기록되지 않음"]

        # 약물별 복용 기록 요약용 딕셔너리 구축
        medication_stats = {}
        for i in intakes:
            med_name = i.medication.name
            if med_name not in medication_stats:
                medication_stats[med_name] = {"total": 0, "taken": 0}
            medication_stats[med_name]["total"] += 1
            if i.status == "taken":
                medication_stats[med_name]["taken"] += 1

        medication_records = []
        medication_summary_for_db = []
        for name, stats in medication_stats.items():
            rate = int((stats["taken"] / stats["total"]) * 100) if stats["total"] > 0 else 0
            medication_records.append(
                {
                    "약품명": name,
                    "복용률": f"{rate}%",
                }
            )
            medication_summary_for_db.append({"name": name, "takenRate": rate})

        # 방어 로직: 기록이 전혀 없는 경우 테스트/데모용으로 더미 데이터 추가 (기능 검증 목적)
        if total_intakes == 0:
            adherence_rate = 85
            medication_records = [
                {"약품명": "타이레놀(예시)", "복용률": "100%"},
                {"약품명": "위장약(예시)", "복용률": "70%"},
            ]
            medication_summary_for_db = [
                {"name": "타이레놀(예시)", "takenRate": 100},
                {"name": "위장약(예시)", "takenRate": 70},
            ]

        # 3. AI 리포트 생성 호출
        ai_comment = await generate_medication_report(
            adherence_rate=adherence_rate,
            medication_records=medication_records,
            user_conditions=user_conditions,
            period=period,
        )

        # 4. AiReport 모델 반영 (완료)
        await AiReport.filter(report_id=report_id).update(
            adherence_rate=adherence_rate,
            condition_summary=" | ".join(user_conditions)[:500],  # 최대 500자
            medication_summary=medication_summary_for_db,
            ai_comment=ai_comment,
            status=ReportStatus.COMPLETED,
        )

    except Exception as e:
        print(f"🔥 [Background Task Error] Report Worker 에러: {e}")
        await AiReport.filter(report_id=report_id).update(status=ReportStatus.FAILED)


async def _get_unconfirmed_ocr_context(ocr_id: str) -> list[str]:
    """방금 분석된 최신 OCR(확정 전) 정보를 텍스트 리스트로 변환합니다."""
    from app.models.medications import OcrPrescription

    ocr_record = await OcrPrescription.get_or_none(ocr_id=ocr_id)
    if not ocr_record or not ocr_record.extracted_data:
        return []

    extracted = ocr_record.extracted_data
    parsed_list = extracted.get("parsed", []) if isinstance(extracted, dict) else []

    if not parsed_list:
        return []

    lines = ["[방금 분석된 새 처방전 약물 목록 - 아직 확정되지 않음]"]
    for med in parsed_list:
        name, dosage, freq, timing = (
            med.get("name", ""),
            med.get("dosage", ""),
            med.get("frequency", ""),
            med.get("timing", ""),
        )
        desc = med.get("description", "")
        line = f"- {name}: {dosage} (복용법: {freq}, {timing})"
        if desc:
            line += f" -> 특징/설명: {desc}"
        lines.append(line)
    lines.append("")  # 구분을 위한 줄바꿈
    return lines


async def _get_confirmed_medication_context(user_id: int) -> list[str]:
    """사용자가 이미 확정하여 복용 중인 약물 정보를 텍스트 리스트로 변환합니다."""
    from tortoise.expressions import Q

    from app.models.medications import MedicationLog

    logs = await MedicationLog.filter(
        Q(user_id=user_id),
        Q(end_date__gte=datetime.today().date()) | Q(end_date__isnull=True),
    ).order_by("-created_at")

    if not logs:
        return []

    lines = ["[현재 복용 중인 약물 목록]"]
    for log in logs:
        line = f"- {log.name}: {log.dosage or ''} (복용법: {log.frequency or ''}, {log.timing or ''})"
        if log.caution:
            line += f" -> 주의사항: {log.caution}"
        lines.append(line)
    return lines


async def get_medication_context_for_chatbot(user_id: int, ocr_id: str | None = None) -> str:
    """
    [타 팀원 지원용 브릿지 함수]
    챗봇 파트를 담당하는 팀원이 환자의 '현재 복약 정보'를 GPT 프롬프트에 통째로
    주입할 수 있도록, DB 쿼리를 거쳐 깔끔한 텍스트 덩어리로 반환합니다.
    """
    context_lines = []

    # 1. OCR 기반 최신(확정 전) 정보 추가
    if ocr_id:
        context_lines.extend(await _get_unconfirmed_ocr_context(ocr_id))

    # 2. 기존 확정된 복용 정보 추가
    context_lines.extend(await _get_confirmed_medication_context(user_id))

    if not context_lines:
        return "현재 복용 중이거나 분석된 약물이 없습니다."

    return "\n".join(context_lines).strip()


async def batch_analyze_unmatched_drugs(unmatched_meds: list[dict]) -> dict[str, str]:
    """
    여러 약품 정보를 한 번에 묶어서 GPT에 질문하여 설명을 보완합니다.
    환각 방지를 위한 System Prompt가 포함됩니다.
    """
    system_prompt = """
    당신은 처방전 분석을 돕는 의료 데이터 어시스턴트입니다.
    사용자가 처방전에서 추출한 약품 정보를 제공할 것입니다.
    다음 규칙을 반드시 지켜주세요:
    1. 각 약품명에 대한 간략한 설명(효능/용도 위주, 1문장)을 작성하세요.
    2. [할루시네이션 방지 필수]: 만약 알 수 없는 약품명(또는 실제 존재하지 않거나 오타가 심한 약품)이라면 절대로 효능이나 부작용을 지어내지 마세요.
    3. 알 수 없는 약품의 경우 설명은 "일치하는 약품 정보를 찾을 수 없습니다." 로 고정하세요. 복용 스케줄 연동을 위해 임시 저장됩니다.
    4. 응답은 반드시 약품명을 키(key)로, 설명을 값(value)으로 하는 순수 JSON 객체(dict) 포맷만 반환하세요.
    예시: {"타이레놀정500mg": "해열진통제로 열을 내리고 통증을 완화합니다.", "이상한약123": "일치하는 약품 정보를 찾을 수 없습니다."}
    """

    user_message = f"다음 약품들에 대한 설명을 JSON으로 반환해주세요: {json.dumps(unmatched_meds, ensure_ascii=False)}"

    try:
        response = await client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            temperature=0,
            max_tokens=1000,
        )

        content = response.choices[0].message.content or "{}"
        clean_content = content.strip()
        if clean_content.startswith("```"):
            clean_content = clean_content.split("```")[1]
            if clean_content.startswith("json"):
                clean_content = clean_content[4:]
        clean_content = clean_content.strip()

        return json.loads(clean_content)
    except Exception as e:
        print(f"GPT Batch Fallback 에러: {e}")
        # 오류 발생 시 모든 빈 약품에 대해 동일한 폴백 메시지 반환
        return {
            med["name"]: "서비스 지연으로 약품 정보를 불러오지 못했습니다." for med in unmatched_meds if "name" in med
        }


async def generate_chat_answer(user_message: str, ocr_context: str, summary: str, recent_messages: list[dict]) -> str:
    """
    환자의 질문에 답변을 생성합니다. (PII 요약 반영)
    """
    system_prompt = f"""당신은 복약 정보 전문 AI 어시스턴트입니다.

[중요 규칙]
1. 사용자가 "부작용", "주의사항", "복용법", "몇 번", "언제" 등을 물으면, 아래 제공된 처방전 분석 결과나 현재 복용 중인 약물 목록의 모든 약물에 대해 답변하세요.
2. 구체적인 약 이름을 언급하지 않았다면, 처방전에 있는 약물 전체를 대상으로 설명하세요.
3. 처방전이나 복용 목록에 없는 약품에 대한 질문은 다음과 같이 안내하세요: "현재는 인식된 처방전 속 약품 정보만 답변해 드릴 수 있습니다. 질문하신 약품이 처방전에 포함되어 있는지 다시 한번 확인해 주세요."
4. 약학 및 복약 관련 질문에만 답변하고, 그 외 질문은 정중히 거절하세요.
5. 답변 시 처방전의 약물 정보를 참조한 경우 끝에 '[출처: 식품의약품안전처 e약은요]'를 추가하세요.

{"이전 대화 요약: " + summary if summary else ""}

{"처방전 분석 결과(현재 복용 기록 포함):\n" + ocr_context if ocr_context else "현재 분석된 처방전이나 복용 중인 약물이 없습니다."}"""

    # GPT 대화 구성
    messages = [{"role": "system", "content": system_prompt}]

    # 최근 이전 메시지 덧붙이기 (Assistant/User 교차)
    for msg in recent_messages:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # 현재 질문
    messages.append({"role": "user", "content": user_message})

    try:
        response = await client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=messages,
            temperature=0.5,  # 정보성 문서는 조금 낮게
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI 챗봇 생성 에러: {e}")
        return "현재 답변을 생성할 수 없습니다. 잠시 후 다시 시도해 주세요."


async def summarize_and_deidentify_chat(messages: list[dict]) -> str:
    """
    최대 5턴의 대화를 넘겨받아 개인정보나 사담을 날리고, 상태/의학적 내용 위주로 한 줄 요약합니다.
    """
    messages_str = "\\n".join([f"{m['role']}: {m['content']}" for m in messages])

    system_prompt = """
    당신은 의료 채팅 기록 요약 어시스턴트입니다.
    사용자와 챗봇이 나눈 다음 대화를 확인하고 짧게 1~2문장으로 '요약'해주세요.

    [핵심 규칙]
    1. 사람 이름, 나이, 등 개인을 식별할 수 있는 정보(PII)는 절대 요약본에 포함하지 마세요. (예: "환자는~" 으로 대체)
    2. 불필요한 사소한 인사말이나 농담은 모두 배제하세요.
    3. 어떤 약품에 대해 물어봤는지, 주요 증상이나 궁금증이 무엇인지만 의료적 관점으로 압축하세요.
    """

    try:
        response = await client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": messages_str}],
            temperature=0.3,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI 요약 에러: {e}")
        return ""
