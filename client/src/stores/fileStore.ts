import { defineStore } from 'pinia';
import { ref,computed } from 'vue';
import { ApiError, FileItem, type UserFileList, type Body_upload_file_api_files_upload__project_id__post} from '@/utils/api';
import AuthenticatedServiceFactory from '@/utils/api/services/AuthenticatedServiceFactory';
import { ElMessage } from 'element-plus';

export const useFileStore = defineStore('file', () => {

    //authenticated service factory
    const authService = AuthenticatedServiceFactory.getService();

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

    //single file related info
    const userFileList = ref<UserFileList>(default_ufilelist);
    const userFiles = ref<FileItem[]>(default_files);
    const totalSize = ref<number>(default_totalsize);
    const usedSize = ref<number>(default_usedsize);

    //function related info
    const currentFile = ref<FileItem>(default_file);
    const currentKey = ref<string>(default_key);
    const currentContent = ref<any>(default_content);

    //cache default
    const default_cachesize = 20;//20 files

    //cache info
    const fileContentCache = ref(new Map<string,FileCacheItem>());
    const cacheMaxSize = ref<number>(default_cachesize);

    //cache struture
    interface FileCacheItem{
        content: any,
        hitCount: number,
        lastHitTime: number
    }

    //cache functions
    const getCacheStatus = computed(()=>{
        let hitSum = 0;
        let mostHit = {key: default_key, count: 0}
        fileContentCache.value.forEach((item: FileCacheItem, key: string) => {
            hitSum += item.hitCount;
            if (item.hitCount > mostHit.count) {
                mostHit = { key: key, count: item.hitCount };
            }
        });
        return{
            size: fileContentCache.value.size,
            hitSum: hitSum,
            mostHit: mostHit
        }
    })

    function refreshCache(){
        fileContentCache.value.clear();
    }

    function addCacheContent(key: string,content: any){
        if(hitCacheContent(key)){
            updateCacheContent(key,content);
        }
        else{
            if(fileContentCache.value.size>=cacheMaxSize.value){
                replaceLeastFrequentlyUsed(key,content)
            }
            else{
                const toBeAdded: FileCacheItem ={
                    content: content,
                    hitCount: 1,
                    lastHitTime: Date.now()
                }
                fileContentCache.value.set(key,toBeAdded)
            }
        }  
    }

    function updateCacheContent(key: string,content: any){
        const cacheItem = fileContentCache.value.get(key);
        if(cacheItem){
            cacheItem.content=content;
            cacheItem.lastHitTime=Date.now();
            cacheItem.hitCount++;
        }
    }

    function removeCacheContent(key: string){
        if(hitCacheContent(key)){
            fileContentCache.value.delete(key);
        }
    }
    
    async function getCacheContent(key: string){
        const cacheItem = fileContentCache.value.get(key);
        if(!cacheItem){
            await getFileContent(key);
            addCacheContent(key,currentContent)
        }
        const cacheItem_after = fileContentCache.value.get(key) as FileCacheItem;
            cacheItem_after.hitCount++;
            cacheItem_after.lastHitTime = Date.now();
            return cacheItem_after.content;
    }
    
    function hitCacheContent(key: string){
        return fileContentCache.value.has(key);
    }

    function replaceLeastFrequentlyUsed(key: string,content: any){
        let leastHitKey: string = '';
        let minHitCount = Infinity;
        let earliestHitTime = Infinity;
        
        fileContentCache.value.forEach((item: FileCacheItem, key: string) => {
            if (item.hitCount < minHitCount || (item.hitCount === minHitCount && item.lastHitTime < earliestHitTime)) {
                leastHitKey = key;
                minHitCount = item.hitCount;
                earliestHitTime = item.lastHitTime;
            }
        });

        removeCacheContent(leastHitKey);
        addCacheContent(key,content);

    }

    //file functions
    function refreshFile(){
        userFiles.value = default_files;
        totalSize.value = default_totalsize;
        usedSize.value = default_usedsize;
        currentFile.value = default_content;
        currentKey.value = default_key;
    }

    function changeCurrentFile(file: FileItem){
        currentFile.value = file;
    }

    function getCurrentFile(){
        return currentFile.value
    }

    async function initializeFiles(){
        try{
            const response = await authService.listFilesApiFilesListGet();
            userFileList.value = response;
            refreshFile();
            refreshCache();
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
            const response = await authService.listFilesApiFilesListGet();
            userFileList.value = response;
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
            const response = await authService.uploadFileApiFilesUploadProjectIdPost(pid,nodeid,formData);
            ElMessage('文件上传成功');
            await getUserFileList();
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
            const response = await authService.getFileContentApiFilesKeyGet(key);
            currentContent.value = response;
            ElMessage('获取文件内容成功');
            return currentContent.value
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
            const response = await authService.deleteFileApiFilesKeyDelete(key)
            ElMessage('删除文件成功');
            removeCacheContent(key);
            await getUserFileList();
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
        currentContent,
        changeCurrentFile,
        getCurrentFile,
        initializeFiles,
        getUserFileList,
        uploadFile,
        getFileContent,
        deleteFile,
        getCacheStatus,
        refreshCache,
        addCacheContent,
        updateCacheContent,
        removeCacheContent,
        getCacheContent,
    }
})