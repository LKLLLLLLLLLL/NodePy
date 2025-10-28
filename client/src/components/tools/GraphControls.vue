<script lang="ts" setup>
    import { useVueFlow } from '@vue-flow/core';
    import { DefaultService } from '@/utils/api';
    import Result from './results/Result.vue';
    import { useModalStore } from '@/stores/modalStore';

    const modalStore = useModalStore();

    const props = defineProps<{
        id: string
    }>();

    const {zoomIn,zoomOut,fitView} = useVueFlow('main');

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
        await DefaultService.syncProjectApiProjectSyncPost(project);
    }

    function handleShowResult(){
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
            isResizable: false,
            position:{
                x: xPosition,
                y: yPosition
            },
            size: {
                width: modalWidth,
                height: modalHeight
            },
            component: Result
        })
    }

    function handleAnnotate(){

    }
</script>
<template>
    <div class="graph-controls-container">
        <el-button @click="handleZoomIn">ZoomIn</el-button>
        <el-button @click="handleZoomOut">ZoomOut</el-button>
        <el-button @click="handleFitView">FitView</el-button>
        <el-button @click="handleShowResult">ShowResult</el-button>
        <el-button @click="handleForcedSync(props.id)">ForcedSync</el-button>
        <el-button @click="handleAnnotate">Annotate</el-button>
    </div>
</template>
<style lang="scss" scoped>
    .graph-controls-container{
        display: flex;
        flex-direction: row;
        background-color: grey;
    }
</style>