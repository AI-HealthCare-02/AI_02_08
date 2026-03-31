import apiClient from "./apiClient";

export const authApi = {
  login: (data: { email: string; password: string }) =>
    apiClient.post("/v1/auth/login", data),

  signup: (data: { email: string; password: string; nickname: string }) =>
    apiClient.post("/v1/auth/signup", data),

  refresh: (refreshToken: string) =>
    apiClient.post("/v1/auth/token/refresh", { refresh_token: refreshToken }),
};
