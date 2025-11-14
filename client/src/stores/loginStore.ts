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
        const response = await authLogin(credentials)
        checkAuthStatus() // 更新状态
        return response
    }

    // 注册
    const signup = async (userData: SignupRequest): Promise<TokenResponse> => {
        const response = await authSignup(userData)
        checkAuthStatus() // 更新状态
        return response
    }

    // 退出登录
    const logout = async (): Promise<void> => {
        await authLogout()
        checkAuthStatus() // 更新状态
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