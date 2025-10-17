<script lang="ts" setup>
    import ChartView from './ChartView.vue';
    import TableView from './TableView.vue';
    import FileView from './FileView.vue';
    import ImageView from './ImageView.vue';
    import ValueView from './ValueView.vue';
    import { useGraphStore } from '@/stores/graphStore';

    const graphStore = useGraphStore();

    const {getNodes,findNode} = graphStore.vueFlowInstance

    const currentNode = findNode('2')

    console.log(currentNode.data.label)
</script>
<template>
    <div :style="{width: '100%',height: '100%'}">
        <div class = "result-control">
            <v-btn height="100%">按钮</v-btn>
            <v-btn height="100%">按钮</v-btn>
        </div>
        <div class = "result-container">
            <div v-if="!currentNode">无结果</div>
            <ChartView v-else-if="currentNode.data.resultType === 'chart'" 
                            :data="currentNode.data"
                            class = "view-content chart-view">
            </ChartView>
            <TableView v-else-if="currentNode.data.resultType === 'table'" 
                            :data="currentNode.data"
                            class = "view-content table-view">
            </TableView>
            <FileView  v-else-if="currentNode.data.resultType === 'file'"  
                            :data="currentNode.data"
                            class = "view-content file-view">
            </FileView>
            <ImageView v-else-if="currentNode.data.resultType  === 'image'" 
                            :data="currentNode.data"
                            class = "view-content image-view">
            </ImageView>
            <ValueView v-else-if="currentNode.data.resultType  === 'number' 
                            ||currentNode.data.resultType  === 'string' 
                            ||currentNode.data.resultType  === 'boolean'"
                            :data="currentNode.data"
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