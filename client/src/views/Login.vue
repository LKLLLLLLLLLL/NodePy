<script lang="ts" setup>
    // 登录逻辑将在这里实现
</script>

<template>
    <div class="login-container">
        <div class="login-card controller-style">
            <div class="login-header">
                <h1 class="login-title">登录 Dify</h1>
                <p class="login-subtitle">欢迎！请登录以开始使用。</p>
            </div>
            
            <div class="social-login">
                <el-button class="social-button github-button">
                    <div class="social-icon github-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                        </svg>
                    </div>
                    <span>使用 GitHub 登录</span>
                </el-button>
                <el-button class="social-button google-button">
                    <div class="social-icon google-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24">
                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                        </svg>
                    </div>
                    <span>使用 Google 登录</span>
                </el-button>
            </div>
            
            <div class="divider">
                <div class="divider-line"></div>
                <span class="divider-text">或</span>
                <div class="divider-line"></div>
            </div>
            
            <el-form class="email-login-form">
                <el-form-item class="email-form-item">
                    <label class="email-label">邮箱</label>
                    <el-input 
                        placeholder="输入邮箱地址" 
                        class="email-input"
                        size="large"
                    ></el-input>
                </el-form-item>
                
                <el-button type="primary" class="send-email-button" size="large">
                    发送验证邮件
                </el-button>
            </el-form>
            
            <div class="agreement-text">
                使用即代表您同意我们的 
                <a href="#" class="agreement-link">使用协议</a> 
                & 
                <a href="#" class="agreement-link">隐私政策</a>
            </div>
        </div>
    </div>
</template>

<style lang="scss" scoped>
    @import '../common/global.scss';
    
    .login-container {
        width: 100%;
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        box-sizing: border-box;
    }
    
    .login-card {
        width: 100%;
        max-width: 400px;
        padding: 40px 32px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        border: none;
        border-radius: 12px;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 32px;
    }
    
    .login-title {
        font-size: 24px;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    
    .login-subtitle {
        color: #718096;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .social-login {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-bottom: 24px;
    }
    
    .social-button {
        width: 100%;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #e2e8f0;
        background: white;
        border-radius: 8px;
        padding: 0 16px;
        font-weight: 500;
        transition: all 0.2s ease;
        
        &:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border-color: #cbd5e0;
        }
        
        span {
            font-size: 14px;
            color: #2d3748;
        }
    }
    
    .github-button:hover {
        background: #f7fafc;
    }
    
    .google-button:hover {
        background: #f7fafc;
    }
    
    .social-icon {
        width: 20px;
        height: 20px;
        margin-right: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .github-icon {
        color: #2d3748;
    }
    
    .divider {
        display: flex;
        align-items: center;
        margin: 24px 0;
    }
    
    .divider-line {
        flex: 1;
        height: 1px;
        background: #e2e8f0;
    }
    
    .divider-text {
        padding: 0 16px;
        color: #718096;
        font-size: 14px;
        background: white;
    }
    
    .email-login-form {
        margin-bottom: 24px;
    }
    
    .email-form-item {
        margin-bottom: 20px;
    }
    
    .email-label {
        display: block;
        margin-bottom: 8px;
        font-size: 14px;
        font-weight: 500;
        color: #2d3748;
    }
    
    .email-input {
        :deep(.el-input__wrapper) {
            border-radius: 8px;
            box-shadow: 0 0 0 1px #e2e8f0;
            transition: all 0.2s ease;
            
            &:hover {
                box-shadow: 0 0 0 1px #cbd5e0;
            }
            
            &.is-focus {
                box-shadow: 0 0 0 1px $stress-color;
            }
        }
        
        :deep(.el-input__inner) {
            &::placeholder {
                color: #a0aec0;
            }
        }
    }
    
    .send-email-button {
        width: 100%;
        height: 48px;
        background: $stress-color;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        font-size: 14px;
        transition: all 0.2s ease;
        
        &:hover {
            background: darken($stress-color, 10%);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba($stress-color, 0.3);
        }
    }
    
    .agreement-text {
        text-align: center;
        color: #718096;
        font-size: 13px;
        line-height: 1.5;
    }
    
    .agreement-link {
        color: $stress-color;
        text-decoration: none;
        
        &:hover {
            text-decoration: underline;
        }
    }
    
    @media (max-width: 480px) {
        .login-card {
            padding: 32px 24px;
        }
        
        .login-title {
            font-size: 22px;
        }
    }
</style>