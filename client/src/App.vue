<script setup lang = "ts">
    import ControlBar from './components/ControlBar.vue';
    import { useRoute,RouterView } from 'vue-router';

    const route = useRoute();

</script>
<template>
    <div class = "main-container controller-style">
        <div class = "up-container" v-if="route.path!='/login'">
            <ControlBar />
        </div>
        <div class = "down-container">
            <RouterView></RouterView>
        </div>
    </div>
    <ModalManager />
</template>
<style scoped lang = "scss">
@use '@/common/global.scss';
    .main-container{
        display: flex;
        flex-direction: column;
        width: 100%;
        min-width: 1000px;
        height: 100vh;
        min-height: 800px;
        overflow: auto;
    }
    .up-container{
        top: 0;
        z-index: 1000;
        height: 55px;
        width: 100%;
        position: sticky;
        flex-shrink: 0;
    }
    .down-container{
        display: flex;
        flex: 1;
        min-height: 0;
        overflow: auto;
    }
</style>
<!-- <style lang = "scss">
    @import 'splitpanes/dist/splitpanes.css';
    .splitpanes__pane {
        display: flex;
        width: 100%;
        height: 100%;
    }

    .splitpanes--vertical > .splitpanes__splitter {
        width: 6px;
    }

    .splitpanes--horizontal > .splitpanes__splitter {
        height: 6px;
    }
</style> -->
