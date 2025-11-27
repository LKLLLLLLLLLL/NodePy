<script lang="ts" setup>
    import { ref, watch, onUnmounted, onMounted, nextTick } from 'vue'
    import { useVueFlow } from '@vue-flow/core';
    import { useModalStore } from '@/stores/modalStore';
    import { useGraphStore } from '@/stores/graphStore';
    import { useResultStore } from '@/stores/resultStore';

    import { sync } from '@/utils/network';

    import Result from '../Result/Result.vue'
    import SvgIcon from '@jamescoyle/vue-icon'
    import {mdiMagnifyPlusOutline,mdiMagnifyMinusOutline,mdiCrosshairsGps,mdiEyeOutline,mdiEyeOff,mdiContentSave} from '@mdi/js'

    //stores
    const modalStore = useModalStore();
    const graphStore = useGraphStore();
    const resultStore = useResultStore();

    // 定义各个按钮要使用的 mdi 路径
    const mdiZoomIn: string = mdiMagnifyPlusOutline;
    const mdiZoomOut: string = mdiMagnifyMinusOutline;
    const mdiFitView: string = mdiCrosshairsGps;
    const mdiView: string = mdiEyeOutline;
    const mdiHide: string = mdiEyeOff;
    const mdiUploadIcon: string = mdiContentSave;

    //showResult
    const showResult = ref<boolean>(false)

    watch(()=>{
        return modalStore.findModal('result')?.isActive
    },(newValue)=>{
        if(newValue==undefined){
            showResult.value = false
        }
        else{
            if(newValue)showResult.value = true;
            else showResult.value = false
        }
    },{immediate: true});

    // 监听窗口大小变化，使result-modal右侧边界跟随窗口右侧移动
    let resizeTimer: ReturnType<typeof setTimeout> | null = null
    
    const handleWindowResize = () => {
        // 防抖处理，避免频繁更新
        if (resizeTimer) {
            clearTimeout(resizeTimer)
        }
        
        resizeTimer = setTimeout(() => {
            const resultModal = modalStore.findModal('result')
            if (resultModal && resultModal.isActive) {
                const currentWidth = resultModal.size?.width || resultStore.modalWidth
                const currentHeight = resultModal.size?.height || resultStore.modalHeight
                
                // 限制高度：不超过窗口高度减去上下边距
                const maxHeight = window.innerHeight - resultStore.marginTop - resultStore.marginBottom
                const constrainedHeight = Math.min(currentHeight, maxHeight)
                
                // 限制宽度：不超过窗口宽度减去两侧边距
                const maxWidth = window.innerWidth - resultStore.marginRight * 2
                const constrainedWidth = Math.min(currentWidth, maxWidth)
                
                // 计算X位置：始终将模态框右侧边界放在 marginRight 处
                // X位置 = 窗口宽度 - 模态框宽度 - marginRight
                const newX = Math.max(
                    resultStore.marginRight, 
                    window.innerWidth - constrainedWidth - resultStore.marginRight
                )
                
                // Y位置保持不变或调整以符合顶部边距
                const newY = resultStore.marginTop
                
                // 更新模态框大小和位置
                modalStore.updateModalSize('result', {
                    width: constrainedWidth,
                    height: constrainedHeight
                })
                modalStore.updateModalPosition('result', {
                    x: newX, 
                    y: newY
                })
            }
        }, 0)
    }
    
    // 在挂载时添加 resize 事件监听器
    onMounted(() => {
        window.addEventListener('resize', handleWindowResize)
        // 初始化时也调用一次，确保弹窗位置正确
        nextTick(() => {
            handleWindowResize()
        })
    })

    const {zoomIn,zoomOut,fitView} = useVueFlow('main');

    function handleZoomIn(){
        console.log("zoom-in")
        zoomIn({
            duration: 200
        });
    }

    function handleZoomOut(){
        console.log("zoom-out")
        zoomOut({
            duration: 200
        });
    }

    function handleFitView(){
        fitView({
            padding: 0.1,
            maxZoom: 1,
            duration: 300
        })
    }

    async function handleForcedSync(){
        await sync(graphStore);
    }

    function handleShowResult(){
        const result_modal = modalStore.findModal('result');

        if(!result_modal){
            resultStore.createResultModal();
            modalStore.activateModal('result');
            // 创建后立即调整位置
            setTimeout(() => {
                handleWindowResize()
            }, 0) // 增加延迟确保DOM更新完成
        }
        else if(result_modal.isActive){
            modalStore.deactivateModal('result');
        }
        else {
            modalStore.activateModal('result');
            // 激活后立即调整位置
            setTimeout(() => {
                handleWindowResize()
            }, 0) // 增加延迟确保DOM更新完成
        }

        resultStore.cacheGarbageRecycle()
    }

    function animateButton(e: MouseEvent){
        const el = (e.currentTarget as HTMLElement | null);
        if(!el) return;
        el.classList.add('clicked');
        el.addEventListener('animationend', () => {
            el.classList.remove('clicked');
        }, { once: true });
    }

    // 在组件卸载时清理定时器和事件监听器
    onUnmounted(() => {
        if (resizeTimer) {
            clearTimeout(resizeTimer)
        }
        window.removeEventListener('resize', handleWindowResize)
    })

</script>
<template>
    <div class="graph-controls-container">
        <div class="graph-controls-left">
            <button class="gc-btn" type="button" @click="(e) => { animateButton(e); handleZoomIn();}" aria-label="Zoom in">
                <SvgIcon type="mdi" :path="mdiZoomIn" class="btn-icon zoom" />
            </button>

            <button class="gc-btn" type="button" @click="(e) => { animateButton(e); handleZoomOut();}" aria-label="Zoom out">
                <SvgIcon type="mdi" :path="mdiZoomOut" class="btn-icon zoom" />
            </button>

            <div class="divider"></div>

            <button class="gc-btn" type="button" @click="(e) => { animateButton(e); handleFitView();}" aria-label="Fit view">
                <SvgIcon type="mdi" :path="mdiFitView" class="btn-icon" />
            </button>
        </div>

        <div class="graph-controls-right">
            <div class="gc-btn-container">
                <button class="gc-btn" type="button" @click="(e) => { animateButton(e); handleForcedSync(); }" aria-label="Sync project">
                    <SvgIcon type="mdi" :path="mdiUploadIcon" class="btn-icon" />
                    <div class="gc-btn-text">同步</div>
                </button>
            </div>
            <!-- <div class="divider"></div> -->
            <div class="gc-btn-container">
                <button class="gc-btn" type="button" @click="(e) => { animateButton(e); handleShowResult(); }" aria-label="Toggle result">
                    <SvgIcon type="mdi" :path="showResult ? mdiHide : mdiView" class="btn-icon" />
                    <div class="gc-btn-text">{{ showResult ? '隐藏结果' : '查看结果' }}</div>
                </button>
            </div>
        </div>
    </div>
</template>
<style lang="scss" scoped>
@use "../../common/global.scss" as *;
    .graph-controls-container{
        display: flex;
        flex-direction: row;
        width: 100vw;
        padding-left: 240px;
        padding-right: 10px;
        // gap: 8px;
        align-items: center;
        background-color: transparent;
    }

    .graph-controls-left{
        @include controller-style;
        display: flex;
        padding: 3px 5px;
        flex-direction: row;
        gap: 4px;
        margin-left: 8px;
    }

    .graph-controls-right{
        display: flex;
        flex-direction: row;
        gap: 10px;
        margin-left: auto;
        margin-right: 8px;
    }

    .divider{
        width: 1px;
        height: 24px;
        margin: 5px 1px;
        background-color: rgba(0, 0, 0, 0.1);
    }

    .gc-btn-container{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 3px 5px;
        @include controller-style;
    }

    .gc-btn{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 5px 5px;
        border-radius: 8px;
        cursor: pointer;
        .gc-btn-text{
            margin-left: 4px;
            font-size: 16px;
            color: rgba(0, 0, 0, 0.75);
            user-select: none;
        }
    }

    .zoom { // zoom icon looks smaller, so enlarge it a bit
        width: 26px !important;
        height: 26px !important;
    }

    .btn-icon{
        width: 24px;
        height: 24px;
        display: inline-block;
        color: rgba(0, 0, 0, 0.75);
    }

    .gc-btn.clicked{
        animation: clickGray 200ms ease;
    }

    @keyframes clickGray {
        0%   { background-color: transparent; }
        40%  { background-color: rgba(128,128,128,0.35); }
        100% { background-color: transparent; }
    }
</style>