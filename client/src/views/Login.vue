<script lang="ts" setup>
    import { ref, computed } from 'vue';
    import { ElMessage } from 'element-plus';
    import { useRouter } from 'vue-router';
    // 导入新的认证工具函数
    import { login, signup } from '@/utils/AuthHelper';
    import { usePageStore } from '@/stores/pageStore';

    const router = useRouter();
    const pageStore = usePageStore();

    //el-form config
    const label_width = "80px"
    const label_position = "right"

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
        if(loginType.value=='email')return 'Email';
        else return 'UserName'
    })

    function loginByGoogle(){
        // 谷歌登录逻辑
    }

    function loginByGitHub(){
        // GitHub登录逻辑
    }

    function restrictPassword(){
        
    }

    function restrictUsername(){

    }

    function testAllInfo(){

    }

    function comparePassword(){
        if(password.value==confirm_password.value){
            return true
        }
        else return false
    }

    function jumpToPage(){
        switch(pageStore.currentPage){
            case('File'):
                router.push({
                    name: 'file'
                })
                break;
            case('Example'):
                router.push({
                    name: 'example'
                })
                break;
            case('Home'):
                router.push({
                    name: 'home'
                })
                break;
            case('ProjectList'):
                router.push({
                    name: 'project'
                })
                break;
            case('Visitor'):
                router.push({
                    name: 'visitor'
                })
                break;
            default:
                router.push({
                    name: 'home'
                })
                break;
        }
    }
    
    async function handleLogin(){
        try {
            // 使用新的登录函数
            await login({
                username: username.value,
                password: password.value
            });
            ElMessage('登录成功');
            jumpToPage();
        } catch (error: any) {
            console.error('登录失败:', error);
            if (error.status === 401) {
                ElMessage('用户名或密码错误');
            } else {
                ElMessage('登录失败，请重试');
            }
        }
    }

    async function handleRegister(){
        if(comparePassword()){
            try {
                // 使用新的注册函数
                await signup({
                    username: username.value,
                    email: email.value,
                    password: password.value
                });
                ElMessage('注册成功，已自动登录');
                jumpToPage();
            } catch (error: any) {
                console.error('注册失败:', error);
                if (error.status === 400) {
                    ElMessage('用户名或邮箱已被注册');
                } else {
                    ElMessage('注册失败，请重试');
                }
            }
        }
        else{
            password.value = default_password
            confirm_password.value = default_password
            ElMessage('密码不一致，请重试')
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
                <h2>Sign In to NodePy</h2>
            </div>
            <div class="login-form">
                <el-form>
                    <el-form-item class="login-type-selector">
                        <el-radio-group v-model="loginType">
                            <el-radio-button value="email">Email</el-radio-button>
                            <el-radio-button value="username">Username</el-radio-button>
                        </el-radio-group>
                    </el-form-item>
                </el-form>
                <el-form
                    :label-width="label_width"
                    label-position="right">
                    <el-form-item class="login-account" :label="accountLabel">
                        <el-input 
                            placeholder="Please enter your email"
                            v-if="loginType=='email'"
                            v-model="email"
                        >
                        </el-input>
                        <el-input
                            placeholder="Please enter your username"
                            v-else
                            v-model="username">
                        </el-input>
                    </el-form-item>
                    
                    <el-form-item class="login-password" label="Password">
                        <el-input 
                            placeholder="Please enter your password" 
                            v-model="password"
                            type="password"
                            show-password
                        >
                        </el-input>
                    </el-form-item>
                </el-form>
                <el-form>
                    <el-form-item class="login-control">
                        <el-button type="primary" @click="handleSubmit">Submit</el-button>
                        <el-button @click="handleReset">Reset</el-button>
                    </el-form-item>
                </el-form>
                    
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
                <el-form>
                    <el-form-item class="switcher">
                        <el-button type="text" @click="handleSwitch">Register</el-button>
                    </el-form-item>
                </el-form>
            </div>
        </div>
        <div class="register-container" v-else>
            <div class="login-head">
                <h2>Register for NodePy</h2>
            </div>
            <div class="register-form">
                <el-form
                    :label-width="label_width"
                    :label-position="label_position">
                    <el-form-item class="register-email" label="Email">
                        <el-input 
                            placeholder="Please enter your email" 
                            v-model="email"
                        >
                        </el-input>
                    </el-form-item>
                    
                    <el-form-item class="register-username" label="UserName">
                        <el-input 
                            placeholder="Please enter your username" 
                            v-model="username"
                        >
                        </el-input>
                    </el-form-item>
                    
                    <el-form-item class="register-password" label="Password">
                        <el-input 
                            placeholder="Please enter your password" 
                            v-model="password"
                            type="password"
                            show-password
                        >
                        </el-input>
                    </el-form-item>
                    
                    <el-form-item class="register-password-confirm" label="Confirm">
                        <el-input 
                            placeholder="Please confirm your password" 
                            v-model="confirm_password"
                            type="password"
                            show-password
                        >
                        </el-input>
                    </el-form-item>
                </el-form>
                <el-form>
                    <el-form-item class="register-control">
                        <el-button type="primary" @click="handleSubmit">Create Account</el-button>
                        <el-button @click="handleReset">Reset</el-button>
                    </el-form-item>
                    
                    <el-form-item class="switcher">
                        <el-button type="text" @click="handleSwitch">Return</el-button>
                    </el-form-item>
                </el-form>
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
    }
    .login-container, .register-container {
        display: flex;
        flex-direction: column;
        height: 500px;
        width: 500px;
        background-color: $mix-background-color;
        padding: 20px;
        @include controller-style
    }
    .login-head,.register-head{
        text-align: center;
        height: 50px;
    }
    
    /* 第三方登录样式 */
    .third-party-login {
        margin: 20px 0 10px;
        display: flex;
        flex-direction: column;
    }

    .divider{
        width: 100%;
        text-align: center;
        height: 30px;
    }
    
    .oauth-buttons{
        display: flex;
        justify-content: center;
        align-items: center;
    }
</style>