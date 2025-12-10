<script lang="ts" setup>
    import { ref, computed } from 'vue';
    import { notify } from '@/components/Notification/notify';
    import { LoginRequest } from '@/utils/api';
    import { useRouter } from 'vue-router';
    // 导入新的认证工具函数
    import { usePageStore } from '@/stores/pageStore';
    import { useLoginStore } from '@/stores/loginStore';

    const router = useRouter();
    const pageStore = usePageStore();
    const loginStore = useLoginStore()

    //el-form config
    const label_width = "80px"
    const label_position = "top"

    //form type
    type State = 'login'|'register';
    type LoginType = 'email'|'username';
    const state = ref<State>('login');
    const loginType = ref<LoginType>('username');

    //default info
    const default_password: string = '';
    const default_username: string = '';
    const default_confirmpassword: string = '';
    const default_email: string = '';
    const default_email_username: string = ''

    const password = ref<string>(default_password);
    const confirm_password = ref<string>(default_confirmpassword);
    const email = ref<string>(default_email);
    const username = ref<string>(default_username);
    const email_username = ref<string>(default_email_username)

    const accountLabel = computed(()=>{
        if(loginType.value=='email')return '邮箱';
        else return '用户名'
    })

    function loginByGoogle(){
        // 谷歌登录逻辑
    }

    function loginByGitHub(){
        // GitHub登录逻辑
    }

    // 密码限制函数
    function restrictPassword(): boolean {
        const pwd = password.value;
        // // 检查密码长度（至少8位）
        // if (pwd.length < 8) {
        //     return false;
        // }
        // // 检查是否包含数字
        // if (!/\d/.test(pwd)) {
        //     return false;
        // }
        // // 检查是否包含字母
        // if (!/[a-zA-Z]/.test(pwd)) {
        //     return false;
        // }
        // // 检查是否包含特殊字符
        // if (!/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) {
        //     return false;
        // }
        return true;
    }

    // 用户名限制函数
    function restrictUsername(): boolean {
        const usr = username.value;
        // // 检查用户名长度（3-20个字符）
        // if (usr.length < 3 || usr.length > 20) {
        //     return false;
        // }
        // // 检查是否只包含字母、数字、下划线
        // if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(usr)) {
        //     return false;
        // }
        // // 不能以数字开头
        // if (/^\d/.test(usr)) {
        //     return false;
        // }
        return true;
    }

    // 测试所有信息是否符合规定
    function testAllInfo(): boolean {
        // 检查用户名
        if (!restrictUsername()) {
            if (username.value.length < 3 || username.value.length > 20) {
                notify({ message: '用户名长度应在3-20个字符之间', type: 'error' });
            } else if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(username.value)) {
                notify({ message: '用户名只能包含字母、数字、下划线和中文', type: 'error' });
            } else if (/^\d/.test(username.value)) {
                notify({ message: '用户名不能以数字开头', type: 'error' });
            } else {
                notify({ message: '用户名不符合要求', type: 'error' });
            }
            return false;
        }

        // 检查密码
        if (!restrictPassword()) {
            if (password.value.length < 8) {
                notify({ message: '密码长度至少8位', type: 'error' });
            } else if (!/\d/.test(password.value)) {
                notify({ message: '密码必须包含数字', type: 'error' });
            } else if (!/[a-zA-Z]/.test(password.value)) {
                notify({ message: '密码必须包含字母', type: 'error' });
            } else if (!/[!@#$%^&*(),.?":{}|<>]/.test(password.value)) {
                notify({ message: '密码必须包含特殊字符', type: 'error' });
            } else {
                notify({ message: '密码不符合要求', type: 'error' });
            }
            return false;
        }

        // 检查确认密码
        if (password.value !== confirm_password.value) {
            notify({ message: '两次输入的密码不一致', type: 'error' });
            return false;
        }

        // 检查邮箱（如果是邮箱登录或注册）
        if ((state.value === 'login' && loginType.value === 'email') || state.value === 'register') {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email.value)) {
                notify({ message: '请输入有效的邮箱地址', type: 'error' });
                return false;
            }
        }

        return true;
    }

    function comparePassword(){
        if(password.value==confirm_password.value){
            return true
        }
        else return false
    }

    async function handleLogin(){
        try {
            if(loginType.value === LoginRequest.type.EMAIL){
                await loginStore.login({
                    type: LoginRequest.type.EMAIL,
                    identifier: email.value,
                    password: password.value
                });
            }
            else if(loginType.value === LoginRequest.type.USERNAME){
                await loginStore.login({
                    type: LoginRequest.type.USERNAME,
                    identifier: username.value,
                    password: password.value
                });
            }
            notify({ message: '登录成功', type: 'success' });
            pageStore.jumpToPage();
        } catch (error: any) {
            if (error.status === 401) {
                notify({ message:'用户名、邮箱或密码错误', type: 'error' });
            } else {
                notify({ message: '登录失败，请重试', type: 'error' });
            }
        }
    }

    async function handleRegister(){
        // 先验证所有信息
        if (!testAllInfo()) {
            return;
        }

        try {
            // 使用新的注册函数
            await loginStore.signup({
                username: username.value,
                email: email.value,
                password: password.value
            });
            notify({ message: '注册成功，已自动登录', type: 'success' });
            pageStore.jumpToPage();
        } catch (error: any) {
            if (error.status === 400) {
                notify({ message: '用户名或邮箱已被注册', type: 'error' });
            } else {
                notify({ message: '注册失败，请重试', type: 'error' });
            }
        }
    }

    function handleSubmit(){
        if(state.value=='login'){
            handleLogin()
        }
        else handleRegister()
    }

    function handleReset(){
        password.value = default_password;
        confirm_password.value = default_confirmpassword;
        email.value = default_email;
        username.value = default_username;
    }

    function handleSwitch(){
        if(state.value=='login')state.value='register';
        else state.value='login';
    }

</script>

<template>
    <div class="login-background">
        <div class="login-container" v-if="state=='login'">
            <div class="login-head">
                <div class="icon-container">
                    <img src="../../public/logo-trans.png" alt="logo">
                </div>
                <div class="title-container">
                    <h2 class="nodepy-title">
                        登录
                        <!-- <span class="brand-highlight">NodePy</span> -->
                    </h2>
                </div>
            </div>
            <div class="login-form">
                <el-form>
                    <el-form-item class="login-type-selector">
                        <el-radio-group v-model="loginType">
                            <el-radio-button value="email">邮箱</el-radio-button>
                            <el-radio-button value="username">用户名</el-radio-button>
                        </el-radio-group>
                    </el-form-item>
                </el-form>
                <el-form
                    :label-width="label_width"
                    :label-position="label_position">
                    <el-form-item class="login-account" :label="accountLabel">
                        <el-input
                            placeholder="请输入邮箱"
                            v-if="loginType=='email'"
                            v-model="email"
                        >
                        </el-input>
                        <el-input
                            placeholder="请输入用户名"
                            v-else
                            v-model="username">
                        </el-input>
                    </el-form-item>

                    <el-form-item class="login-password" label="密码">
                        <el-input
                            placeholder="请输入密码"
                            v-model="password"
                            type="password"
                            show-password
                        >
                        </el-input>
                    </el-form-item>
                </el-form>
                <div class="login-bottom-controler">
                    <div class="login-control">
                        <el-button type="primary" @click="handleSubmit" class="confirm-button login">登录</el-button>
                        <!-- <el-button @click="handleReset">重置</el-button> -->
                    </div>
                    <div class="switcher">
                        <el-button type="text" @click="handleSwitch">注册</el-button>
                    </div>
                </div>

                    <!-- 第三方登录按钮 -->
                    <!-- <div class="third-party-login">
                        <div class="divider">
                            Or continue with
                        </div>
                        <div class="oauth-buttons">
                            <el-button class="oauth-btn google-btn" @click="loginByGoogle">
                                <svg class="oauth-icon" viewBox="0 0 24 24" width="20" height="20">
                                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                                </svg>
                                <span>Google</span>
                            </el-button>
                            <el-button class="oauth-btn github-btn" @click="loginByGitHub">
                                <svg class="oauth-icon" viewBox="0 0 24 24" width="20" height="20">
                                    <path fill="currentColor" d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                                </svg>
                                <span>GitHub</span>
                            </el-button>
                        </div>
                    </div> -->
            </div>
        </div>
        <div class="register-container" v-else>
            <div class="register-head">
                <div class="icon-container">
                    <img src="../../public/logo-trans.png" alt="logo">
                </div>
                <div class="title-container">
                    <h2 class="nodepy-title">
                        注册
                        <!-- <span class="brand-highlight">NodePy</span> -->
                    </h2>
                </div>
            </div>
            <div class="register-form">
                <el-form
                    :label-width="label_width"
                    :label-position="label_position">
                    <el-form-item class="register-email" label="邮箱">
                        <el-input
                            placeholder="请输入邮箱"
                            v-model="email"
                        >
                        </el-input>
                    </el-form-item>

                    <el-form-item class="register-username" label="用户名">
                        <el-input
                            placeholder="请输入用户名"
                            v-model="username"
                        >
                        </el-input>
                    </el-form-item>

                    <el-form-item class="register-password" label="密码">
                        <el-input
                            placeholder="请输入密码（至少8位，包含数字、字母和特殊字符）"
                            v-model="password"
                            type="password"
                            show-password
                        >
                        </el-input>
                    </el-form-item>

                    <el-form-item class="register-password-confirm" label="确认密码">
                        <el-input
                            placeholder="请再次输入密码"
                            v-model="confirm_password"
                            type="password"
                            show-password
                        >
                        </el-input>
                    </el-form-item>
                </el-form>
                <div class="register-bottom-controler">
                    <div class="register-control">
                        <el-button type="primary" @click="handleSubmit" class="confirm-button register">创建</el-button>
                        <!-- <el-button @click="handleReset">重置</el-button> -->
                    </div>

                    <div class="switcher">
                        <el-button type="text" @click="handleSwitch">返回</el-button>
                    </div>
                </div>
            </div>
        </div>
    </div>

</template>

<style lang="scss" scoped>
    @use '../common/global.scss' as *;
    .login-background{
        display: flex;
        flex: 1;
        justify-content: center;
        align-items: center;
        background-color: $background-color; /* 使用global.scss中的背景色 */
        min-height: 100vh;
        padding: 20px;
    }
    .login-container, .register-container {
        @include controller-style; /* 使用controller-style混合宏 */
        display: flex;
        flex-direction: column;
        width: 450px;
        background-color: $stress-background-color;
        padding: 30px;
        position: relative;
        overflow: hidden;
    }

    .login-container {
        height: 500px; // 登录界面高度
    }

    .register-container {
        height: 600px; // 注册界面高度
    }

    .login-head, .register-head {
        display: flex;
        flex-direction: column;
        height: 85px;
        position: relative;
        z-index: 1;
    }

    .icon-container {
        width: 130px;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 10px;
        img {
            width: 100%;
            height: 100%;
        }
    }

    .title-container {
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .nodepy-title {
        font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
        font-weight: 600;
        letter-spacing: 1px;
        margin: 0;
        color: #333;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1); /* 修改为中性阴影，避免蓝光 */
        font-size: 24px;
    }

    .brand-highlight {
        font-weight: 700;
        color: $stress-color; /* 使用项目主色 #108efe */
        position: relative;
        display: inline-block;
    }

    .register-form, .login-form {
        margin-top: 20px;
        position: relative;
        z-index: 1;
        flex: 1;
        display: flex;
        flex-direction: column;
    }

    .login-bottom-controler, .register-bottom-controler {
        margin-top: 28px;
        width: 100%;
        display: flex;
        flex-direction: column;
        gap: 15px;
        position: relative;
        z-index: 1;
    }

    .login-control, .register-control {
        width: 100%;
        display: flex;
        justify-content: flex-end;
    }

    .switcher {
        width: 100%;
        display: flex;
        justify-content: flex-end;
    }

    .confirm-button {
        width: 100%;
        height: 45px;
        font-size: 16px;
        font-weight: 500;
        letter-spacing: 1px;
    }

    /* 第三方登录样式 */
    .third-party-login {
        margin: 20px 0 10px;
        display: flex;
        flex-direction: column;
    }

    .divider {
        width: 100%;
        text-align: center;
        height: 30px;
        position: relative;
        color: #999;

        &::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(to right, transparent, #ddd, transparent);
        }

        span {
            background: white;
            padding: 0 15px;
            position: relative;
        }
    }

    .oauth-buttons {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        margin-top: 15px;
    }

    .oauth-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid #eee;
        background: white;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); /* 使用中性阴影，避免蓝光 */

        &:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); /* 使用中性阴影，避免蓝光 */
            border-color: #ddd;
        }

        .oauth-icon {
            width: 20px;
            height: 20px;
        }
    }

    // 响应式设计
    @media (max-width: 500px) {
        .login-container, .register-container {
            width: 95%;
            padding: 20px;
        }

        .login-container {
            height: 450px;
        }

        .register-container {
            height: 550px;
        }
    }
</style>
