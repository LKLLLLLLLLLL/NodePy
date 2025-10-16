<script lang = "ts" setup>
    import { ref } from 'vue';
    import { useModalStore } from '@/stores/modalStore';
    import Result from './results/Result.vue'

    const modalStore = useModalStore();

    let resultID = 0;
    let width0 = 400;
    let height0 = 300;
    let x0 = 500;
    let y0 = 500;
    function openResult(){
        modalStore.createModal({
            id: 'result-modal'+(resultID++),
            title: 'Result'+(resultID),
            content: 'This is the result modal'+(resultID),
            isActive: true,
            isResizable: false,
            size: { width: width0++, height: height0++ },
            position: { x: x0++, y: y0++ },
            minSize: { width: 200, height: 150 },
            maxSize: { width: 800, height: 600 },
            component: Result
        })
    }

</script>
<template>
    <div class = "control-bar">
        <v-btn @click="openResult">唤起结果弹窗</v-btn>
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