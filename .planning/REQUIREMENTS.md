# Requirements: AI Medication Management & Chatbot

**Defined:** 2026-04-16
**Core Value:** 정확한 약품 정보 추출과 맥락 유지형 챗봇(약속이 상담소)을 통한 맞춤 복약 가이드 제공

## v1 Requirements

### OCR (처방전 분석)

- [ ] **OCR-01 (약품 정보 매칭)**: 시딩 스크립트 연결(처방전 + 클로바ocr + seed + gpt). OCR 추출 텍스트를 기반으로 약품명을 식별하고 내부 DB(DrugInfo)와 매칭한다. *(현재 내부적으로 거의 완료됨)*
- [ ] **OCR-02 (데이터 조회)**: 매칭된 약품의 기본 정보를 DB에서 시스템 내부로 원활하게 조회 및 반환한다.
- [ ] **OCR-03 (AI 보완)**: DB에 없는 정보 또는 추가 설명이 필요한 경우 GPT 스크립트를 사용하여 보완 처리한다.
- [ ] **OCR-04 (실패 처리)**: 분석 실패 시, 케이스별로 나눠진 상태 메시지를 반환한다 (예: "ocr 실패: ...", "gpt 연동 실패: ...").

### Chatbot (약속이 상담소)

- [ ] **CHAT-01 (대화 세션 및 맥락 관리)**: 사용자가 챗봇을 열면 세션을 생성하고, 어떤 맥락(처방전/리포트/복약기록 화면)에서 대화가 시작되었는지 연결하여 저장한다.
- [ ] **CHAT-02 (대화 삭제)**: 사용자가 대화 기록을 삭제할 시, 소프트 딜리트(Soft Delete) 방식으로 처리한다.
- [ ] **CHAT-03 (질문 빛 답변 연동)**: 챗봇 내 답변은 앞선 OCR 분석 결과와 연결되어 구체적으로 도출되어야 한다.
- [ ] **CHAT-04 (FAQ 및 비용 절감)**: 제공되는 예시 질문들 중 답이 완전히 정해져 있는 건에 대해서는 AI 호출 없이 바로 하드코딩된 답변을 반환하여 과금 비용을 절약한다. *(마지막에 여유 시 진행)*

## Out of Scope

| Feature | Reason |
|---------|--------|
| 음성 인식 기반 채팅봇 지원 | V1 스코프 밖, 텍스트 UI/UX에 집중. |
| 자체 거대언어모델 호스팅 | 현재 예산과 개발 여력으로는 외부 모델(OpenAI)에 의지하는 것이 효율적. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| OCR-01 | Phase 1 | Complete |
| OCR-02 | Phase 1 | Pending |
| OCR-03 | Phase 1 | Pending |
| OCR-04 | Phase 1 | Pending |
| CHAT-01 | Phase 2 | Pending |
| CHAT-02 | Phase 2 | Pending |
| CHAT-03 | Phase 2 | Pending |
| CHAT-04 | Phase 2 | Pending |

**Coverage:**
- v1 requirements: 8 total
- Mapped to phases: 8
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-16*
