<script lang="ts" setup>
    import { ref, watch } from 'vue'
    import { useVueFlow } from '@vue-flow/core';
    import { useModalStore } from '@/stores/modalStore';
    import { useGraphStore } from '@/stores/graphStore';
    import { useResultStore } from '@/stores/resultStore';

    import { autoCaptureDetailed } from './GraphCapture/detailedCapture';
    import { autoCaptureMinimap } from './GraphCapture/minimapCapture';
    import { DefaultService, type Project } from '@/utils/api';
    import { getProject } from '@/utils/projectConvert';
    import { syncProject } from '@/utils/network';

    import Result from '../Result/Result.vue'
    import SvgIcon from '@jamescoyle/vue-icon'
    import {mdiMagnifyPlusOutline,mdiMagnifyMinusOutline,mdiCrosshairsGps,mdiEyeOutline,mdiEyeOff,mdiContentSave} from '@mdi/js'

    //stores
    const modalStore = useModalStore();
    const graphStore = useGraphStore();
    const resultStore = useResultStore();

    const select = 0

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

    // 在 GraphControls.vue 中修复watch
    watch(() => {
        return {
            width: window.innerWidth,
            height: window.innerHeight
        }
    }, () => {
        const resultModal = modalStore.findModal('result')
        if (resultModal && resultModal.isActive) {
            // 使用当前store中的宽度，或者默认值
            const currentWidth = resultModal.size?.width || resultStore.modalWidth
            const constrainedWidth = Math.min(currentWidth, window.innerWidth - resultStore.marginRight * 2)
        
            const constrainedHeight = Math.min(
                window.innerHeight - resultStore.marginTop - resultStore.marginBottom,
                resultModal.maxSize?.height || Number.MAX_SAFE_INTEGER
            )
        
            // 计算约束后的位置
            const newX = Math.max(0, window.innerWidth - constrainedWidth - resultStore.marginRight)
            const newY = Math.max(0, resultStore.marginTop)
        
            modalStore.updateModalSize('result', {
                width: constrainedWidth,
                height: constrainedHeight
            })
            modalStore.updateModalPosition('result', {
                x: newX, 
                y: newY
            })
        }
    }, { immediate: true })

    const {zoomIn,zoomOut,fitView,vueFlowRef} = useVueFlow('main');

    function captureGraph(vue:any){
        if(select == 0)return autoCaptureMinimap(vue)
        else return autoCaptureDetailed(vue)
    }

    function handleZoomIn(){
        console.log("zoom-in")
        zoomIn();
    }

    function handleZoomOut(){
        console.log("zoom-out")
        zoomOut();
    }

    function handleFitView(){
        fitView();
    }

    async function handleForcedSync(){
        //@ts-ignore
        const project: Project = getProject(graphStore.project);
        await syncProject(project, graphStore);
    }

    function handleShowResult(){
        const result_modal = modalStore.findModal('result');

        if(!result_modal){
            resultStore.createResultModal();
            modalStore.activateModal('result');
        }
        else if(result_modal.isActive){
            modalStore.deactivateModal('result');
        }
        else {
            modalStore.activateModal('result');
        }
    }

    function animateButton(e: MouseEvent){
        const el = (e.currentTarget as HTMLElement | null);
        if(!el) return;
        el.classList.add('clicked');
        el.addEventListener('animationend', () => {
            el.classList.remove('clicked');
        }, { once: true });
    }


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
