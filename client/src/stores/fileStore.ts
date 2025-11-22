import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { ApiError, FileItem, type UserFileList, type Body_upload_file_api_files_upload__project_id__post} from '@/utils/api';
import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory';
import notify from '@/components/Notification/notify';

export const useFileStore = defineStore('file', () => {

    //authenticated service factory
    const authService = AuthenticatedServiceFactory.getService();

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
        console.log('fileStore: 缓存已清空')
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
                console.log('fileStore: 已添加缓存，key:', key, '内容类型:', typeof content, '缓存大小:', fileContentCache.value.size)
            }
        }
    }

    function updateCacheContent(key: string, content: any) {
        const cacheItem = fileContentCache.value.get(key);
        if (cacheItem) {
            cacheItem.content = content;
            cacheItem.lastHitTime = Date.now();
            cacheItem.hitCount++;
            console.log('fileStore: 已更新缓存，key:', key)
        }
    }

    function removeCacheContent(key: string) {
        if (hitCacheContent(key)) {
            fileContentCache.value.delete(key);
            console.log('fileStore: 已移除缓存，key:', key)
        }
    }

    async function getCacheContent(key: string): Promise<any> {
        try {
            const cacheItem = fileContentCache.value.get(key);
            if (!cacheItem) {
                console.log('fileStore: 缓存未命中，从 API 获取:', key)
                await getFileContent(key);
                // 直接缓存原始数据，不进行转换
                addCacheContent(key, currentContent.value)
            }
            const cacheItem_after = fileContentCache.value.get(key) as FileCacheItem;
            if (cacheItem_after) {
                cacheItem_after.hitCount++;
                cacheItem_after.lastHitTime = Date.now();
                console.log('fileStore: 从缓存返回内容，key:', key, '类型:', typeof cacheItem_after.content)
                return cacheItem_after.content;
            }
            return null;
        } catch (error) {
            console.error('fileStore: getCacheContent 失败:', error)
            return null
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
        console.log('fileStore: 已替换最少使用缓存，移除:', leastHitKey, '添加:', key)
    }

    //file functions
    function refreshFile() {
        userFiles.value = default_files;
        totalSize.value = default_totalsize;
        usedSize.value = default_usedsize;
        currentFile.value = default_file;
        currentKey.value = default_key;
        console.log('fileStore: 文件信息已重置')
    }

    function changeCurrentFile(file: FileItem) {
        currentFile.value = file;
        console.log('fileStore: 当前文件已切换，key:', file.key, '格式:', file.format)
    }

    function getCurrentFile() {
        return currentFile.value
    }

    async function initializeFiles() {
        try {
            console.log('fileStore: 开始初始化文件列表...')
            const response = await authService.listFilesApiFilesListGet();
            userFileList.value = response;
            userFiles.value = response.files || default_files;
            totalSize.value = response.total_size || default_totalsize;
            usedSize.value = response.used_size || default_usedsize;
            refreshCache();
            console.log('fileStore: 文件列表初始化成功，共', userFiles.value.length, '个文件')
        } catch (error) {
            console.error('fileStore: initializeFiles 失败:', error)
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
                }
            }
        }
    }

    async function getUserFileList() {
        try {
            console.log('fileStore: 获取用户文件列表...')
            const response = await authService.listFilesApiFilesListGet();
            userFileList.value = response;
            userFiles.value = response.files || default_files;
            totalSize.value = response.total_size || default_totalsize;
            usedSize.value = response.used_size || default_usedsize;
            console.log('fileStore: 文件列表已更新，共', userFiles.value.length, '个文件')
        } catch (error) {
            console.error('fileStore: getUserFileList 失败:', error)
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
                }
            }
        }
    }

    async function uploadFile(pid: number, nodeid: string, formData: Body_upload_file_api_files_upload__project_id__post) {
        try {
            console.log('fileStore: 开始上传文件到项目', pid)
            const response = await authService.uploadFileApiFilesUploadProjectIdPost(pid, nodeid, formData);
            notify({
                message: '文件上传成功',
                type: 'success'
            });
            await getUserFileList();
            console.log('fileStore: 文件上传成功')
        } catch (error) {
            console.error('fileStore: uploadFile 失败:', error)
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
                }
            }
        }
    }

    async function getFileContent(key: string) {
        try {
            console.log('fileStore: 开始获取文件内容，key:', key)
            
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
            console.log('fileStore: 成功获取到 ArrayBuffer，大小:', arrayBuffer.byteLength)
            
            // 诊断：显示前 10 个字节
            const uint8Array = new Uint8Array(arrayBuffer);
            console.log('fileStore: 前 10 个字节:', Array.from(uint8Array.slice(0, 10)).map(b => '0x' + b.toString(16).padStart(2, '0')).join(' '))
            
            // 转换为 Blob
            const blob = new Blob([arrayBuffer], { type: 'application/octet-stream' });
            currentContent.value = blob;
            return currentContent.value;
            
        } catch (error) {
            console.error('fileStore: 获取文件失败:', error)
            notify({
                message: '获取文件失败: ' + (error instanceof Error ? error.message : String(error)),
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
    }
})
