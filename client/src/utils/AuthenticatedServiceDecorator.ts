// services/AuthenticatedServiceDecorator.ts
import { CancelablePromise } from './api/core/CancelablePromise';
import { OpenAPI } from './api/core/OpenAPI';
import { DefaultService } from './api/services/DefaultService';

// 环境判断
const isDev = import.meta.env.DEV;

/**
 * 认证错误类
 */
export class AuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthError';
  }
}

// 定义排除的方法类型
type ExcludedMethods = 
  | 'refreshAccessTokenApiAuthRefreshPost'
  | 'loginApiAuthLoginPost'
  | 'signupApiAuthSignupPost'
  | 'logoutApiAuthLogoutPost'
  | 'spaFallbackFullPathGet';

// 使用条件类型排除特定方法
type DefaultServiceMethodNames = {
  [K in keyof typeof DefaultService]: 
    K extends ExcludedMethods ? never :
    (typeof DefaultService)[K] extends (...args: any[]) => CancelablePromise<any> ? K : never
}[keyof typeof DefaultService];

/**
 * 认证服务类型：包含 DefaultService 的所有需要认证的方法
 */
export type AuthenticatedService = {
  [K in DefaultServiceMethodNames]: (typeof DefaultService)[K];
};

/**
 * 安全地获取 token 字符串
 */
const getTokenString = (token: any): string | null => {
  return typeof token === 'string' ? token : null;
};

/**
 * 获取当前 token（优先从内存获取，其次从 localStorage）
 */
const getCurrentToken = (): string | undefined => {
  return getTokenString(OpenAPI.TOKEN) || localStorage.getItem('access_token') || undefined;
};

/**
 * 保存 token 到内存和本地存储
 */
export const setAuthToken = (token: string): void => {
  OpenAPI.TOKEN = token;
  localStorage.setItem('access_token', token);
  isDev && console.log('✅ Token 已保存');
};

/**
 * 清除 token
 */
export const clearAuthToken = (): void => {
  OpenAPI.TOKEN = undefined;
  localStorage.removeItem('access_token');
};

/**
 * 初始化 token（应用启动时调用）
 */
export const initAuthToken = (): void => {
  const savedToken = localStorage.getItem('access_token');
  if (savedToken) {
    OpenAPI.TOKEN = savedToken;
  }
};

/**
 * 为单个API方法添加认证功能的装饰器
 */
export function withAuthMethod<T extends any[], R>(
  apiMethod: (...args: T) => CancelablePromise<R>
): (...args: T) => CancelablePromise<R> {
  
  return (...args: T): CancelablePromise<R> => {
    
    const executeWithAuth = async (retryCount = 0): Promise<R> => {
      try {
        // 确保请求前有最新的 token
        const currentToken = getCurrentToken();
        if (currentToken && getTokenString(OpenAPI.TOKEN) !== currentToken) {
          OpenAPI.TOKEN = currentToken;
        }
        
        const result = await apiMethod(...args);
        return result;
        
      } catch (error: any) {
        console.error(`❌ API 请求失败 (${apiMethod.name}):`, error);
        
        const isAuthError = error.status === 401;
        
        if (isAuthError && retryCount < 1) {
          try {
            const tokenResponse = await DefaultService.refreshAccessTokenApiAuthRefreshPost();
            
            if (tokenResponse.access_token) {
              setAuthToken(tokenResponse.access_token);
              console.log('✅ Token刷新成功，重试原请求...');
              return await executeWithAuth(retryCount + 1);
            }
          } catch (refreshError) {
            console.error('❌ Token刷新失败:', refreshError);
            clearAuthToken();
            throw new AuthError(`Token刷新失败: ${refreshError}`);
          }
        }
        throw error;
      }
    };

    return new CancelablePromise<R>((resolve, reject) => {
      executeWithAuth()
        .then(resolve)
        .catch(reject);
    });
  };
}

/**
 * 获取类的所有静态方法名
 */
const getStaticMethodNames = (cls: any): string[] => {
  return Object.getOwnPropertyNames(cls)
    .filter(prop => 
      prop !== 'constructor' && 
      prop !== 'name' && 
      prop !== 'length' && 
      prop !== 'prototype' &&
      typeof cls[prop] === 'function'
    );
};

/**
 * 为整个服务添加认证功能
 */
export function createAuthenticatedService(): AuthenticatedService {
  // 初始化 token
  initAuthToken();
  
  const authenticatedService = {} as AuthenticatedService;
  
  // 不需要添加认证的方法列表
  const excludedMethods: ExcludedMethods[] = [
    'refreshAccessTokenApiAuthRefreshPost',
    'loginApiAuthLoginPost', 
    'signupApiAuthSignupPost',
    'logoutApiAuthLogoutPost',
    'spaFallbackFullPathGet'
  ];
  
  // 获取并过滤方法
  const methodNames = getStaticMethodNames(DefaultService)
    .filter(methodName => !excludedMethods.includes(methodName as ExcludedMethods));
  
  // 包装方法
  methodNames.forEach(methodName => {
    try {
      (authenticatedService as any)[methodName] = withAuthMethod(
        (DefaultService as any)[methodName]
      );
    } catch (error) {
      console.error(`❌ 为方法 ${methodName} 添加认证功能失败:`, error);
    }
  });
  
  return authenticatedService;
}

/**
 * 开发工具：检查服务状态
 */
export function getServiceStatus(service: AuthenticatedService) {
  const hasToken = !!getCurrentToken();
  return {
    serviceAvailable: !!service,
    methodCount: Object.keys(service || {}).length,
    hasToken,
    tokenSource: hasToken ? (getTokenString(OpenAPI.TOKEN) ? 'memory' : 'localStorage') : 'none',
    methods: Object.keys(service || {}).filter(key => typeof service[key] === 'function')
  };
}