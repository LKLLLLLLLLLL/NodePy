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

    // el-form config (removed unused variables)

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
    const password = ref<string>(default_password);
    const confirm_password = ref<string>(default_confirmpassword);
    const email = ref<string>(default_email);
    const username = ref<string>(default_username);

    const accountLabel = computed(()=>{
        if(loginType.value=='email')return '邮箱';
        else return '用户名'
    })

    // 第三方登录逻辑（占位）已移除以简化此文件，若需要请在专用 composable 中实现

    // 定义允许的标点符号
    const allowedPunctuation = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~";

    // 辅助函数：转义正则表达式特殊字符
    function escapeRegExp(string: string): string {
        return string.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&');
    }

    // 密码限制函数
    function restrictPassword(): boolean {
        const pwd = password.value;
        // 检查密码长度（6-20位）
        if (pwd.length < 6 || pwd.length > 20) {
            return false;
        }
        // 检查是否包含中文字符
        if (/[\u4e00-\u9fa5]/.test(pwd)) {
            return false;
        }
        // 构建允许的字符正则表达式（字母、数字和允许的标点符号）
        const escapedPunctuation = escapeRegExp(allowedPunctuation);
        const allowedChars = new RegExp(`^[a-zA-Z0-9${escapedPunctuation}]*$`);
        if (!allowedChars.test(pwd)) {
            return false;
        }
        return true;
    }

    // 用户名限制函数
    function restrictUsername(): boolean {
        const usr = username.value;
        // 检查用户名长度（1-20个字符）
        if (usr.length < 1 || usr.length > 20) {
            return false;
        }
        // 构建允许的字符正则表达式（中文、字母、数字和允许的标点符号）
        const escapedPunctuation = escapeRegExp(allowedPunctuation);
        const allowedChars = new RegExp(`^[\\u4e00-\\u9fa5a-zA-Z0-9${escapedPunctuation}]*$`);
        if (!allowedChars.test(usr)) {
            return false;
        }
        return true;
    }

    // 测试所有信息是否符合规定
    function testAllInfo(): boolean {
        // 检查用户名
        if (!restrictUsername()) {
            if (username.value.length < 1 || username.value.length > 20) {
                notify({ message: '用户名长度应在1-20个字符之间', type: 'error' });
            } else {
                notify({ message: '用户名只能包含中文、字母、数字和标准英文标点符号', type: 'error' });
            }
            return false;
        }

        // 检查密码
        if (!restrictPassword()) {
            if (password.value.length < 6 || password.value.length > 20) {
                notify({ message: '密码长度应在6-20个字符之间', type: 'error' });
            } else if (/[\u4e00-\u9fa5]/.test(password.value)) {
                notify({ message: '密码不能包含中文字符', type: 'error' });
            } else {
                notify({ message: '密码只能包含字母、数字和标准英文标点符号', type: 'error' });
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

    // comparePassword 已内联使用于校验逻辑，移除独立实现以精简代码

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

    // handleReset 与 handleSwitch 被替换为直接操作 state/ref 或在表单控件中处理

    // 返回首页（使用路由导航）
    function goHome(){
        router.push('/');
    }

</script>

<template>
    <div class="login-background">
        <div class="large-area">
            <div class="large-top">
                <div class="large-logo">
                    <img src="../../public/logo-trans.png" alt="logo">
                </div>
                <div class="large-top-right">
                    <button class="global-register-btn" @click="state = state === 'login' ? 'register' : 'login'">{{ state === 'login' ? '注册' : '返回' }}</button>
                </div>
            </div>

            <div class="auth-card" :class="{ 'register-mode': state === 'register' }">
                <div class="auth-card-left">
                    <template v-if="state==='login'">
                        <h1 class="welcome-title">欢迎！请登录以使用 <span class="nodepy-brand">NodePy</span></h1>
                        <!-- <p class="welcome-sub">NodePy是一个安全且高效的平台，帮助你以可视化方式构建与管理数据流程。</p> -->
                        <div class="auth-quote">
                            <p>登录后，你可以浏览示例或立即创建你的第一个流程。</p>
                        </div>
                    </template>
                    <template v-else>
                        <h1 class="welcome-title">欢迎！注册以加入 <span class="nodepy-brand">NodePy</span></h1>
                        <!-- <p class="welcome-sub">注册后可保存项目、共享流程。</p> -->
                        <div class="auth-quote">
                            <p>请填写下列信息来创建你的账号，随后你将获得完整的项目存储与共享功能。</p>
                        </div>
                    </template>
                </div>

                <div class="auth-card-right">
                    <div class="auth-box">
                        <div class="login-container" v-if="state=='login'">
                            <div class="login-head">
                                <h2 class="nodepy-title title-container">登录</h2>
                            </div>
                            <div class="login-form">
                                <div class="login-type-row">
                                    <div class="login-type-capsule" role="tablist" aria-label="登录方式">
                                        <button
                                            type="button"
                                            class="capsule"
                                            :class="{ active: loginType === 'email' }"
                                            @click="loginType = 'email'"
                                            role="tab"
                                            :aria-selected="loginType === 'email' ? 'true' : 'false'"
                                        >邮箱</button>
                                        <button
                                            type="button"
                                            class="capsule"
                                            :class="{ active: loginType === 'username' }"
                                            @click="loginType = 'username'"
                                            role="tab"
                                            :aria-selected="loginType === 'username' ? 'true' : 'false'"
                                        >用户名</button>
                                    </div>
                                </div>

                                <form class="my-form" @submit.prevent="handleSubmit">
                                    <div class="form-item">
                                        <label class="form-label">{{ accountLabel }}</label>
                                        <input v-if="loginType==='email'" class="my-input" placeholder="请输入邮箱" v-model="email" />
                                        <input v-else class="my-input" placeholder="请输入用户名" v-model="username" />
                                    </div>

                                    <div class="form-item">
                                        <label class="form-label">密码</label>
                                        <input class="my-input" placeholder="请输入密码" v-model="password" type="password" />
                                    </div>

                                    <div class="login-bottom-controler">
                                        <div class="login-control">
                                            <button type="submit" class="my-btn my-btn-primary confirm-button">登录</button>
                                        </div>
                                        <!-- 注册由页面顶部全局按钮切换 -->
                                    </div>
                                </form>
                                <!-- <div class="legal-note">使用即代表同意我们的 <a>使用协议</a> &amp; <a>隐私政策</a></div> -->
                            </div>
                        </div>

                        <div class="register-container" v-else>
                            <div class="register-head">
                                <h2 class="nodepy-title title-container">注册</h2>
                            </div>
                            <div class="register-form">
                                <form class="my-form" @submit.prevent="handleSubmit">
                                    <div class="form-item">
                                        <label class="form-label">邮箱</label>
                                        <input class="my-input" placeholder="请输入邮箱" v-model="email" />
                                    </div>
                                    <div class="form-item">
                                        <label class="form-label">用户名</label>
                                        <input class="my-input" placeholder="请输入用户名（1-20位）" v-model="username" />
                                    </div>
                                    <div class="form-item">
                                        <label class="form-label">密码</label>
                                        <input class="my-input" placeholder="请输入密码（6-20位）" v-model="password" type="password" />
                                    </div>
                                    <div class="form-item">
                                        <label class="form-label">确认密码</label>
                                        <input class="my-input" placeholder="请再次输入密码" v-model="confirm_password" type="password" />
                                    </div>
                                    <div class="register-bottom-controler">
                                        <div class="register-control">
                                            <button type="submit" class="my-btn my-btn-primary confirm-button register">创建</button>
                                        </div>
                                    </div>
                                </form>
                                <!-- <div class="legal-note">使用即代表同意我们的 <a>使用协议</a> &amp; <a>隐私政策</a></div> -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="large-footer"><span class="copyright">© 2025 NodePy. All rights reserved.</span></div>
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
    /* reset global login/register container styles so nested cards don't overflow */
    .login-container, .register-container {
        display: flex;
        flex-direction: column;
        width: 100%;
        background-color: transparent;
        padding: 0;
        position: relative;
        overflow: visible;
    }

    /* Large area that holds the whole centered card */
    .large-area {
        width: calc(100% - 80px);
        // max-width: 1400px;
        margin: 40px auto;
        min-height: calc(100vh - 120px);
        background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(250,252,255,0.9));
        border-radius: 14px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.06);
        position: relative;
        padding: 28px;
        display: flex;
        flex-direction: column;
    }

    .large-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }

    .large-logo img {
        width: 160px;
        height: auto;
    }

    .large-top-right {
        width: 120px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
    }

    .global-register-btn {
        background: transparent;
        border: 1px solid transparent;
        color: $stress-color;
        padding: 6px 12px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
    }
    .global-register-btn:hover { background: rgba(16,142,254,0.06); }

    .auth-card {
        margin: 20px auto 0;
        width: 100%;
        max-width: 1000px;
        display: grid;
        grid-template-columns: 1fr minmax(320px, 420px);
        gap: 28px;
        align-items: start;
        flex: 1;
    }

    /* Center login content vertically when not in register mode */
    .auth-card:not(.register-mode) {
        align-items: center;
    }
    .auth-card:not(.register-mode) .auth-card-left {
        justify-content: center; /* vertically center left promo */
    }
    .auth-card:not(.register-mode) .auth-card-right {
        justify-content: center;
        align-items: center;
    }

    /* In register-mode keep the same left-promo / right-form layout as login
       and center content for visual consistency. */
    .auth-card.register-mode {
        grid-template-columns: 1fr minmax(320px, 420px);
        align-items: center;
    }
    .auth-card.register-mode .auth-card-left,
    .auth-card.register-mode .auth-card-right {
        justify-content: center;
        align-items: center;
        display: flex;
    }
    /* keep auth-box margin consistent in register-mode */
    .auth-card.register-mode .auth-box { margin: 24px auto; }

    .auth-card-left {
        padding: 36px 28px;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    /* 在注册模式下，让左侧的说明内容左对齐（注册说明靠左显示） */
    .auth-card.register-mode .auth-card-left {
        align-items: flex-start;
        text-align: left;
        padding-left: 28px;
    }

    /* register intro block inside right auth box */
    .register-intro { margin-bottom: 12px; }
    .register-title { margin: 0 0 6px 0; font-size: 18px; color: #102132; }
    .register-sub { margin: 0; color: #6b7c88; }

    .welcome-title {
        font-size: 26px;
        margin: 0;
        color: #0f2130;
        font-weight: 700;
        line-height: 1.1;
    }

    .welcome-sub {
        margin: 6px 0 0 0;
        color: #556770;
        font-size: 14px;
        max-width: 440px;
    }

    .auth-quote p { color: #6b7c88; margin-top: 14px; font-size: 14px; }

    /* NodePy art brand gradient */
    .nodepy-brand {
        background: $stress-color;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        font-weight: 700;
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        padding: 0 6px;
        border-radius: 6px;
    }

    .auth-card-right {
        display: flex;
        justify-content: center;
        align-items: center;
        width: auto;
    }

    .auth-box {
        width: 100%;
        max-width: 420px;
        padding: 24px;
        box-sizing: border-box;
        margin: 24px auto;
        @include controller-style;
        background: $stress-background-color;
        /* Do not scroll internally; allow page-level scrolling instead */
        overflow: visible;
        max-height: none;
    }

    .legal-note {
        font-size: 12px;
        color: #97a4ad;
        text-align: center;
        margin-top: 12px;
    }

    .legal-note a { color: $stress-color; text-decoration: underline; cursor: pointer; }

    .large-footer {
        text-align: center;
        color: #7b8b94;
        font-size: 13px;
        padding: 18px 0 6px;
    }

    /* 返回首页按钮，固定在大区域左下角；视觉样式与顶部注册按钮一致 */
    .back-home-btn {
        position: absolute;
        left: 24px;
        bottom: 20px;
        z-index: 30;
        padding: 6px 12px;
        border-radius: 8px;
        cursor: pointer;
        transition: transform 0.12s ease, background 0.12s ease;
    }
    // .back-home-btn:hover { transform: translateY(-2px); }

    /* formal copyright text */
    .large-footer .copyright {
        display: block;
        font-size: 13px;
        color: #7b8b94;
    }

    .login-container {
        /* remove fixed height so content can size naturally */
        min-height: auto;
    }

    .register-container {
        min-height: auto;
    }

    .login-head, .register-head {
        display: flex;
        flex-direction: column;
        height: auto; /* let content size naturally to avoid large gaps */
        position: relative;
        z-index: 1;
        padding-bottom: 6px;
    }

    /* .icon-container 已移除（未在模板中使用） */

    .title-container {
        height: auto;
        display: flex;
        align-items: center;
        justify-content: center;
        padding-bottom: 6px;
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
        margin-top: 8px;
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

    /* Capsule style for login type switch (邮箱 / 用户名) */
    .login-type-capsule {
        display: inline-flex;
        gap: 8px;
        align-items: center;
        padding: 4px;
        background: transparent;
        border-radius: 999px;
        margin: 12px auto; /* 居中 */
        justify-content: center;
    }

    .login-type-row { display:flex; justify-content:center; }

    .login-type-capsule .capsule {
        height: 34px;
        font-size: 13px;
        font-weight: 600;
        color: rgba(20,20,20,0.85);
        padding: 6px 14px;
        border-radius: 18px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        min-width: 70px;
        cursor: pointer;
        border: none;
        background-color: rgba(0, 0, 0, 0.03);
        box-shadow: none;
        transition: all 0.18s ease;
    }

    .login-type-capsule .capsule:hover {
        background-color: rgba(0, 0, 0, 0.06);
    }

    .login-type-capsule .capsule:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.12);
    }

    .login-type-capsule .capsule.active {
        color: #ffffff;
        background-color: $stress-color;
        box-shadow: 0px 3px 5px rgba(128, 128, 128, 0.15);
    }

    /* Element Plus 内部类样式移除；Login.vue 使用自定义 `.my-input` */

    /* Make primary confirm button more prominent */
    .confirm-button {
        @include confirm-button-style;
        width: 100%;
        height: 48px;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 0.3px;
        border-radius: 10px;
        background-color: $stress-color;
        color: #fff;
        border: none;
        transition: transform 0.12s ease, box-shadow 0.12s ease, background-color 0.12s ease;
    }

    .confirm-button:hover {
        @include confirm-button-hover-style;
    }

    /* Make the small text buttons lighter */
    .switcher .el-button {
        color: $stress-color;
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

    /* Custom simple input and button styles to replace element-plus */
    .my-form { display: flex; flex-direction: column; gap: 12px; }
    .form-item { display: flex; flex-direction: column; gap: 6px; }
    .form-label { font-size: 13px; color: #5b6b74; }
    .my-input {
        border-radius: 10px;
        padding: 10px 12px;
        border: 1px solid #e6eef9;
        background: #fbfdff;
        font-size: 14px;
        color: #12212b;
    }
    .my-input:focus { outline: none; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06); border-color: $stress-color; }

    .my-btn { border-radius: 10px; padding: 10px 14px; font-weight: 600; cursor: pointer; border: 1px solid transparent; }
    .my-btn-primary { background: $stress-color; color: white; box-shadow: 0 8px 20px rgba(16,142,254,0.12); }
    .my-btn-text { background: transparent; color: $stress-color; border: none; padding: 6px 8px; }

    /* small adjustments to ensure auth-box content doesn't get clipped */
    .auth-box .login-form, .auth-box .register-form { width: 100%; }

    // 响应式设计
    @media (max-width: 500px) {
        .auth-card {
            grid-template-columns: 1fr;
            padding: 0;
        }

        .auth-card-left { order: 1; padding: 20px; }
        .auth-card-right { order: 2; padding: 8px; }

        .login-container, .register-container {
            width: 100%;
            padding: 18px;
        }
    }
</style>
