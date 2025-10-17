<script lang = "ts" setup>
    import { ref } from 'vue';
    import { useModalStore } from '@/stores/modalStore';
    import Result from './results/Result.vue'

    const modalStore = useModalStore();

    let width0 = 1000;
    let height0 = 1200;
    let x0 = 400;
    let y0 = 300;

    function openResult(){
        modalStore.createModal({
            id: 'result-modal',
            title: 'Result',
            content: 'This is the result modal',
            isActive: true,
            isResizable: false,
            isDraggable: true,
            size: { width: width0, height: height0},
            position: { x: x0, y: y0 },
            minSize: { width: 200, height: 150 },
            maxSize: { width: 1000, height: 800 },
            component: Result
        })
    }

</script>
<template>
    <div class = "control-bar">
        <v-btn 
            @click="openResult" 
            :style="{height: '100%'}"
        >
            唤起结果弹窗
        </v-btn>
    </div>
</template>
<style lang = "scss" scoped>
    .control-bar{
        display: flex;
        flex-direction: row;
        height: 100%;
        width: 100%;
        color: black;
        background-color: #655555;
    }
</style>