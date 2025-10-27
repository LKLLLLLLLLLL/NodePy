<script setup lang = "ts">
    import ControlBar from './components/ControlBar.vue';
    import Project from './views/ProjectList.vue';
    import Home from './views/Home.vue';
    import File from './views/File.vue';
    import Login from './views/Login.vue';
    import Example from './views/Example.vue';
    import Visitor from './views/Visitor.vue';
    import Editor from './views/Editor.vue';
    import { RouterView } from 'vue-router';
    import { usePageStore } from './stores/pageStore';
    import { computed } from 'vue';

    // const pageComponents = {
    //     Program,
    //     Home,
    //     File,
    //     Login,
    //     Example,
    //     Visitor,
    //     Editor
    // }

    // const pageStore = usePageStore();
    // const currentPage = computed(() => pageStore.currentPage);

</script>
<template>
    <div class = "main-container controller-style">
        <div class = "up-container">
            <ControlBar />
        </div>
        <div class = "down-container">
            <RouterView></RouterView>
        </div>
    </div>
    <ModalManager />
</template>
<style scoped lang = "scss">
@use '@/common/style/global.scss';
    .main-container{
        display: flex;
        flex-direction: column;
        width: 100%;
        min-width: 1000px;
        height: 100vh;
        min-height: 800px;
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
