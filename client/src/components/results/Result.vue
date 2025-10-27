<script lang="ts" setup>
    import TableView from './TableView.vue';
    import FileView from './FileView.vue';
    import ValueView from './ValueView.vue';
    import { useVueFlow } from '@vue-flow/core';
    import { DefaultService } from '@/utils/api';
    import { type DataView } from '@/utils/api';
    import { ref } from 'vue';

    const {onNodeClick,findNode} = useVueFlow('main');

    let url_id = 10086
    const result = ref<DataView>()

    onNodeClick( async (event) => {
        // 获取节点完整信息
        const currentNode = findNode(event.node.id)
        console.log('完整节点信息:', currentNode)
        console.log('Data_id:',currentNode?.data.data_out.result.data_id)
        if(currentNode) url_id = currentNode.data.data_out.result.data_id
        result.value = await getResult(url_id)
        console.log(result)
        console.log(result.value)
    })

    async function getResult(id: number){
        console.log('operating by: ',id)
        const result = await DefaultService.getNodeDataApiDataDataIdGet(id);
        return result;
    }
    
</script>
<template>
    <div :style="{width: '100%',height: '100%'}">
        <div class = "result-control">
        </div>
        <div class = "result-container">
            <div v-if="!result">无结果</div>
            <TableView v-else-if="result.type === 'Table'"
                            :value="result.value"
                            class = "view-content chart-view">
            </TableView>
            <FileView  v-else-if="result.type === 'File'"
                            :value="result.value"
                            class = "view-content file-view">
            </FileView>
            <ValueView v-else-if="result.type === 'int'
                            ||result.type  === 'str'
                            ||result.type  === 'bool'
                            ||result.type  === 'float'"
                            :value="result.value"
                            class = "view-content value-view">
            </ValueView>
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
