import apiClient from './apiClient';

// ========== 타입 정의 ==========
export interface ChatSession {
  session_id: number;
  user_id: number;
  ocr_id: string | null;
  message_count: number;
  created_at: string;
}

export interface ChatMessage {
  message_id: number;
  session_id: number;
  sender: 'user' | 'assistant';
  content: string;
  is_faq: boolean;
  created_at: string;
}

export interface CreateSessionRequest {
  ocr_id?: string | null;
}

export interface SendMessageRequest {
  user_message: string;
}

// ========== API 함수 ==========

/**
 * 새 채팅 세션 생성
 */
export const createChatSession = async (ocrId?: string): Promise<ChatSession> => {
  const response = await apiClient.post('/chat/sessions', {
    ocr_id: ocrId || null,
  });
  return response.data;
};

/**
 * 사용자의 모든 채팅 세션 조회
 */
export const getChatSessions = async (): Promise<ChatSession[]> => {
  const response = await apiClient.get('/chat/sessions');
  return response.data;
};

/**
 * 특정 세션 조회
 */
export const getChatSession = async (sessionId: number): Promise<ChatSession> => {
  const response = await apiClient.get(`/chat/sessions/${sessionId}`);
  return response.data;
};

/**
 * 세션 삭제
 */
export const deleteChatSession = async (sessionId: number): Promise<void> => {
  await apiClient.delete(`/chat/sessions/${sessionId}`);
};

/**
 * 세션의 메시지 내역 조회
 */
export const getChatMessages = async (sessionId: number): Promise<ChatMessage[]> => {
  const response = await apiClient.get(`/chat/sessions/${sessionId}/messages`);
  return response.data;
};

/**
 * 기존 채팅 세션에 ocrId를 연결 (PATCH)
 */
export const updateChatSession = async (
  sessionId: number,
  ocrId: string
): Promise<ChatSession> => {
  const response = await apiClient.patch(`/chat/sessions/${sessionId}`, {
    ocr_id: ocrId,
  });
  return response.data;
};

/**
 * AI 응답 받기 (사용자 메시지 전송 + AI 응답 자동 저장)
 */
export const sendMessageAndGetAIResponse = async (
  sessionId: number,
  userMessage: string
): Promise<ChatMessage> => {
  const response = await apiClient.post(
    `/chat/sessions/${sessionId}/ai-response`,
    { user_message: userMessage }
  );
  return response.data;
};
