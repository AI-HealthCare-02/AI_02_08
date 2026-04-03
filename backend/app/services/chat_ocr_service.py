import json
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta

from openai import OpenAI


@dataclass
class Message:
    id: str
    content: str
    is_user: bool
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M"))


class ChatOcrService:
    def __init__(self):
        # 1. 채팅 초기 상태 간소화
        self.messages: list[Message] = [
            Message("1", "안녕하세요! 복약 관련 궁금한 점을 물어보세요.", False)
        ]
        # 빠른 답장 옵션
        self.quick_replies = ["복약 방법이 있나요?", "주의사항 알려줘", "같이 먹으면 안 되는 약 있어?"]

        # OpenAI 클라이언트 (chat1.py 기능)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "dummy"))
        self.medicine_db = []

        # 2. 임시 DB 파일로 userMedicationData.json 활용 (chat2.py 대체)
        self.medication_data = self._load_medication_data()
        self.analysis_data = {}

        # 보안 및 세션 상태
        self.is_blocked = False
        self.last_warning_time = datetime.now()

    def reset_chat(self):
        self.messages = [
            Message("1", "안녕하세요! 복약 관련 궁금한 점을 물어보세요.", False)
        ]
        self.is_blocked = False
        self.last_warning_time = datetime.now()
        return {"status": "success", "message": "대화가 초기화되었습니다."}

    def _check_pii(self, text: str) -> bool:
        # 이메일, 전화번호, 주민등록번호 정규식
        email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        phone_pattern = r"\b\d{2,3}[-\.\s]?\d{3,4}[-\.\s]?\d{4}\b"
        ssn_pattern = r"\b\d{6}[-\s]?\d{7}\b"

        if (
            re.search(email_pattern, text)
            or re.search(phone_pattern, text)
            or re.search(ssn_pattern, text)
        ):
            return True
        return False

    def _check_illicit_drugs(self, text: str) -> bool:
        illicit_drugs = [
            "대마", "코카인", "헤로인", "필로폰", "엑스터시",
            "mdma", "lsd", "펜타닐", "ghb", "케타민", "졸피뎀",
            "프로포폴", "히로뽕", "물뽕", "떨",
        ]
        for kw in illicit_drugs:
            if kw in text:
                return True
        return False

    def _check_moderation(self, text: str) -> bool:
        try:
            response = self.client.moderations.create(input=text)
            return response.results[0].flagged
        except Exception:
            return False

    def _load_medication_data(self):
        """userMedicationData.json 파일을 로드"""
        try:
            # app/services/chat_ocr_service.py 기준, backend 루트에 있는 json 파일 접근
            file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "userMedicationData.json",
            )
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"JSON 로드 오류: {e}")
            return []

    async def process_ocr(self, image_bytes: bytes) -> dict:
        """
        이미지 분석 후 결과 반환
        - 'e 약은요'를 불러오지 못할 경우에 대비하여 userMedicationData.json 을
          활용하여 분석 결과 데이터를 냄
        """
        try:
            # 여기서 e 약은요 API 연동 로직을 시도 (현재 미구현/실패 상황을 가정)
            raise Exception("e 약은요 API 연결 실패 혹은 미구현")
        except Exception as e:
            print(e)
            # fallback: userMedicationData.json 전체 데이터를 OCR 인식 결과 포맷으로 변환
            if self.medication_data:
                # 전체 약 정보를 분석 포맷에 맞춰 구조화 (무작위 추출 아님)
                medications_detail = []
                for med in self.medication_data:
                    medications_detail.append({
                        "name": med.get("name", ""),
                        "category": med.get("category", ""),
                        "dosage": med.get("dosage", "미정"),
                        "schedule": med.get("schedule", "미정"),
                        "caution": med.get("caution", ""),
                        "description": med.get("description", "").strip(),
                    })
                med_names = [med["name"] for med in medications_detail]
                warnings = " / ".join(
                    [med["caution"] for med in medications_detail if med["caution"]]
                )
                interactions = "userMedicationData 기반 전체 약물 분석 결과"
            else:
                # 데이터 없음 → 사용자 직접 입력 요청
                return {
                    "analysis_id": str(uuid.uuid4())[:8],
                    "medications": [],
                    "medications_detail": [],
                    "warnings": "",
                    "interactions": "",
                    "status": "manual_input_required",
                    "message": "약물 데이터를 인식하지 못했습니다. 약물 정보를 직접 입력해 주세요.",
                }

        self.analysis_data = {
            "medications": med_names,
            "medications_detail": medications_detail,
            "warnings": warnings,
            "interactions": interactions,
        }
        return {
            "analysis_id": str(uuid.uuid4())[:8],
            "medications": med_names,
            "medications_detail": medications_detail,
            "warnings": warnings,
            "interactions": interactions,
            "status": "success",
        }

    async def confirm_prescription(self, medication_list: list) -> dict:
        added_count = 0
        for med in medication_list:
            new_entry = {
                "id": str(uuid.uuid4())[:8],
                "name": med.name,
                "category": "처방약(분석됨)",
                "englishName": "N/A",
                "description": f"{datetime.now().strftime('%Y-%m-%d')} OCR 분석 등록",
                "dosage": med.dosage,
                "frequency": med.frequency,
            }
            self.medicine_db.append(new_entry)
            added_count += 1

        return {
            "status": "success",
            "message": f"{added_count}개의 약물이 복약 목록에 추가되었습니다.",
            "current_db_size": len(self.medicine_db),
        }

    async def send_chat(self, content: str) -> dict:
        if not content.strip():
            return {"error": "내용이 없습니다."}

        if self.is_blocked:
            return {
                "error": "접근이 차단되었습니다. 보건복지콜센터(129) 등 전문 상담 서비스를 이용해주세요."
            }

        # 1. 유저 메시지 생성 및 저장
        user_msg = Message(id=str(uuid.uuid4())[:4], content=content, is_user=True)
        self.messages.append(user_msg)

        # PII 패턴 감지
        if self._check_pii(content):
            ai_content = "해당 질문에는 답변할 수 없습니다."
            ai_msg = Message(id=str(uuid.uuid4())[:4], content=ai_content, is_user=False)
            self.messages.append(ai_msg)
            return {"user": asdict(user_msg), "ai": asdict(ai_msg)}

        # 불법 약물 관련 키워드 감지
        if self._check_illicit_drugs(content):
            self.is_blocked = True
            ai_content = (
                "불법 약물 관련 키워드가 감지되었습니다. 챗봇 접근이 금지되었습니다. "
                "구체적이고 전문적인 상담을 원하신다면 보건복지콜센터(129)로 연락해 주세요."
            )
            ai_msg = Message(id=str(uuid.uuid4())[:4], content=ai_content, is_user=False)
            self.messages.append(ai_msg)
            return {"user": asdict(user_msg), "ai": asdict(ai_msg)}

        # OpenAI Moderation 검사
        if self._check_moderation(content):
            ai_content = "민감한 키워드가 감지되었습니다. 전문 상담 서비스(보건복지상담센터 129 등)로 연결을 권장합니다."
            ai_msg = Message(id=str(uuid.uuid4())[:4], content=ai_content, is_user=False)
            self.messages.append(ai_msg)
            return {"user": asdict(user_msg), "ai": asdict(ai_msg)}

        # 2. normal OpenAI 프로세스
        try:
            meds_str = ", ".join(self.analysis_data.get("medications", []))
            warnings = self.analysis_data.get("warnings", "없음")
            interactions = self.analysis_data.get("interactions", "없음")

            system_prompt = f"""당신은 전문 약사 AI 입니다.
다음 처방전(분석) 정보를 바탕으로 사용자의 질문에 친절하게 답변하세요.
[처방 정보]
- 약물: {meds_str}
- 주의사항: {warnings}
- 상호작용: {interactions}
의학적 조언은 신중하게 하되, 처방전 내용을 우선으로 설명하세요."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *[
                        {"role": "user" if m.is_user else "assistant", "content": m.content}
                        for m in self.messages[-5:]
                    ],
                ],
                temperature=0.7,
            )
            ai_content = response.choices[0].message.content
        except Exception as e:
            # API 키가 없거나 문제 발생시 기본 응답 (chat2.py 의 기능 fallback)
            ai_content = f"'{content}'에 대한 답변입니다. (OpenAI 연동 실패/미설정: {str(e)})"

        # 3시간 경고 문구 추가 플로우
        now = datetime.now()
        if now - self.last_warning_time >= timedelta(hours=3):
            ai_content += "\n\n[안내] 건강과 관련된 상담은 의료인과 하는 것이 원칙이며 AI 가 제공하는 정보에는 오류가 있을 수 있습니다."
            self.last_warning_time = now

        ai_msg = Message(id=str(uuid.uuid4())[:4], content=ai_content, is_user=False)
        self.messages.append(ai_msg)

        return {"user": asdict(user_msg), "ai": asdict(ai_msg)}


chat_ocr_service = ChatOcrService()
