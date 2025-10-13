<script setup lang = "ts">
    import Graph from './components/Graph.vue';
    import ControlBar from './components/ControlBar.vue';
    import NodeSelector from './components/NodeSelector.vue';
    import Property from './components/Property.vue';
    import Result from './components/Result.vue';
    import { useLayoutStore } from './stores/layoutStore';
    import { Splitpanes, Pane } from 'splitpanes';
    const layoutStore = useLayoutStore();

</script>
<template>
    <div class = "main-container">
        <div class = "up-container">
            <ControlBar />
        </div>
        <Splitpanes 
            class = "down-container"
            vertical
        >
            <Pane :size="15" :min-size="10">
                <NodeSelector />
            </Pane>
            <Pane :size="70" :min-size="40">
                <Splitpanes
                    horizontal
                >
                    <Pane :size="40" :min-size="20">
                        <Result/>
                    </Pane>
                    <Pane :size="60" :min-size="20">
                        <Graph />
                    </Pane>
                </Splitpanes>
            </Pane>
            <Pane :size="15" :min-size="10">
                <Property/>
            </Pane>
        </Splitpanes>
    </div>
    <ModalManager />
</template>
<style scoped lang = "scss">
    .main-container{
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 98vh;
    }
    .up-container{
        height: 50px;
        width: 100%;
    }
    .down-container{
        flex: 1;
    }
</style>
<style lang = "scss">
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
</style>