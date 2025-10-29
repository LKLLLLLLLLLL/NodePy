<script lang="ts" setup>
    import { useVueFlow } from '@vue-flow/core';
    import { DefaultService } from '@/utils/api';
    import {ref} from 'vue'
    import Result from '../results/Result.vue'
    import { useModalStore } from '@/stores/modalStore';
    import { autoCaptureDetailed } from './GraphCapture/detailedCapture';
    import SvgIcon from '@jamescoyle/vue-icon'
    import {mdiMagnifyPlusOutline,mdiMagnifyMinusOutline,mdiCrosshairsGps,mdiEyeOutline,mdiEyeOff,mdiContentSave} from '@mdi/js'
    import { autoCaptureMinimap } from './GraphCapture/minimapCapture';
    const modalStore = useModalStore();

    const select = 0
    function captureGraph(vue:any){
        if(select == 0)return autoCaptureMinimap(vue)
        else return autoCaptureDetailed(vue)
    }

    // 定义各个按钮要使用的 mdi 路径
    const mdiZoomIn: string = mdiMagnifyPlusOutline;
    const mdiZoomOut: string = mdiMagnifyMinusOutline;
    const mdiFitView: string = mdiCrosshairsGps;
    const mdiView: string = mdiEyeOutline;
    const mdiHide: string = mdiEyeOff;
    const mdiUploadIcon: string = mdiContentSave;

    const showResult = ref<boolean>(false)

    const props = defineProps<{
        id: string
    }>();

    const {zoomIn,zoomOut,fitView,vueFlowRef} = useVueFlow('main');

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

    async function handleForcedSync(id: string){
        const now_id = Number(id);
        const project = await DefaultService.getProjectApiProjectProjectIdGet(now_id);
        const thumbBase64 = await captureGraph(vueFlowRef.value);
        if (thumbBase64) {
            // 确保是纯 Base64，不带 data URL 前缀
            const pureBase64 = thumbBase64.startsWith('data:image')
                ? thumbBase64.split(',')[1]
                : thumbBase64;

            project.thumb = pureBase64;
        } else {
            project.thumb = null;
        }
        project.updated_at = Math.floor(Date.now() / 1000);
        await DefaultService.syncProjectApiProjectSyncPost(project);
    }

    function handleShowResult(){
        const result_modal = modalStore.findModal('result');

        if(!result_modal){
            const marginRight = 20;
            const modalWidth = 600;
            const modalHeight = 800;
            const xPosition = window.innerWidth - modalWidth - marginRight;
            const yPosition = 75;

            modalStore.createModal({
                id: 'result',
                title: '结果查看',
                isActive: true,
                isDraggable: false,
                isResizable: true,
                position:{
                    x: xPosition,
                    y: yPosition
                },
                size: {
                    width: modalWidth,
                    height: modalHeight
                },
                maxSize: {
                    width: 1000,
                    height: modalHeight
                },
                minSize: {
                    width: modalWidth,
                    height: modalHeight
                },
                component: Result
            });
            showResult.value = true;
        }
        else if(result_modal.isActive){
            modalStore.deactivateModal('result');
            showResult.value = false;
        }
        else {
            modalStore.activateModal('result');
            showResult.value = true;
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
            <button class="gc-btn" type="button" @click="(e) => { animateButton(e); handleForcedSync(props.id); }" aria-label="Sync project">
                <SvgIcon type="mdi" :path="mdiUploadIcon" class="btn-icon" />
            </button>
            <div class="divider"></div>
            <button class="gc-btn" type="button" @click="(e) => { animateButton(e); handleShowResult(); }" aria-label="Toggle result">
                <SvgIcon type="mdi" :path="showResult ? mdiHide : mdiView" class="btn-icon" />
            </button>
        </div>
    </div>
</template>
<style lang="scss" scoped>
@use "../../common/style/global.scss" as *;
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
        @include controller-style;
        display: flex;
        flex-direction: row;
        padding: 3px 5px;
        gap: 4px;
        margin-left: auto;
        margin-right: 8px;
    }

    .divider{
        width: 1px;
        height: 24px;
        margin: 5px 1px;
        background-color: rgba(0, 0, 0, 0.1);
        // margin: 0 4px;
    }

    .gc-btn{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 5px 5px;
        border-radius: 8px;
        cursor: pointer;
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
