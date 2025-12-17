<script lang="ts" setup>
    import { ref, watch, computed, onUnmounted, onMounted, nextTick } from 'vue'
    import { useVueFlow } from '@vue-flow/core';
    import { useModalStore } from '@/stores/modalStore';
    import { useGraphStore } from '@/stores/graphStore';
    import { useResultStore } from '@/stores/resultStore';
    import { useLoginStore } from '@/stores/loginStore';
    import { useProjectStore } from '@/stores/projectStore';
    import { useRoute } from 'vue-router';
    import { useRouter } from 'vue-router';

    import { sync } from '@/utils/network';

    import Result from '../Result/Result.vue'
    import notify from '../Notification/notify';

    import SvgIcon from '@jamescoyle/vue-icon'
    import {
        mdiMagnifyPlusOutline,
        mdiMagnifyMinusOutline,
        mdiCrosshairsGps,
        mdiEyeOutline,
        mdiEyeOff,
        mdiContentSave,
        mdiMusicAccidentalSharp,
        mdiTextBoxOutline,
        mdiCommaBoxOutline,
        mdiFormatQuoteOpen,
        mdiOpenInNew
    } from '@mdi/js'

    //stores
    const graphStore = useGraphStore()
    const modalStore = useModalStore()
    const loginStore = useLoginStore()
    const resultStore = useResultStore()
    const projectStore = useProjectStore()
    const route = useRoute()
    const router = useRouter()

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

    const {zoomIn,zoomOut,fitView, onPaneClick, screenToFlowCoordinate} = useVueFlow('main');
    let pendingAnnotateOff: (() => void) | null = null
    const armedAnnotateType = ref<'text' | 'title' | null>(null)

    function handleZoomIn(){
        zoomIn({
            duration: 200
        });
    }

    function handleZoomOut(){
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

    const clearPendingAnnotate = () => {
        if (pendingAnnotateOff) {
            try { pendingAnnotateOff() } catch (e) {}
            pendingAnnotateOff = null
        }
        armedAnnotateType.value = null
    }

    const armAnnotatePlacement = (type: 'text' | 'title') => {
        // toggle: clicking the same button again cancels
        if (armedAnnotateType.value === type) {
            clearPendingAnnotate()
            return
        }
        // clear previous pending listener
        clearPendingAnnotate()
        armedAnnotateType.value = type
        const disposer = onPaneClick((event: MouseEvent) => {
            const flowPos = screenToFlowCoordinate({ x: event.clientX, y: event.clientY })
            const nodeType = type === 'text' ? 'TextAnnotationNode' : 'TitleAnnotationNode'
            graphStore.addNode(nodeType, { x: flowPos.x, y: flowPos.y })
            clearPendingAnnotate()
        })
        if (typeof disposer === 'function') {
            pendingAnnotateOff = disposer
        } else if (disposer && typeof (disposer as any).off === 'function') {
            pendingAnnotateOff = (disposer as any).off
        }
    }

    function handleTitleAnnotate(){
        armAnnotatePlacement('title')
    }

    function handleTextAnnotate(){
        armAnnotatePlacement('text')
    }

    // 判断项目是否为只读模式
    const isReadOnly = computed(() => {
        return graphStore.project.editable === false
    })

    async function handleCopy(){
        const newProjectId = await projectStore.copyProject(Number(route.params.projectId))

        if (newProjectId) {
            // 使用原生URL跳转方法
            window.location.href = `/project/${newProjectId}`;

            notify({
                message: '项目复制成功',
                type: 'success'
            })
        }
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
        <div class="graph-controls-left-container">
            <div class="graph-controls-left left_1">
                <div class="gc-btn-container">
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
            </div>
            <div v-if="!isReadOnly" class="graph-controls-left left_2">
                <div class="gc-btn-container">
                    <button class="gc-btn" :class="{ armed: armedAnnotateType === 'title' }" type="button" @click="(e) => { animateButton(e); handleTitleAnnotate();}" aria-label="Title annotate">
                        <SvgIcon type="mdi" :path="mdiFormatQuoteOpen" class="btn-icon quote" />
                        <div class="gc-btn-text">注释</div>
                    </button>

                    <div class="divider"></div>

                    <button class="gc-btn" :class="{ armed: armedAnnotateType === 'text' }" type="button" @click="(e) => { animateButton(e); handleTextAnnotate();}" aria-label="Text annotate">
                        <SvgIcon type="mdi" :path="mdiTextBoxOutline" class="btn-icon" />
                        <div class="gc-btn-text">文本注释</div>
                    </button>
                </div>
            </div>
        </div>

        <div class="graph-controls-right-container">
            <div class="graph-controls-right right_1">
                <div v-if="!isReadOnly" class="gc-btn-container">
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
            <div class="graph-controls-right right_2" v-if="isReadOnly">
                <div class="gc-btn-container">
                    <button class="gc-btn" type="button" @click="(e) => { animateButton(e); handleCopy(); }" aria-label="Copy project">
                        <SvgIcon type="mdi" :path="mdiOpenInNew" class="btn-icon" />
                        <div class="gc-btn-text">在工作台中打开</div>
                    </button>
                </div>
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
        padding-left: 235px;
        padding-right: 10px;
        // gap: 8px;
        align-items: center;
        background-color: transparent;
    }

    .graph-controls-left-container{
        display: flex;
        flex-direction: row;
        gap: 8px;
    }

    .graph-controls-left{
        display: flex;
        padding: 3px 5px;
        flex-direction: row;
        gap: 4px;
        margin-left: 0px;
    }

    .graph-controls-right-container{
        display: flex;
        flex-direction: row;
        gap: 8px;
        margin-left: auto;
        margin-right: 8px;
    }

    .graph-controls-right{
        display: flex;
        flex-direction: row;
        gap: 10px;
    }

    .graph-controls-right.right_2 .gc-btn-container{
        background-color: $stress-color;
        .gc-btn-text, .btn-icon{
            color: #fff;
        }
        .btn-icon{
            width: 21px;
            height: 21px;
        }
        &:hover{
            @include confirm-button-hover-style;
        }
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
        &.armed{
            background-color: rgba(0, 0, 0, 0.08);
        }
    }

    .zoom { // zoom icon looks smaller, so enlarge it a bit
        width: 26px !important;
        height: 26px !important;
    }

    .quote {
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
