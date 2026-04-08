import json
from pydantic import BaseModel, Field

from openai import AsyncOpenAI

from app.core.config import settings

# 비동기 OpenAI 클라이언트 초기화
# 오픈AI API 키가 .env 안의 OPENAI_API_KEY 환경변수에 있어야 작동됩니다.
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_medication_report(
    adherence_rate: int,
    medication_records: list[dict],
    user_conditions: list[str],
    period: str = "weekly"
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
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7, # 0.7 정도로 약간의 다정함/창의성 부여
            max_tokens=250
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API 에러: {e}")
        return "현재 AI 리포트를 생성할 수 없습니다. 잠시 후 다시 시도해 주세요."


async def get_medication_context_for_chatbot(user_id: int) -> str:
    """
    [타 팀원 지원용 브릿지 함수]
    챗봇 파트를 담당하는 팀원이 환자의 '현재 복약 정보'를 GPT 프롬프트에 통째로
    주입할 수 있도록, DB 쿼리를 거쳐 깔끔한 텍스트 덩어리로 반환합니다.
    (현재는 테스트를 위해 더미 포맷을 유지합니다)
    """
    # 실제로는 MedicationLog 에서 user_id 기준으로 필터링하여 가져옵니다.
    # mock_logs = await MedicationLog.filter(user_id=user_id, end_date__gte=datetime.today())

    mock_context = """
    - 복용 중인 약: 타이레놀 (1일 3회, 식후 30분)
    - 주의사항: 위장 장애 우려 (자체 DB 기반 경고)
    - 최근 복약률: 80%
    """
    return mock_context


class ParsedMedication(BaseModel):
    name: str = Field(..., description="약품명 (예: 타이레놀500mg, 소화제 등)")
    dosage: str = Field(..., description="1회 투여량 (예: 1정, 1포, 2캡슐 등)")
    frequency: str = Field(..., description="1일 투여 횟수 (예: 1일 3회, 1일 2회)")
    timing: str = Field(..., description="복용 시기 (예: 식후 30분, 취침 전)")

class OcrMedicationList(BaseModel):
    medications: list[ParsedMedication]

async def parse_ocr_text_to_medications(extracted_texts: list[str]) -> list[dict]:
    """
    Clova OCR에서 추출한 텍스트 리스트를 기반으로,
    OpenAI Structured Outputs를 사용하여 약물 정보를 JSON(딕셔너리 리스트)으로 파싱합니다.
    """
    if not extracted_texts:
        return []

    system_prompt = """
    당신은 처방전 및 약봉지 텍스트에서 약물 정보를 전문적으로 추출하는 의료 AI입니다.
    사용자가 OCR로 추출한 텍스트 조각(목록)을 제공하면, 각 약물별로 '약품명', '투여량', '투여횟수', '복용시기'를 정확히 매핑하여 반환하세요.
    최대한 제공된 텍스트 안에서 정보를 추출하되, 명확히 없는 값은 빈 문자열로 두세요.
    """
    
    user_message = f"""
    아래는 OCR로 추출된 텍스트 목록입니다:
    {extracted_texts}
    
    이를 바탕으로 약물 정보를 추출해 주세요.
    """
    try:
        response = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format=OcrMedicationList,
            temperature=0.0,
        )
        parsed = response.choices[0].message.parsed
        return [med.model_dump() for med in parsed.medications] if parsed else []
    except Exception as e:
        print(f"OpenAI 파싱 에러: {e}")
        return []
