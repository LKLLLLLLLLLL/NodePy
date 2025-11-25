<script lang="ts" setup>
    import TableView from './TableView.vue';
    import FileView from './FileView.vue';
    import ValueView from './ValueView.vue';
    import NodeInfo from './NodeInfo.vue';
    import { watch, ref,computed, onMounted } from 'vue';
    import { useResultStore } from '@/stores/resultStore';
    import { useGraphStore } from '@/stores/graphStore';

    const resultStore = useResultStore();
    const graphStore = useGraphStore()
    const resultId = computed(()=>{
        const dataOut = graphStore.currentNode?.data.data_out
        if (!dataOut) {
            console.log('Result: 当前节点没有 data_out')
            return undefined
        }

        if (dataOut.plot?.data_id) {
            return dataOut.plot.data_id
        }
        else if (dataOut.const?.data_id) {
            return dataOut.const.data_id
        }
        else if (dataOut.file?.data_id) {
            return dataOut.file.data_id
        }
        else if (dataOut.table?.data_id) {
            return dataOut.table.data_id
        }
        return undefined
    })

    watch([() => graphStore.currentNode, resultId], async ([newNode, newResultId]) => {
        try {
            
            if (!newResultId) {
                console.log('Result: resultId 不存在，显示节点信息');
                resultStore.currentInfo = newNode?.data?.param || {};
                resultStore.currentResult = resultStore.default_dataview;
                return;
            }
            
            resultStore.currentInfo = resultStore.default_info;
            
            // 先设置为默认值，避免显示旧数据
            resultStore.currentResult = resultStore.default_dataview;
            
            // 获取新结果
            const result = await resultStore.getResultCacheContent(newResultId);
            resultStore.currentResult = result;
            
        } catch (error) {
            console.error('Result: 加载结果失败:', error);
            resultStore.currentInfo = newNode?.data?.param || {};
            resultStore.currentResult = resultStore.default_dataview;
        }
    }, { immediate: true });

</script>
<template>
    <div :style="{width: '100%',height: '100%'}">
        <div class = "result-control">
            Control
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
            <!-- <div class="if-info" v-if="resultStore.currentInfo!=resultStore.default_info">
                <NodeInfo :data="resultStore.currentInfo">
                </NodeInfo>
            </div> -->
        </div>
    </div>
</template>
<style lang = "scss" scoped>
    .result-container{
        width: 100%;
        height: calc(100% - 30px);
        color: grey;
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
