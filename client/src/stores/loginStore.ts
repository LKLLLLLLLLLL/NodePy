import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
    login as authLogin, 
    logout as authLogout, 
    signup as authSignup,
    isLoggedIn, 
    getCurrentToken
} from '../utils/AuthHelper'
import type { LoginRequest } from '@/utils/api' 
import type { SignupRequest } from '@/utils/api' 
import type { TokenResponse } from '@/utils/api'
import { ApiError } from '@/utils/api'
import notify from "@/components/Notification/notify"

export const useLoginStore = defineStore('login', () => {
    // 状态 - 直接使用 authHelper 中的函数
    const loggedIn = ref<boolean>(isLoggedIn())
    const token = ref<string | null>(getCurrentToken())

    // 计算属性
    const isAuthenticated = computed(() => loggedIn.value)
    const currentToken = computed(() => token.value)

    // 检查认证状态
    const checkAuthStatus = (): boolean => {
        const newStatus = isLoggedIn()
        const newToken = getCurrentToken()
        
        loggedIn.value = newStatus
        token.value = newToken
        
        return newStatus
    }

    // 登录
    const login = async (credentials: LoginRequest): Promise<TokenResponse> => {
        try {
            const response = await authLogin(credentials)
            checkAuthStatus() // 更新状态
            return response
        } catch (error) {
            // 检查是否是网络错误
            if (error instanceof TypeError && error.message && 
                (error.message.includes('Network Error') || error.message.includes('Failed to fetch'))) {
                notify({
                    message: '无法连接到服务器，请检查网络连接',
                    type: 'error'
                });
            } else if (error instanceof ApiError) {
                // 处理ApiError
                switch(error.status) {
                    case 401:
                        notify({
                            message: '用户名或密码错误',
                            type: 'error'
                        });
                        break;
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    case 500:
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
                        break;
                    default:
                        notify({
                            message: `登录失败 (${error.status}): ${error.statusText || '未知错误'}`,
                            type: 'error'
                        });
                        break;
                }
            } else if (error instanceof Error) {
                // 其他错误
                notify({
                    message: '登录失败: ' + error.message,
                    type: 'error'
                });
            } else {
                // 未知错误
                notify({
                    message: '登录过程中发生未知错误，请稍后重试',
                    type: 'error'
                });
            }
            throw error;
        }
    }

    // 注册
    const signup = async (userData: SignupRequest): Promise<TokenResponse> => {
        try {
            const response = await authSignup(userData)
            checkAuthStatus() // 更新状态
            return response
        } catch (error) {
            // 检查是否是网络错误
            if (error instanceof TypeError && error.message && 
                (error.message.includes('Network Error') || error.message.includes('Failed to fetch'))) {
                notify({
                    message: '无法连接到服务器，请检查网络连接',
                    type: 'error'
                });
            } else if (error instanceof ApiError) {
                // 处理ApiError
                switch(error.status) {
                    case 400:
                        notify({
                            message: '用户名或邮箱已被注册',
                            type: 'error'
                        });
                        break;
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    case 500:
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
                        break;
                    default:
                        notify({
                            message: `注册失败 (${error.status}): ${error.statusText || '未知错误'}`,
                            type: 'error'
                        });
                        break;
                }
            } else if (error instanceof Error) {
                // 其他错误
                notify({
                    message: '注册失败: ' + error.message,
                    type: 'error'
                });
            } else {
                // 未知错误
                notify({
                    message: '注册过程中发生未知错误，请稍后重试',
                    type: 'error'
                });
            }
            throw error;
        }
    }

    // 退出登录
    const logout = async (): Promise<void> => {
        try {
            await authLogout()
            checkAuthStatus() // 更新状态
        } catch (error) {
            // 检查是否是网络错误
            if (error instanceof TypeError && error.message && 
                (error.message.includes('Network Error') || error.message.includes('Failed to fetch'))) {
                notify({
                    message: '无法连接到服务器，您可能仍处于登录状态',
                    type: 'error'
                });
            } else if (error instanceof ApiError) {
                // 处理ApiError
                switch(error.status) {
                    case 401:
                        // 令牌已过期或无效，但仍清除本地状态
                        checkAuthStatus();
                        notify({
                            message: '会话已过期',
                            type: 'warning'
                        });
                        return;
                    case 500:
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
                        break;
                    default:
                        notify({
                            message: `登出失败 (${error.status}): ${error.statusText || '未知错误'}`,
                            type: 'error'
                        });
                        break;
                }
            } else if (error instanceof Error) {
                // 其他错误
                notify({
                    message: '登出失败: ' + error.message,
                    type: 'error'
                });
            } else {
                // 未知错误
                notify({
                    message: '登出过程中发生未知错误，请手动清除浏览器缓存',
                    type: 'error'
                });
            }
            throw error;
        }
    }

    return {
        // 状态
        loggedIn,
        token,
        
        // 计算属性
        isAuthenticated,
        currentToken,
        
        // 方法
        checkAuthStatus,
        login,
        signup,
        logout
    }
})