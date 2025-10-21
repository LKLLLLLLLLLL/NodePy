<script setup lang = "ts">
    import ControlBar from './components/ControlBar.vue';
    import Program from './views/Program.vue';
    import Home from './views/Home.vue';
    import File from './views/File.vue';
    import Login from './views/Login.vue';
    import { usePageStore } from './stores/pageStore';
    import { computed } from 'vue';

    const pageComponents = {
        Program,
        Home,
        File,
        Login
    }

    const pageStore = usePageStore();
    const currentPage = computed(() => pageStore.currentPage);

</script>
<template>
    <div class = "main-container">
        <div class = "up-container">
            <ControlBar />
        </div>
        <div class = "down-container">
            <component :is="pageComponents[currentPage]" />
        </div>
    </div>
    <ModalManager />
</template>
<style scoped lang = "scss">
    .main-container{
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 100vh;
    }
    .up-container{
        height: 50px;
        width: 100%;
    }
    .down-container{
        display: flex;
        flex: 1;
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