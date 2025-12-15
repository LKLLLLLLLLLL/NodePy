import { defineStore } from 'pinia'
import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory';
import { handleNetworkError } from '@/utils/networkError';
import { ApiError } from '@/utils/api';
import { ref } from 'vue';
import notify from '@/components/Notification/notify';

interface UserInfo{
    email: string;
    id: number;
    project_count: number;
    file_space_used: number;
    file_space_total: number;
    username: string;
    // 为将来支持头像功能预留字段
    avatar_url?: string;
}

export const useUserStore = defineStore('user',()=>{

    const default_userinfo: UserInfo = {
        email: 'default@email.com',
        id: -1,
        project_count: -1,
        file_space_used: -1,
        file_space_total: -1,
        username: 'default_user',
        // 为将来支持头像功能预留字段
        avatar_url: undefined
    }

    const authService = AuthenticatedServiceFactory.getService();

    const currentUserInfo = ref<UserInfo>(default_userinfo)

    function refreshUserInfo(){
        currentUserInfo.value = default_userinfo;
    }

    async function initializeUserInfo(){
        refreshUserInfo();
        await getUserInfo();
    }

    async function getUserInfo(){
        try{
            const response = await authService.getCurrentUserInfoApiUserMeGet()
            currentUserInfo.value = response as UserInfo;
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case 401:
                        notify({
                            type: 'error',
                            message: '未认证'
                        })
                        break;
                    case 500:
                        notify({
                            type: 'error',
                            message: '服务器内部错误'
                        })
                        break;
                    default:
                        const errMsg = handleNetworkError(error)
                        notify({
                            message: errMsg,
                            type: 'error'
                        });
                        break;
                }
            }
            else{
                const errMsg = handleNetworkError(error)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
        }
    }

    return {
        currentUserInfo,
        initializeUserInfo,
        refreshUserInfo,
        getUserInfo
    }
})