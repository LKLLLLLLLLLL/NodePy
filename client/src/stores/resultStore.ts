import { defineStore } from "pinia"
import {ref,computed, watch} from 'vue'
import { useModalStore } from "./modalStore"
import AuthenticatedServiceFactory from "@/utils/AuthenticatedServiceFactory"
import { DataView, type TableView, type ModelView } from "@/utils/api"
import type { File } from "@/utils/api"
import { handleNetworkError } from "@/utils/networkError"
import Result from "@/components/Result/Result.vue"
import { useVueFlow } from "@vue-flow/core"
import { useFileStore } from "./fileStore"
import { useGraphStore } from "./graphStore"
import notify from "@/components/Notification/notify"
import { ApiError } from "@/utils/api"

export type ResultType = string | number | boolean | File | TableView | null | ModelView

export const useResultStore = defineStore('result',()=>{

    const modalStore = useModalStore();
    const graphStore = useGraphStore();
    const fileStore = useFileStore();
    const {nodes} = useVueFlow('main')
    const authService = AuthenticatedServiceFactory.getService();

    const openCache = true

    const default_content: string = 'no-result'
    const default_dataview: DataView = {
        type: DataView.type.STR,
        value: default_content
    }
    const default_info: any = 'default_info'
    const default_id: number = 12315
    const default_typedataid: Record<string,number> = {
        'default_type': default_id
    }

    const currentTypeDataID = ref<{[key:string]:number}>(default_typedataid)
    const currentResult = ref<DataView>(default_dataview)
    const currentInfo = ref<any>(default_info)
    const loading = ref<boolean>(false) // 添加loading状态

    //result modal default
    const marginRight = 20;
    const marginTop = 60;
    const marginBottom = 55;
    const modalWidth = ref<number>(500);
    const modalHeight = ref<number>(window.innerHeight - marginTop - marginBottom);

    // 使用函数来动态计算位置，而不是静态值
    const getXPosition = () => {
        // 确保不会出现负数坐标
        const x = window.innerWidth - modalWidth.value - marginRight;
        return Math.max(marginRight, x);
    };
    const getYPosition = () => marginTop;

    interface ResultCacheItem{
        nodeID: string,
        content: DataView,
        hitCount: number,
        lastHitTime: number,
        createTime: number
    }

    const resultCache = ref(new Map<Number,ResultCacheItem>());
    const cacheMaxSize: number = 30;//结果数量最大值30
    const basicDuration: number = 10*60*1000//10 minutes
    const toBeDeleted = ref<number[]>([])

    const cacheStatus = computed(()=>{
        let hitSum = 0;
        let mostHit = {id: default_id, count: 0}
        resultCache.value.forEach((item, id) => {
            hitSum += item.hitCount;
            if (item.hitCount > mostHit.count) {
                mostHit = { id: Number(id), count: item.hitCount };
            }
        });
        return{
            size: resultCache.value.size,
            hitSum: hitSum,
            mostHit: mostHit
        }
    })

    // 工具函数：将 data_out 转换为类型:data_id 字典
    function convertDataOutToDict(dataOut: Record<string, any>): Record<string, number> {
        const result: Record<string, number> = {};

        for (const [key, value] of Object.entries(dataOut)) {
            // 检查值是否存在且具有 data_id 属性
            if (value && typeof value === 'object' && 'data_id' in value) {
                result[key] = value.data_id;
            }
        }

        return result;
    }

    function refreshResultCache(){
        resultCache.value.clear();
    }

    function getCacheItemsToBeDeleted() {
        const currentNodeIds = new Set(nodes.value.map(node => node.id));
        toBeDeleted.value = []

        //delete nodes that has been deleted but remain in the cache
        resultCache.value.forEach((cacheItem, cacheId) => {
            if (!currentNodeIds.has(cacheItem.nodeID)) {
                toBeDeleted.value.push(Number(cacheId));
            }
        });

        //delete nodes that live longer than limitation
        resultCache.value.forEach((cacheItem,cacheId)=>{
            if(cacheItem.hitCount*basicDuration <= Date.now()-cacheItem.createTime){
                toBeDeleted.value.push(Number(cacheId))
            }
        })

        return toBeDeleted.value.length; // 返回删除的数量
    }

    function cacheGarbageRecycle(){
        // 删除所有标记的缓存项
        const deleteNumber = getCacheItemsToBeDeleted()
        toBeDeleted.value.forEach(cacheId => {
            resultCache.value.delete(cacheId);
        });
        refresh();//确保若删除了当前选中的节点，将会显示默认信息
    }

    function hitResultCacheContent(id: number){
        return resultCache.value.has(id);
    }

    function addResultCacheContent(id: number,content: DataView){
        if(hitResultCacheContent(id)){
            updateResultCacheContent(id,content);
        }
        else{
            if(resultCache.value.size>=cacheMaxSize){
                replaceLeastFrequentlyUsed(id,content);
            }
            else{
                const newCacheItem: ResultCacheItem = {
                    nodeID: graphStore.currentNode?.id as string,
                    content: content,
                    hitCount: 1,
                    lastHitTime: Date.now(),
                    createTime: Date.now()
                }
                resultCache.value.set(id,newCacheItem);
            }
        }
    }

    function updateResultCacheContent(id: number,content: DataView){
        const cacheItem = resultCache.value.get(id);
        if(cacheItem){
            cacheItem.content = content;
            cacheItem.hitCount++;
            cacheItem.lastHitTime = Date.now();
        }
    }

    function replaceLeastFrequentlyUsed(id: number,content: DataView){
        let leastHitId: number = default_id;
        let minHitCount = Infinity;
        let earliestHitTime = Infinity;

        resultCache.value.forEach((item, id) => {
            if (item.hitCount < minHitCount || (item.hitCount === minHitCount && item.lastHitTime < earliestHitTime)) {
                leastHitId = Number(id);
                minHitCount = item.hitCount;
                earliestHitTime = item.lastHitTime;
            }
        });

        removeResultCacheContent(leastHitId);
        addResultCacheContent(id,content);
    }

    function removeResultCacheContent(id: number){
        if(hitResultCacheContent(id)){
            resultCache.value.delete(id);
        }
    }

    async function getResultCacheContent(id: number){
        loading.value = true; // 开始请求时设置loading为true
        try {
            if(openCache){
                const cacheItem = resultCache.value.get(id);
                if(!cacheItem){
                    const content = await authService.getNodeDataApiDataDataIdGet(id);
                    addResultCacheContent(id,content);
                }
                const cacheItem_after = resultCache.value.get(id) as ResultCacheItem;
                cacheItem_after.hitCount++;
                cacheItem_after.lastHitTime = Date.now();
                return cacheItem_after.content;
            }
            else {
                return await authService.getNodeDataApiDataDataIdGet(id);
            }
        } catch (error) {
            // 检查是否是网络错误
            if (error instanceof TypeError && error.message &&
                (error.message.includes('Network Error') || error.message.includes('Failed to fetch'))) {
                notify({
                    message: '网络错误: ' + error.message,
                    type: 'error'
                });
            } else if (error instanceof ApiError) {
                // 处理ApiError
                switch(error.status) {
                    case 403:
                        notify({
                            message: '没有访问权限',
                            type: 'error'
                        });
                        break;
                    case 404:
                        notify({
                            message: '找不到数据',
                            type: 'error'
                        });
                        break;
                    case 422:
                        notify({
                            message: '认证错误',
                            type: 'error'
                        });
                        break;
                    case 500:
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
            else {
                const errMsg = handleNetworkError(error)
                notify({
                    message: errMsg,
                    type: 'error'
                });
            }
            throw error;
        } finally {
            loading.value = false; // 请求完成时（无论成功还是失败）设置loading为false
        }
    }

    function refresh(){
        currentInfo.value = default_info;
        currentResult.value = default_dataview;
    }

    // 监听窗口大小变化，实时更新modalHeight
    const handleWindowResize = () => {
        modalHeight.value = window.innerHeight - marginTop - marginBottom;
        // 更新现有的result modal的位置和大小
        const resultModal = modalStore.modals.find(modal => modal.id === 'result');
        if (resultModal) {
            modalStore.updateModalPosition('result', {
                x: getXPosition(),
                y: getYPosition()
            });
            modalStore.updateModalSize('result', {
                width: resultModal.size?.width || 500,
                height: modalHeight.value
            });
        }
    };

    // 添加窗口大小变化监听器
    if (typeof window !== 'undefined') {
        window.addEventListener('resize', handleWindowResize);
    }

    function createResultModal(){
        // 每次创建时都重新计算位置
        modalStore.createModal({
            id: 'result',
            title: '结果查看',
            isActive: false,
            isDraggable: false,
            isResizable: true,
            // 为Result弹窗添加特殊属性标识
            isResultModal: true,
            position:{
                x: getXPosition(),
                y: getYPosition()
            },
            size: {
                width: modalWidth.value,
                height: modalHeight.value
            },
            // 设置最小尺寸
            minSize: {
                width: 500,
                height: 200
            },
            component: Result
        });
    }

    // 在 resultStore.ts 中更新 downloadResult 函数

    /**
     * 下载结果内容
     * @param dataId 数据ID
     * @param filename 可选的文件名，如果不提供则自动生成
     */
    async function downloadResult(dataId?: number, filename?: string) {
        try {
            notify({
                message: '开始下载结果',
                type: 'info'
            })
            const dataIdToUse = dataId || default_id;
            const result = await getResultCacheContent(dataIdToUse);

            if (!result) {
                notify({
                    message: '无法获取结果内容',
                    type: 'error'
                });
                return;
            }

            let blob: Blob;
            let downloadFilename = filename || `result_${dataIdToUse}`;

            // 根据结果类型处理不同的下载内容
            switch (result.type) {
                case DataView.type.INT:
                case DataView.type.FLOAT:
                case DataView.type.STR:
                case DataView.type.BOOL:
                    // 基本类型转换为字符串
                    const basicValue = String(result.value);
                    blob = new Blob([basicValue], { type: 'text/plain' });
                    // 根据类型添加扩展名
                    const extMap = {
                        [DataView.type.INT]: 'txt',
                        [DataView.type.FLOAT]: 'txt',
                        [DataView.type.STR]: 'txt',
                        [DataView.type.BOOL]: 'txt',
                        [DataView.type.DATETIME]: 'txt',
                    };
                    const ext = extMap[result.type] || 'txt';
                    downloadFilename = filename || `result_${dataIdToUse}.${ext}`;
                    break;

                case DataView.type.TABLE:
                    // 处理表格数据
                    if (result.value && typeof result.value === 'object') {
                        // 转换为CSV格式
                        const csvContent = convertTableToCSV(result.value);
                        blob = new Blob([csvContent], { type: 'text/csv' });
                        downloadFilename = filename || `result_${dataIdToUse}.csv`;
                    } else {
                        // 如果不是对象，直接转为字符串
                        const content = String(result.value);
                        blob = new Blob([content], { type: 'text/plain' });
                        downloadFilename = filename || `result_${dataIdToUse}.txt`;
                    }
                    break;

                case DataView.type.FILE:
                    // 处理文件类型
                    if (result.value && typeof result.value === 'object') {
                        // 假设result.value是File对象
                        const fileValue = result.value as any;

                        // 如果有key属性，使用fileStore下载
                        if ('key' in fileValue && fileValue.key) {
                            const fileStore = useFileStore();
                            await fileStore.downloadFile(fileValue.key, fileValue.filename);
                            return; // fileStore会处理下载，这里直接返回
                        }
                        // 如果有content属性，直接创建Blob
                        else if ('content' in fileValue && fileValue.content) {
                            // 根据content类型创建Blob
                            if (fileValue.content instanceof ArrayBuffer) {
                                blob = new Blob([fileValue.content], {
                                    type: fileValue.contentType || 'application/octet-stream'
                                });
                            } else if (typeof fileValue.content === 'string') {
                                blob = new Blob([fileValue.content], {
                                    type: fileValue.contentType || 'text/plain'
                                });
                            } else {
                                // 其他类型转为JSON
                                const jsonStr = JSON.stringify(fileValue.content, null, 2);
                                blob = new Blob([jsonStr], { type: 'application/json' });
                            }

                            // 确定文件名
                            if ('filename' in fileValue && fileValue.filename) {
                                downloadFilename = fileValue.filename;
                            } else {
                                downloadFilename = filename || `file_${dataIdToUse}`;
                            }
                        } else {
                            notify({
                                message: '文件信息不完整',
                                type: 'error'
                            });
                            return;
                        }
                    } else {
                        notify({
                            message: '文件数据格式错误',
                            type: 'error'
                        });
                        return;
                    }
                    break;

                case DataView.type.DATETIME:
                    // 处理日期时间类型
                    const dateValue = String(result.value);
                    blob = new Blob([dateValue], { type: 'text/plain' });
                    downloadFilename = filename || `result_${dataIdToUse}.txt`;
                    break;

                default:
                    // 默认处理：转换为JSON格式
                    const content = typeof result.value === 'string'
                        ? result.value
                        : JSON.stringify(result.value, null, 2);
                    blob = new Blob([content], { type: 'application/json' });
                    downloadFilename = filename || `result_${dataIdToUse}.json`;
                    break;
            }

            // 创建下载链接
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = downloadFilename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);

            notify({
                message: '结果下载成功',
                type: 'success'
            });

        } catch (error) {
            console.error('下载结果失败:', error);
            notify({
                message: `下载失败: ${error instanceof Error ? error.message : '未知错误'}`,
                type: 'error'
            });
        }
    }

    /**
     * 将表格数据转换为CSV格式
     * @param tableData 表格数据，可能是TableView或其他对象
     */
    function convertTableToCSV(tableData: any): string {
        if (!tableData || typeof tableData !== 'object') {
            return '';
        }

        try {
            // 处理TableView类型（根据API定义）
            if (tableData.columns && tableData.rows) {
                const headers = tableData.columns.map((col: any) => {
                    const header = col.name || col.title || '';
                    // CSV转义：如果包含逗号、双引号或换行符，用双引号包裹
                    if (header.includes(',') || header.includes('"') || header.includes('\n')) {
                        return `"${header.replace(/"/g, '""')}"`;
                    }
                    return header;
                }).join(',');

                const rows = tableData.rows.map((row: any[]) => {
                    return row.map((cell: any) => {
                        const cellStr = cell !== null && cell !== undefined ? String(cell) : '';
                        // CSV转义
                        if (cellStr.includes(',') || cellStr.includes('"') || cellStr.includes('\n')) {
                            return `"${cellStr.replace(/"/g, '""')}"`;
                        }
                        return cellStr;
                    }).join(',');
                }).join('\n');

                return `${headers}\n${rows}`;
            }

            // 处理二维数组
            if (Array.isArray(tableData) && tableData.length > 0 && Array.isArray(tableData[0])) {
                const rows = tableData.map(row => {
                    return row.map((cell: any) => {
                        const cellStr = cell !== null && cell !== undefined ? String(cell) : '';
                        // CSV转义
                        if (cellStr.includes(',') || cellStr.includes('"') || cellStr.includes('\n')) {
                            return `"${cellStr.replace(/"/g, '""')}"`;
                        }
                        return cellStr;
                    }).join(',');
                }).join('\n');

                return rows;
            }

            // 处理对象数组
            if (Array.isArray(tableData) && tableData.length > 0 && typeof tableData[0] === 'object') {
                // 获取所有可能的键作为表头
                const headers = [...new Set(tableData.flatMap(Object.keys))];
                const headerRow = headers.map(header => {
                    if (header.includes(',') || header.includes('"') || header.includes('\n')) {
                        return `"${header.replace(/"/g, '""')}"`;
                    }
                    return header;
                }).join(',');

                const rows = tableData.map(item => {
                    return headers.map(header => {
                        const value = item[header] !== undefined ? String(item[header]) : '';
                        if (value.includes(',') || value.includes('"') || value.includes('\n')) {
                            return `"${value.replace(/"/g, '""')}"`;
                        }
                        return value;
                    }).join(',');
                }).join('\n');

                return `${headerRow}\n${rows}`;
            }

            // 其他情况返回JSON字符串
            return JSON.stringify(tableData, null, 2);
        } catch (error) {
            console.error('转换CSV失败:', error);
            return JSON.stringify(tableData, null, 2);
        }
    }

    return{
        default_dataview,
        default_info,
        default_typedataid,
        currentResult,
        currentInfo,
        currentTypeDataID,
        loading, // 导出loading状态
        modalWidth,
        modalHeight,
        marginRight,
        marginTop,
        marginBottom,
        getXPosition,
        getYPosition,
        createResultModal,
        refresh,
        cacheStatus,
        convertDataOutToDict,
        refreshResultCache,
        cacheGarbageRecycle,
        hitResultCacheContent,
        addResultCacheContent,
        updateResultCacheContent,
        replaceLeastFrequentlyUsed,
        removeResultCacheContent,
        getResultCacheContent,
        downloadResult,
        convertTableToCSV,
    }
})
