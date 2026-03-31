export interface User {
  id: number;
  email: string;
  nickname: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}
