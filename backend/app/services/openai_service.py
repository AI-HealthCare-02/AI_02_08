import json
from datetime import datetime, timedelta

from openai import AsyncOpenAI

from app.core.config import settings
from app.models.medications import AiReport, MedicationIntakeLog, ReportStatus

# 비동기 OpenAI 클라이언트 초기화
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_medication_report(
    adherence_rate: int, medication_records: list[dict], user_conditions: list[str], period: str = "weekly"
) -> str:
    system_prompt = """
    당신은 환자의 건강과 복약을 관리해주는 다정하고 전문적인 '디지털 약사'입니다.
    환자의 약물 복용 기록, 순응도(%), 그리고 지난 기간 컨디션 메모를 보고
    다음 조건에 맞춰 리포트 코멘트를 작성해 주세요.
    1. 따뜻하고 격려하는 말투를 사용할 것 (예: ~했어요, ~하시는 것이 좋습니다.)
    2. 복약 순응도가 낮을 경우 부드럽게 주의를 주고 개선 팁을 제안할 것.
    3. 전체 분량은 3~4문장 내외의 1문단으로 간결하게 요약할 것.
    """
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
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            temperature=0.7,
            max_tokens=250,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API 에러: {e}")
        return "현재 AI 리포트를 생성할 수 없습니다. 잠시 후 다시 시도해 주세요."


async def process_ai_report_worker(report_id: str, user_id: int, period: str):
    try:
        days = 7 if period == "weekly" else 30
        start_date = datetime.now() - timedelta(days=days)
        intakes = await MedicationIntakeLog.filter(user_id=user_id, scheduled_time__gte=start_date).prefetch_related(
            "medication"
        )

        total_intakes = len(intakes)
        taken_intakes = [i for i in intakes if i.status == "taken"]
        adherence_rate = int((len(taken_intakes) / total_intakes) * 100) if total_intakes > 0 else 0

        user_conditions = [i.opinion for i in intakes if i.opinion and i.opinion.strip()]
        if not user_conditions:
            user_conditions = ["특이사항이 기록되지 않음"]

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
            medication_records.append({"약품명": name, "복용률": f"{rate}%"})
            medication_summary_for_db.append({"name": name, "takenRate": rate})

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

        ai_comment = await generate_medication_report(adherence_rate, medication_records, user_conditions, period)

        await AiReport.filter(report_id=report_id).update(
            adherence_rate=adherence_rate,
            condition_summary=" | ".join(user_conditions)[:500],
            medication_summary=medication_summary_for_db,
            ai_comment=ai_comment,
            status=ReportStatus.COMPLETED,
        )
    except Exception as e:
        print(f"🔥 [Background Task Error] Report Worker 에러: {e}")
        await AiReport.filter(report_id=report_id).update(status=ReportStatus.FAILED)


async def _get_unconfirmed_ocr_context(ocr_id: str) -> list[str]:
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
        # 할루시네이션 방지를 위해 설명(사실 근거) 복구
        line = f"- {name}: {dosage} (복용법: {freq}, {timing})"
        if desc:
            line += f" -> 특징/기능: {desc}"
        lines.append(line)
    lines.append("")
    return lines


async def _get_confirmed_medication_context(user_id: int) -> list[str]:
    from tortoise.expressions import Q

    from app.models.medications import MedicationLog

    logs = await MedicationLog.filter(
        Q(user_id=user_id), Q(end_date__gte=datetime.today().date()) | Q(end_date__isnull=True)
    ).order_by("-created_at")
    if not logs:
        return []

    lines = ["[현재 복용 중인 약물 목록]"]
    for log in logs:
        # 할루시네이션 방지를 위해 주의사항(핵심 안전 정보) 복구
        line = f"- {log.name}: {log.dosage or ''} (복용법: {log.frequency or ''}, {log.timing or ''})"
        if log.caution:
            line += f" -> 주의사항: {log.caution}"
        lines.append(line)
    return lines


async def get_medication_context_for_chatbot(user_id: int, ocr_id: str | None = None) -> str:
    context_lines = []
    if ocr_id:
        context_lines.extend(await _get_unconfirmed_ocr_context(ocr_id))
    context_lines.extend(await _get_confirmed_medication_context(user_id))
    return "\n".join(context_lines).strip() if context_lines else "현재 복용 중이거나 분석된 약물이 없습니다."


async def batch_analyze_unmatched_drugs(unmatched_meds: list[dict]) -> dict[str, str]:
    system_prompt = """당신은 처방전 분석을 돕는 의료 데이터 어시스턴트입니다... (생략)"""
    user_message = f"다음 약품들에 대한 설명을 JSON으로 반환해주세요: {json.dumps(unmatched_meds, ensure_ascii=False)}"
    try:
        response = await client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            temperature=0,
            max_tokens=1000,
        )
        content = response.choices[0].message.content or "{}"
        clean_content = content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean_content)
    except Exception as e:
        print(f"GPT Batch Fallback 에러: {e}")
        return {
            med["name"]: "서비스 지연으로 약품 정보를 불러오지 못했습니다." for med in unmatched_meds if "name" in med
        }


async def generate_chat_answer(user_message: str, ocr_context: str, summary: str, recent_messages: list[dict]) -> str:
    """
    환자의 질문에 답변을 생성합니다. (할루시네이션 방지 강화)
    """
    system_prompt = f"""당신은 복약 정보 전문 AI 어시스턴트입니다.

[핵심 규칙 - 답변 가이드라인]
1. 반드시 아래 제공된 '제공된 약물 컨텍스트'를 최우선 근거로 답변하세요.
2. [정보 보완] 만약 컨텍스트에 특정 약물의 상세 정보(부작용, 주의사항 등)가 누락되어 있다면, AI가 보유한 일반적인 약학 지식을 바탕으로 유익한 정보를 제공하세요.
3. [필수 안전 문구] 컨텍스트 외부의 일반 지식을 제공할 때는 반드시 다음과 같은 취지의 안내를 포함해야 합니다: "일반적으로 이 약물은 ~한 주의사항이 있지만, 환자 개개인의 신체 상태나 기저 질환에 따라 반응이 다를 수 있습니다. 따라서 반드시 전문의나 약사와 상담하여 본인에게 맞는 정확한 지침을 받으시는 것이 가장 안전합니다."
4. [답변 태도] 전문적이면서도 친절한 말투를 유지하고, 답변 끝에는 '[출처: 식품의약품안전처 e약은요 외]'를 추가하세요.
5. [범위] 복약 및 약학 관련 질문 외의 사적인 대화나 타 분야 질문은 정중히 거절하세요.

[이전 대화 요약]
{summary if summary else "없음"}

[제공된 약물 컨텍스트]
{ocr_context if ocr_context else "현재 분석된 처방전이나 복용 중인 약물이 없습니다."}
"""
    messages = [{"role": "system", "content": system_prompt}]
    for msg in recent_messages:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = await client.chat.completions.create(
                model=settings.openai_chat_model,
                messages=messages,
                temperature=0.3,  # 답변의 정합성을 위해 온도를 낮춤
                max_tokens=600,
                timeout=15,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ OpenAI retry {attempt + 1}/{max_retries}: {e}")
                continue
            raise e


async def summarize_and_deidentify_chat(messages: list[dict]) -> str:
    messages_str = "\\n".join([f"{m['role']}: {m['content']}" for m in messages])
    system_prompt = """당신은 의료 채팅 기록 요약 어시스턴트입니다.
    1. 환자의 개인정보(이름, 나이 등)는 절대 포함하지 마세요.
    2. 어떤 약품에 대해 어떤 질문을 했는지 의학적인 관점에서 간략히 요약하세요.
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
