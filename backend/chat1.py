import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from openai import OpenAI


@dataclass
class Message:
    id: str
    content: str
    is_user: bool
    timestamp: datetime = field(default_factory=datetime.now)


class PrescriptionChat:
    def __init__(self, analysis_data: dict = None):
        # OpenAI 클라이언트 초기화 (환경변수 OPENAI_API_KEY 필요)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # 초기 메시지 설정
        self.messages: list[Message] = [
            Message("1", "안녕하세요! 분석된 처방전을 바탕으로 궁금한 점을 물어보세요.", False),
        ]
        self.quick_replies = ["복용법 알려줘", "주의사항은?", "같이 먹으면 안 되는 약 있어?"]
        # 분석 결과 데이터 (실제 서비스에선 외부의 OCR/Vision 결과 파라미터가 여기 할당됨)
        self.analysis_data = analysis_data or {
            "medications": [],
            "warnings": "",
            "interactions": "",
        }
        # 보안 및 세션 상태
        self.is_blocked = False
        self.last_warning_time = datetime.now()

    def _check_pii(self, text: str) -> bool:
        email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        phone_pattern = r"\b\d{2,3}[-\.\s]?\d{3,4}[-\.\s]?\d{4}\b"
        ssn_pattern = r"\b\d{6}[-\s]?\d{7}\b"
        return bool(
            re.search(email_pattern, text)
            or re.search(phone_pattern, text)
            or re.search(ssn_pattern, text)
        )

    def _check_illicit_drugs(self, text: str) -> bool:
        # 키워드를 셋(Set)으로 관리하고 영문은 소문자로 통일
        illicit_drugs = {
            "대마", "코카인", "헤로인", "필로폰", "엑스터시",
            "mdma", "lsd", "펜타닐", "ghb", "케타민", "졸피뎀", "프로포폴", "히로뽕", "물뽕", "떨",
        }
        # 입력 텍스트를 소문자로 변환 후 검사
        text_lower = text.lower()
        return any(kw in text_lower for kw in illicit_drugs)

    def _check_moderation(self, text: str) -> bool:
        try:
            response = self.client.moderations.create(input=text)
            return response.results[0].flagged
        except Exception:
            return False

    async def send_chat(self, content: str):
        if not content.strip():
            return None
        if self.is_blocked:
            error_msg = Message(id="err", content="접근이 차단되었습니다. 보건복지콜센터(129) 등 전문 상담 서비스를 이용해주세요.", is_user=False)
            return error_msg
        user_msg = Message(id=f"u_{int(datetime.now().timestamp())}", content=content, is_user=True)
        self.messages.append(user_msg)
        # PII 감지
        if self._check_pii(content):
            ai_msg = Message(id="ai_pii", content="해당 질문에는 답변할 수 없습니다.", is_user=False)
            self.messages.append(ai_msg)
            return ai_msg
        # 불법 약물 감지
        if self._check_illicit_drugs(content):
            self.is_blocked = True
            ai_msg = Message(id="ai_block", content="불법 약물 관련 키워드가 감지되었습니다. 챗봇 접근이 금지되었습니다.", is_user=False)
            self.messages.append(ai_msg)
            return ai_msg
        # Moderation 감지
        if self._check_moderation(content):
            ai_msg = Message(id="ai_mod", content="민감한 키워드가 감지되었습니다. 전문 상담 서비스로 연결을 권장합니다.", is_user=False)
            self.messages.append(ai_msg)
            return ai_msg
        try:
            meds_str = ", ".join(self.analysis_data.get("medications", []))
            warnings = self.analysis_data.get("warnings", "없음")
            interactions = self.analysis_data.get("interactions", "없음")
            system_prompt = f"""당신은 전문 약사 AI입니다.
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
                    *[{"role": "user" if m.is_user else "assistant", "content": m.content} for m in self.messages[-5:]],
                ],
                temperature=0.7,
            )
            ai_content = response.choices[0].message.content
            # 3시간 경고 문구 추가 플로우
            now = datetime.now()
            if now - self.last_warning_time >= timedelta(hours=3):
                ai_content += "\n\n[안내] 건강과 관련된 상담은 의료인과 하는 것이 원칙이며 AI가 제공하는 정보에는 오류가 있을 수 있습니다."
                self.last_warning_time = now
        except Exception as e:
            ai_content = f"OpenAI 연동 오류: {e}"
        ai_msg = Message(id=f"ai_{int(datetime.now().timestamp())}", content=ai_content, is_user=False)
        self.messages.append(ai_msg)
        return ai_msg


if __name__ == "__main__":
    sample_ocr_result = {
        "medications": ["타이레놀", "아목시실린"],
        "warnings": "공복 복용 금지",
        "interactions": "음주 시 간 손상 위험",
    }
    chat = PrescriptionChat(analysis_data=sample_ocr_result)