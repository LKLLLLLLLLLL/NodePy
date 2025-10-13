<script setup lang = "ts">
    import Graph from './components/Graph.vue';
    import ControlBar from './components/ControlBar.vue';
    import NodeSelector from './components/NodeSelector.vue';
    import Property from './components/Property.vue';
    import Result from './components/Result.vue';
</script>
<template>
    <div class = "main-container">
        <div class = "up-container">
            <ControlBar />
        </div>
        <div class = "down-container">
            <NodeSelector />
            <div class = "middle-container">
                <Result/>
                <Graph />
            </div>
            <Property/>
        </div>
    </div>
</template>
<style scoped lang = "scss">
    .main-container{
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 100vh;
    }
    .up-container{
        height: 10%;
        width: 100%;
    }
    .down-container{
        display: flex;
        flex-direction: row;
        width: 100%;
        height: 90%;
    }
    .middle-container{
        flex: 1;
        display: flex;
        flex-direction: column;
    }
</style>