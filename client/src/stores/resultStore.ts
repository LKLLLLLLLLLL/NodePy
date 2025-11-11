import { defineStore } from "pinia"
import {ref,computed} from 'vue'
import { useModalStore } from "./modalStore"
import AuthenticatedServiceFactory from "@/utils/AuthenticatedServiceFactory"
import { DataView } from "@/utils/api"
import Result from "@/components/Result/Result.vue"
export const useResultStore = defineStore('result',()=>{

    const modalStore = useModalStore();
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
    const marginRight = 25;
    const marginTop = 75;
    const marginBottom = 75;
    const modalWidth = ref<number>(300);
    const modalHeight = ref<number>(window.innerHeight - marginTop - marginBottom);
    const xPosition = ref<number>(window.innerWidth - modalWidth.value - marginRight);
    const yPosition = ref<number>(marginTop);

    interface ResultCacheItem{
        content: DataView,
        hitCount: number,
        lastHitTime: number
    }

    const default_id: number = 12315

    const resultCache = ref(new Map<Number,ResultCacheItem>());
    const cacheMaxSize: number = 30;//结果数量最大值30

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
                    content: content,
                    hitCount: 1,
                    lastHitTime: Date.now()
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
        hitResultCacheContent,
        addResultCacheContent,
        updateResultCacheContent,
        replaceLeastFrequentlyUsed,
        removeResultCacheContent,
        getResultCacheContent
    }
})