import { defineStore } from 'pinia'
import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory';
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
}

export const useUserStore = defineStore('user',()=>{

    const default_userinfo: UserInfo = {
        email: 'default@email.com',
        id: -1,
        project_count: -1,
        file_space_used: -1,
        file_space_total: -1,
        username: 'default_user'
    }

    const authService = AuthenticatedServiceFactory.getService();

    const currentUserInfo = ref<UserInfo>(default_userinfo)

    function refreshUserInfo(){
        console.log('refreshed')
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
                }
            }
            else{
                notify({
                    type: 'error',
                    message: 'Unknown error occurred'
                })
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
