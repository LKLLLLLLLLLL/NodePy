<script lang="ts" setup>
    import { useVueFlow } from '@vue-flow/core';
    import ChartView from './ChartView.vue';
    import TableView from './TableView.vue';
    import FileView from './FileView.vue';
    import ImageView from './ImageView.vue';
    import ValueView from './ValueView.vue';

</script>
<template>
    <div class = "result-container">
        我是结果
        <!-- <div v-if="!nodeResult">无结果</div>
        <ChartView v-else-if="nodeResult?.resultType === 'chart'" 
                            :data="nodeResult?.resultContent"
                            class = "result-container chart-view">
        </ChartView>
        <TableView v-else-if="nodeResult?.resultType === 'table'" 
                            :data="nodeResult?.resultContent"
                            class = "result-container table-view">
        </TableView>
        <FileView  v-else-if="nodeResult?.resultType === 'file'"  
                            :data="nodeResult?.resultContent"
                            class = "result-container file-view">
        </FileView>
        <ImageView v-else-if="nodeResult?.resultType === 'image'" 
                            :data="nodeResult?.resultContent"
                            class = "result-container image-view">
        </ImageView>
        <ValueView v-else-if="nodeResult?.resultType === 'number' 
                            ||nodeResult?.resultType === 'string' 
                            ||nodeResult?.resultType === 'boolean'"
                            :data="nodeResult?.resultContent"
                            class = "result-container value-view">
        </ValueView> -->
    </div>
</template>
<style lang = "scss" scoped>
    .result-container{
        width: 100%;
        height: 100%;
        flex: 1;
        background-color: #393939;
        color: white;
    }
</style>