import { defineStore } from 'pinia';
import { ref } from 'vue';
import { ApiError, FileItem, type UserFileList, type Body_upload_file_api_files_upload__project_id__post} from '@/utils/api';
import { DefaultService } from '@/utils/api';
import { ElMessage } from 'element-plus';

export const useFileStore = defineStore('file', () => {

    //fileList default
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

    //single file default
    const default_key: string = 'default_key';
    const default_filename: string = 'default_filename';
    const default_format: FileItem.format = FileItem.format.PNG;
    const default_size: number = 10086;
    const default_modifiedat: number = 20251101;
    const default_pname: string = 'default_pname';
    const default_content: any= 'default_content';
    const default_file: FileItem = {
        key: default_key,
        filename: default_filename,
        format: default_format,
        size: default_size,
        modified_at: default_modifiedat,
        project_name: default_pname
    }

    const userFileList = ref<UserFileList>(default_ufilelist);
    const userFiles = ref<FileItem[]>(default_files);
    const totalSize = ref<number>(default_totalsize);
    const usedSize = ref<number>(default_usedsize);

    const currentFile = ref<FileItem>(default_file);
    const currentKey = ref<string>(default_key);
    const currentContent = ref<string>(default_content)

    function refresh(){
        userFiles.value = default_files;
        totalSize.value = default_totalsize;
        usedSize.value = default_usedsize;
        currentFile.value = default_content;
        currentKey.value = default_key;
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

    async function uploadFile(pid: number,nodeid: string,formData: Body_upload_file_api_files_upload__project_id__post){
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
            const response = await DefaultService.getFileContentApiFilesKeyGet(key);
            currentContent.value = response;
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
            const response = await DefaultService.deleteFileApiFilesKeyDelete(key)
            ElMessage('删除文件成功');
            initializeFiles();
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
        default_file,
        userFileList,
        initializeFiles,
        getUserFileList,
        uploadFile,
        getFileContent,
        deleteFile
    }
})