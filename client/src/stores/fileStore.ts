import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { ApiError, FileItem, type UserFileList, type Body_upload_file_api_files_upload__project_id__post} from '@/utils/api';
import { handleNetworkError } from '@/utils/networkError';
import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory';
import notify from '@/components/Notification/notify';

export const useFileStore = defineStore('file', () => {

    //authenticated service factory
    const authService = AuthenticatedServiceFactory.getService();

    const openCache = true

    //fileList default
    const default_file1: FileItem ={
        key: '123',
        filename: 'lkllll',
        format: FileItem.format.PNG,
        size: 100,
        modified_at: 2077,
        project_name: 'default'
    }
    const default_file2: FileItem ={
        key: '456',
        filename: 'WEH',
        format: FileItem.format.JPG,
        size: 120,
        modified_at: 2072,
        project_name: 'abccc'
    }
    const default_file3: FileItem ={
        key: '789',
        filename: 'zhegebi',
        format: FileItem.format.CSV,
        size: 200,
        modified_at: 10086,
        project_name: 'zhegebi'
    }
    const default_file4: FileItem ={
        key: '000',
        filename: 'weh',
        format: FileItem.format.PDF,
        size: 60,
        modified_at: 1949,
        project_name: 'SOFTWARE'
    }
    const default_file5: FileItem ={
        key: '111',
        filename: 'weh',
        format: FileItem.format.PDF,
        size: 60,
        modified_at: 1949,
        project_name: 'sOFTWARE'
    }
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
    const default_content: any = 'default_content';
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
    const fileContentCache = ref(new Map<string, FileCacheItem>());
    const cacheMaxSize = ref<number>(default_cachesize);

    //cache structure
    interface FileCacheItem {
        content: any,  // 改回 any 类型，保存原始数据格式
        hitCount: number,
        lastHitTime: number
    }

    //cache functions
    const getCacheStatus = computed(() => {
        let hitSum = 0;
        let mostHit = { key: default_key, count: 0 }
        fileContentCache.value.forEach((item: FileCacheItem, key: string) => {
            hitSum += item.hitCount;
            if (item.hitCount > mostHit.count) {
                mostHit = { key: key, count: item.hitCount };
            }
        });
        return {
            size: fileContentCache.value.size,
            hitSum: hitSum,
            mostHit: mostHit
        }
    })

    function refreshCache() {
        fileContentCache.value.clear();
    }

    function addCacheContent(key: string, content: any) {
        if (hitCacheContent(key)) {
            updateCacheContent(key, content);
        } else {
            if (fileContentCache.value.size >= cacheMaxSize.value) {
                replaceLeastFrequentlyUsed(key, content)
            } else {
                const toBeAdded: FileCacheItem = {
                    content: content,
                    hitCount: 1,
                    lastHitTime: Date.now()
                }
                fileContentCache.value.set(key, toBeAdded)
            }
        }
    }

    function updateCacheContent(key: string, content: any) {
        const cacheItem = fileContentCache.value.get(key);
        if (cacheItem) {
            cacheItem.content = content;
            cacheItem.lastHitTime = Date.now();
            cacheItem.hitCount++;
        }
    }

    function removeCacheContent(key: string) {
        if (hitCacheContent(key)) {
            fileContentCache.value.delete(key);
        }
    }

    async function getCacheContent(key: string) {
        if(openCache){
            try {
                const cacheItem = fileContentCache.value.get(key);
                if (!cacheItem) {
                    await getFileContent(key);
                    // 直接缓存原始数据，不进行转换
                    addCacheContent(key, currentContent.value)
                }
                const cacheItem_after = fileContentCache.value.get(key) as FileCacheItem;
                if (cacheItem_after) {
                    cacheItem_after.hitCount++;
                    cacheItem_after.lastHitTime = Date.now();
                    return cacheItem_after.content;
                }
                return null;
            } catch (error) {
                return null
            }
        }
        else {
            return await getFileContent(key);
        }
    }

    function hitCacheContent(key: string) {
        return fileContentCache.value.has(key);
    }

    function replaceLeastFrequentlyUsed(key: string, content: any) {
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
        addCacheContent(key, content);
    }

    //file functions
    function refreshFile() {
        userFiles.value = default_files;
        totalSize.value = default_totalsize;
        usedSize.value = default_usedsize;
        currentFile.value = default_file;
        currentKey.value = default_key;
    }

    function changeCurrentFile(file: FileItem) {
        currentFile.value = file;
    }

    function getCurrentFile() {
        return currentFile.value
    }

    async function initializeFiles() {
        try {
            const response = await authService.listFilesApiFilesListGet();
            userFileList.value = response;
            userFiles.value = response.files || default_files;
            totalSize.value = response.total_size || default_totalsize;
            usedSize.value = response.used_size || default_usedsize;
            refreshCache();
        } catch (error) {
            if (error instanceof ApiError) {
                switch (error.status) {
                    case (404):
                        notify({
                            message: '无法找到文件列表',
                            type: 'error'
                        });
                        break;
                    case (500):
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
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

    async function getUserFileList() {
        try {
            const response = await authService.listFilesApiFilesListGet();
            userFileList.value = response;
            userFiles.value = response.files || default_files;
            totalSize.value = response.total_size || default_totalsize;
            usedSize.value = response.used_size || default_usedsize;
        } catch (error) {
            if (error instanceof ApiError) {
                switch (error.status) {
                    case (404):
                        notify({
                            message: '无法找到文件列表',
                            type: 'error'
                        });
                        break;
                    case (500):
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
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

    async function uploadFile(pid: number, nodeid: string, formData: Body_upload_file_api_files_upload__project_id__post) {
        try {
            const response = await authService.uploadFileApiFilesUploadProjectIdPost(pid, nodeid, formData);
            notify({
                message: '文件上传成功',
                type: 'success'
            });
            await getUserFileList();
        } catch (error) {
            if (error instanceof ApiError) {
                switch (error.status) {
                    case (400):
                        notify({
                            message: '无效的文件或参数',
                            type: 'error'
                        });
                        break;
                    case (403):
                        notify({
                            message: '操作被禁止',
                            type: 'error'
                        });
                        break;
                    case (422):
                        notify({
                            message: '认证错误',
                            type: 'error'
                        });
                        break;
                    case (500):
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
                        break;
                    case (507):
                        notify({
                            message: '存储空间不足',
                            type: 'error'
                        });
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

    async function getFileContent(key: string) {
        try {
            
            // 获取 token
            const token = localStorage.getItem('access_token') || '';
            
            // 使用原生 fetch 获取二进制文件内容
            // DefaultService 的 API 代码生成工具不支持 responseType: 'arraybuffer'
            // 所以必须使用 fetch 来正确处理二进制数据
            const response = await fetch(`/api/files/${key}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }
            
            // 获取 ArrayBuffer
            const arrayBuffer = await response.arrayBuffer();
            
            // 诊断：显示前 10 个字节
            const uint8Array = new Uint8Array(arrayBuffer);
            
            // 转换为 Blob
            const blob = new Blob([arrayBuffer], { type: 'application/octet-stream' });
            currentContent.value = blob;
            return currentContent.value;
            
        } catch (error) {
            // 检查是否是网络错误
            if (error instanceof TypeError && error.message && 
                (error.message.includes('Network Error') || error.message.includes('Failed to fetch'))) {
                notify({
                    message: '网络错误: ' + error.message,
                    type: 'error'
                });
            } else if (error instanceof Error) {
                // 其他错误
                notify({
                    message: '获取文件失败: ' + error.message,
                    type: 'error'
                });
            } else {
                const errMsg = handleNetworkError(error)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
        }
    }

    /**
     * 下载文件
     * @param key 文件key
     * @param filename 可选的文件名，如果不提供则使用原始文件名
     */
    async function downloadFile(key?: string, filename?: string) {
        try {
            notify({
                message: '开始下载文件',
                type: 'info'
            })
            const keyToUse = key || currentKey.value;
            if (!keyToUse || keyToUse === default_key) {
                notify({
                    message: '未指定要下载的文件',
                    type: 'error'
                });
                return;
            }
            
            // 从缓存或API获取文件内容
            const content = await getCacheContent(keyToUse);
            
            if (!content) {
                notify({
                    message: '无法获取文件内容',
                    type: 'error'
                });
                return;
            }
            
            // 确定文件名
            let downloadFilename = filename;
            if (!downloadFilename) {
                // 尝试从当前文件信息获取文件名
                if (currentFile.value && currentFile.value.key === keyToUse) {
                    downloadFilename = currentFile.value.filename;
                } else {
                    // 从文件列表中查找
                    const fileItem = userFiles.value.find(file => file.key === keyToUse);
                    downloadFilename = fileItem?.filename || `file_${keyToUse}`;
                }
            }
            
            // 确保文件名有扩展名
            if (downloadFilename && !downloadFilename.includes('.')) {
                const fileItem = userFiles.value.find(file => file.key === keyToUse);
                if (fileItem?.format) {
                    const extMap: Record<string, string> = {
                        [FileItem.format.PNG]: 'png',
                        [FileItem.format.JPG]: 'jpg',
                        [FileItem.format.PDF]: 'pdf',
                        [FileItem.format.CSV]: 'csv',
                        [FileItem.format.TXT]: 'txt',
                        [FileItem.format.JSON]: 'json',
                    };
                    const ext = extMap[fileItem.format] || '';
                    if (ext) {
                        downloadFilename = `${downloadFilename}.${ext}`;
                    }
                }
            }
            
            // 创建下载链接
            let blob: Blob;
            
            if (content instanceof Blob) {
                // 如果已经是Blob对象，直接使用
                blob = content;
            } else if (typeof content === 'string') {
                // 如果是字符串，转换为Blob
                blob = new Blob([content], { type: 'text/plain' });
            } else if (content instanceof ArrayBuffer) {
                // 如果是ArrayBuffer
                blob = new Blob([content], { type: 'application/octet-stream' });
            } else {
                // 其他类型转换为JSON
                const jsonStr = JSON.stringify(content, null, 2);
                blob = new Blob([jsonStr], { type: 'application/json' });
                if (!downloadFilename?.includes('.')) {
                    downloadFilename = downloadFilename ? `${downloadFilename}.json` : 'file.json';
                }
            }
            
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = downloadFilename || `file_${keyToUse}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            
            notify({
                message: '文件下载成功',
                type: 'success'
            });
            
        } catch (error) {
            console.error('下载文件失败:', error);
            notify({
                message: `下载失败: ${error instanceof Error ? error.message : '未知错误'}`,
                type: 'error'
            });
        }
    }

    /**
     * 下载当前选中的文件
     */
    function downloadCurrentFile() {
        if (currentFile.value && currentFile.value.key) {
            return downloadFile(currentFile.value.key, currentFile.value.filename);
        } else {
            notify({
                message: '未选中任何文件',
                type: 'error'
            });
        }
    }

    return {
        default_file,
        userFileList,
        currentContent,
        currentFile,
        changeCurrentFile,
        getCurrentFile,
        initializeFiles,
        getUserFileList,
        uploadFile,
        getFileContent,
        getCacheStatus,
        refreshCache,
        addCacheContent,
        updateCacheContent,
        removeCacheContent,
        getCacheContent,
        downloadFile,
        downloadCurrentFile,
    }
})
