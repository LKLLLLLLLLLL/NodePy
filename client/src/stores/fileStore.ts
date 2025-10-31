import { defineStore } from 'pinia';
import { ref } from 'vue';
import { ApiError, type FileItem, type UserFileList } from '@/utils/api';
import { DefaultService } from '@/utils/api';
import { ElMessage } from 'element-plus';
import { elementToViewport } from 'vuetify/lib/components/VOverlay/util/point.mjs';

const default_uid: number = 1;
const default_files: FileItem[] = [];
const default_totalsize: number = 10086;
const default_usedsize: number = 0;
const default_ufilelist: UserFileList = {
    user_id: default_uid,
    files: default_files,
    total_size: default_totalsize,
    used_size: default_usedsize
}
export const useFileStore = defineStore('file', () => {
    const userFileList = ref<UserFileList>(default_ufilelist);
    const userFiles = ref<FileItem[]>(default_files);
    const totalSize = ref<number>(default_totalsize);
    const usedSize = ref<number>(default_usedsize);

    function refresh(){
        userFiles.value = default_files;
        totalSize.value = default_totalsize;
        usedSize.value = default_usedsize;
    }

    async function initializeFiles(){
        try{
            const response = await DefaultService.listFilesApiFilesListGet();
            userFileList.value = response;
            refresh();
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(404):
                        ElMessage('无法找到文件列表');
                        break;
                    case(500):
                        ElMessage('服务器内部错误');
                        break;
                }
            }
        }
    }

    async function getUserFileList(){
        try{
            const response = await DefaultService.listFilesApiFilesListGet();
            userFileList.value = response;
            ElMessage('获取文件列表成功');
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(404):
                        ElMessage('无法找到文件列表');
                        break;
                    case(500):
                        ElMessage('服务器内部错误');
                        break;
                }
            }
        }
    }

    async function uploadFile(pid,nodeid,formData){
        try{
            const response = await DefaultService.uploadFileApiFilesUploadProjectIdPost(pid,nodeid,formData)
            ElMessage('文件上传成功');
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(400):
                        ElMessage('无效的文件或参数');
                        break;
                    case(403):
                        ElMessage('操作被禁止');
                        break;
                    case(422):
                        ElMessage('认证错误');
                        break;
                    case(500):
                        ElMessage('服务器内部错误');
                        break;
                    case(507):
                        ElMessage('存储空间不足');
                        break;
                }
            }
        }
    }

    async function getFileContent(key: string){
        try{
            await DefaultService.getFileContentApiFilesKeyGet(key)
            ElMessage('获取文件内容成功');
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(403):
                        ElMessage('无权访问此文件');
                        break;
                    case(404):
                        ElMessage('找不到文件');
                        break;
                    case(422):
                        ElMessage('认证错误');
                        break;
                    case(500):
                        ElMessage('服务器内部错误');
                        break;
                }
            }
        }
    }

    async function deleteFile(key: string){
        try{
            await DefaultService.deleteFileApiFilesKeyDelete(key)
            ElMessage('删除文件成功');
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(403):
                        ElMessage('无权访问此文件');
                        break;
                    case(404):
                        ElMessage('找不到文件');
                        break;
                    case(422):
                        ElMessage('认证错误');
                        break;
                    case(500):
                        ElMessage('服务器内部错误');
                        break;
                }
            }
        }
    }


    return{
        userFileList,
        initializeFiles,
        getUserFileList,
        uploadFile,
        getFileContent,
        deleteFile
    }
})