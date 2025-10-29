<script lang="ts" setup>
    import { useVueFlow } from '@vue-flow/core';
    import { DefaultService } from '@/utils/api';
    import {computed, ref} from 'vue'
    import Result from '../results/Result.vue'
    import { useModalStore } from '@/stores/modalStore';
    import { autoCaptureMinimapAndSave } from './GraphCapture/minimapCapture';
    import { autoCaptureDetailedAndSave } from './GraphCapture/detailedCapture';
    import {Aim, FullScreen, Lock, Notebook, Upload, View, ZoomIn, ZoomOut,Hide} from '@element-plus/icons-vue'

    const modalStore = useModalStore();

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
        await DefaultService.syncProjectApiProjectSyncPost(project);
        autoCaptureDetailedAndSave(vueFlowRef.value,id);
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

    function handleAnnotate(){

    }

</script>
<template>
    <div class="graph-controls-container">
        <el-button @click="handleZoomIn" :icon="ZoomIn"></el-button>
        <el-button @click="handleZoomOut" :icon="ZoomOut"></el-button>
        <el-button @click="handleFitView" :icon="Aim"></el-button>
        <el-button @click="handleShowResult" v-if="!showResult" :icon="View"></el-button>
        <el-button @click="handleShowResult" v-else :icon="Hide"></el-button>
        <el-button @click="handleForcedSync(props.id)" :icon="Upload"></el-button>
        <el-button @click="handleAnnotate" :icon="Notebook"></el-button>
    </div>
</template>
<style lang="scss" scoped>
    .graph-controls-container{
        display: flex;
        flex-direction: row;
        background-color: grey;
    }
</style>