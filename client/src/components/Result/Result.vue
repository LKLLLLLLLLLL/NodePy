<script lang="ts" setup>
    import TableView from './TableView.vue';
    import FileView from './FileView.vue';
    import ValueView from './ValueView.vue';
    import NodeInfo from './NodeInfo.vue';
    import { ref,computed } from 'vue';
    import { useResultStore } from '@/stores/resultStore';

    const resultStore = useResultStore();
    
</script>
<template>
    <div :style="{width: '100%',height: '100%'}">
        <div class = "result-control">
        </div>
        <div class = "result-container">
            <div class="if-result" v-if="resultStore.currentResult!=resultStore.default_dataview">
                <TableView v-if="resultStore.currentResult.type === 'Table'"
                            :value="resultStore.currentResult.value"
                            class = "view-content chart-view">
                </TableView>
                <FileView  v-else-if="resultStore.currentResult.type === 'File'"
                            :value="resultStore.currentResult.value"
                            class = "view-content file-view">
                </FileView>
                <ValueView v-else-if="resultStore.currentResult.type === 'int'
                            ||resultStore.currentResult.type  === 'str'
                            ||resultStore.currentResult.type  === 'bool'
                            ||resultStore.currentResult.type  === 'float'"
                            :value="resultStore.currentResult.value"
                            class = "view-content value-view">
                </ValueView>
            </div>
            <div class="if-info" v-if="resultStore.currentInfo!=resultStore.default_info">
                <NodeInfo :data="resultStore.currentInfo">
                </NodeInfo>
            </div>
        </div>
    </div>
</template>
<style lang = "scss" scoped>
    .result-container{
        width: 100%;
        height: calc(100% - 30px);
        color: white;
        padding: 20px;
        padding-top: 10px;
        border-radius: 10px;
    }
    .result-control{
        height: 30px;
        display: flex;
        margin-left: 20px;
        gap: 5px;
    }
    .view-content{
        width: 100%;
        height: 100%;
    }

</style>
