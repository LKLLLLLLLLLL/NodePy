// utils/api/services/authHelper.ts
import { DefaultService } from './DefaultService';
import AuthenticatedServiceFactory from './AuthenticatedServiceFactory';
import type { LoginRequest } from '../models/LoginRequest';
import type { TokenResponse } from '../models/TokenResponse';
import type { SignupRequest } from '../models/SignupRequest';

// 环境判断
const isDev = import.meta.env.DEV;

/**
 * 登录函数
 */
export const login = async (credentials: LoginRequest): Promise<TokenResponse> => {
  try {
    const response = await DefaultService.loginApiAuthLoginPost(credentials);
    
    if (response.access_token) {
      AuthenticatedServiceFactory.setToken(response.access_token);
      isDev && console.log('✅ 登录成功');
    }
    
    return response;
  } catch (error) {
    console.error('❌ 登录失败:', error);
    throw error;
  }
};

/**
 * 注册函数
 */
export const signup = async (userData: SignupRequest): Promise<TokenResponse> => {
  try {
    const response = await DefaultService.signupApiAuthSignupPost(userData);
    
    if (response.access_token) {
      AuthenticatedServiceFactory.setToken(response.access_token);
      isDev && console.log('✅ 注册成功');
    }
    
    return response;
  } catch (error) {
    console.error('❌ 注册失败:', error);
    throw error;
  }
};

/**
 * 登出函数
 */
export const logout = async (): Promise<void> => {
  try {
    await DefaultService.logoutApiAuthLogoutPost();
  } catch (error) {
    console.error('登出 API 调用失败:', error);
  } finally {
    AuthenticatedServiceFactory.clearToken();
    isDev && console.log('✅ 已登出');
  }
};

/**
 * 获取认证服务（用于 API 调用）
 */
export const getAuthService = () => {
  return AuthenticatedServiceFactory.getService();
};

/**
 * 检查是否已登录
 */
export const isLoggedIn = (): boolean => {
  return AuthenticatedServiceFactory.getServiceStatus().hasToken;
};

/**
 * 获取当前 token
 */
export const getCurrentToken = (): string | null => {
  return localStorage.getItem('access_token');
};