import { defineStore } from "pinia"
import {ref,computed} from 'vue'
import { useModalStore } from "./modalStore"
import AuthenticatedServiceFactory from "@/utils/AuthenticatedServiceFactory"
import { DataView } from "@/utils/api"
import Result from "@/components/Result/Result.vue"
import { useVueFlow } from "@vue-flow/core"
import { useGraphStore } from "./graphStore"

export const useResultStore = defineStore('result',()=>{

    const modalStore = useModalStore();
    const graphStore = useGraphStore();
    const {nodes} = useVueFlow('main')
    const authService = AuthenticatedServiceFactory.getService();

    const default_content: string = 'no-result'
    const default_dataview: DataView = {
        type: DataView.type.STR,
        value: default_content
    }
    const default_info: any = 'default_info'

    const currentResult = ref<DataView>(default_dataview)
    const currentInfo = ref<any>(default_info)

    //result modal default 
    const marginRight = 30;
    const marginTop = 60;
    const marginBottom = 65;
    const modalWidth = ref<number>(500);
    const modalHeight = ref<number>(window.innerHeight - marginTop - marginBottom);
    const xPosition = ref<number>(window.innerWidth - modalWidth.value - marginRight);
    const yPosition = ref<number>(marginTop);

    interface ResultCacheItem{
        nodeID: string,
        content: DataView,
        hitCount: number,
        lastHitTime: number,
        createTime: number
    }

    const default_id: number = 12315

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

    function refreshResultCache(){
        resultCache.value.clear();
    }

    function getCacheItemsToBeDeleted() {
        const currentNodeIds = new Set(nodes.value.map(node => node.id));
        console.log('@@@@@@',currentNodeIds)
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
        console.log(resultCache)
        console.log('Deleted CacheItems:',deleteNumber)
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

    function refresh(){
        currentInfo.value = default_info;
        currentResult.value = default_dataview;
    }

    function createResultModal(){
        modalStore.createModal({
            id: 'result',
            title: '结果查看',
            isActive: false,
            isDraggable: false,
            isResizable: true,
            position:{
                x: xPosition.value,
                y: yPosition.value
            },
            size: {
                width: modalWidth.value,
                height: modalHeight.value
            },
            component: Result
        });
    }


    return{
        default_dataview,
        default_info,
        currentResult,
        currentInfo,
        modalWidth,
        modalHeight,
        marginRight,
        marginTop,
        marginBottom,
        createResultModal, 
        refresh,
        cacheStatus,
        refreshResultCache,
        cacheGarbageRecycle,
        hitResultCacheContent,
        addResultCacheContent,
        updateResultCacheContent,
        replaceLeastFrequentlyUsed,
        removeResultCacheContent,
        getResultCacheContent
    }
})