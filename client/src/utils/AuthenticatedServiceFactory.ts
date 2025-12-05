// services/AuthenticatedServiceFactory.ts
import { 
  createAuthenticatedService, 
  type AuthenticatedService,
  getServiceStatus,
  setAuthToken,
  clearAuthToken,
  initAuthToken
} from './AuthenticatedServiceDecorator';

// 环境判断
const isDev = import.meta.env.DEV;

/**
 * 认证服务工厂
 */
class AuthenticatedServiceFactory {
  private static _authenticatedService: AuthenticatedService;
  
  /**
   * 初始化工厂
   */
  static init() {
    initAuthToken();
    this._authenticatedService = createAuthenticatedService();
  }
  
  /**
   * 获取认证服务实例
   */
  static getService(): AuthenticatedService {
    if (!this._authenticatedService) {
      this.init();
    }
    return this._authenticatedService;
  }
  
  /**
   * 刷新认证服务
   */
  static refreshService(): AuthenticatedService {
    this._authenticatedService = createAuthenticatedService();
    return this._authenticatedService;
  }
  
  /**
   * 设置认证 token
   */
  static setToken(token: string): void {
    setAuthToken(token);
  }
  
  /**
   * 清除认证 token
   */
  static clearToken(): void {
    clearAuthToken();
  }
  
  /**
   * 获取服务状态信息
   */
  static getServiceStatus() {
    const service = this.getService();
    return {
      environment: import.meta.env.MODE,
      ...getServiceStatus(service)
    };
  }
  
  /**
   * 开发工具：手动刷新服务
   */
  static devRefresh() {
    if (isDev) {
      this.refreshService();
    }
  }
  
  /**
   * 检查服务是否包含特定方法
   */
  static hasMethod(methodName: string): boolean {
    const service = this.getService();
    return methodName in service && typeof service[methodName as keyof AuthenticatedService] === 'function';
  }
}

// 在模块加载时自动初始化
AuthenticatedServiceFactory.init();

// 在开发环境中将工厂挂载到window，方便调试
if (isDev) {
  (window as any).AuthenticatedServiceFactory = AuthenticatedServiceFactory;
}

export default AuthenticatedServiceFactory;