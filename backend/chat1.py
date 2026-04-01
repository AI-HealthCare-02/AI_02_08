import os
from dataclasses import dataclass, field
from datetime import datetime

from openai import OpenAI


@dataclass
class Message:
    id: str
    content: str
    is_user: bool
    timestamp: datetime = field(default_factory=datetime.now)


class PrescriptionChat:
    def __init__(self):
        # OpenAI 클라이언트 초기화 (환경변수 OPENAI_API_KEY 필요)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # 초기 메시지 설정
        self.messages: list[Message] = [
            Message("1", "안녕하세요! 분석된 처방전을 바탕으로 궁금한 점을 물어보세요.", False),
        ]
        self.quick_replies = ["복용법 알려줘", "주의사항은?", "같이 먹으면 안 되는 약 있어?"]

        # 분석 결과 데이터 (실제 서비스에선 OCR/Vision 결과가 여기 할당됨)
        self.analysis_data = {
            "medications": ["타이레놀 500mg", "아모잘탄 5/50mg"],
            "warnings": "빈속에 복용 시 위장 장애 가능성",
            "interactions": "음주 시 간 손상 위험",
        }

    def send_message(self, content: str):
        """사용자 메시지를 추가하고 OpenAI 응답을 받아 반환함"""
        if not content.strip():
            return None

        # 1. 유저 메시지 저장 및 추가
        user_msg = Message(id=f"u_{int(datetime.now().timestamp())}", content=content, is_user=True)
        self.messages.append(user_msg)

        # 2. OpenAI API 호출
        try:
            # AI가 처방전 내용을 알 수 있도록 'context'를 주입함
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 속도와 비용면에서 효율적
                messages=[
                    {
                        "role": "system",
                        "content": f"""당신은 전문 약사 AI입니다.
                        다음 처방전 정보를 바탕으로 사용자의 질문에 친절하게 답변하세요.
                        [처방 정보]
                        - 약물: {", ".join(self.analysis_data["medications"])}
                        - 주의사항: {self.analysis_data["warnings"]}
                        - 상호작용: {self.analysis_data["interactions"]}
                        의학적 조언은 신중하게 하되, 반드시 처방전 내용을 우선으로 설명하세요.""",
                    },
                    # 대화 흐름 유지를 위해 최근 메시지 전달 (Memory)
                    *[{"role": "user" if m.is_user else "assistant", "content": m.content} for m in self.messages[-5:]],
                ],
                temperature=0.7,
            )

            ai_content = response.choices[0].message.content

            # 3. AI 메시지 생성 및 저장
            ai_msg = Message(id=f"a_{int(datetime.now().timestamp())}", content=ai_content, is_user=False)
            self.messages.append(ai_msg)
            return ai_msg

        except Exception as e:
            error_msg = Message(id="err", content=f"오류가 발생했습니다: {str(e)}", is_user=False)
            self.messages.append(error_msg)
            return error_msg

    def get_analysis_result(self):
        """UI에 표시될 분석 요약 데이터 반환"""
        return self.analysis_data


# --- 실행 테스트 ---
if __name__ == "__main__":
    chat = PrescriptionChat()

    # 질문 전송 테스트
    question = "타이레놀은 언제 먹는 게 좋아?"
    print(f"User: {question}")

    response = chat.send_message(question)
    print(f"AI: {response.content}")
