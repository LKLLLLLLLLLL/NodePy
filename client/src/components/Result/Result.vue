<script lang="ts" setup>
    import type { ResultType } from '@/stores/resultStore';
    import TableView from './TableView.vue';
    import FileView from './FileView.vue';
    import ValueView from './ValueView.vue';
    import NodeInfo from './NodeInfo.vue';
    import Loading from '../Loading.vue'; // 引入Loading组件
    import { watch, ref,computed, onMounted } from 'vue';
    import { useResultStore } from '@/stores/resultStore';
    import { useGraphStore } from '@/stores/graphStore';

    const resultStore = useResultStore();
    const graphStore = useGraphStore()

    // 监听currentTypeDataID字典变化
    watch(() => resultStore.currentTypeDataID, async (newTypeDataID, oldTypeDataID) => {
        try {
            console.log("@@@@@@@newTypeDataID", newTypeDataID);
            console.log("@@@@@@@oldTypeDataID", oldTypeDataID);
            if(newTypeDataID === resultStore.default_typedataid){
                resultStore.currentResult = resultStore.default_dataview
                resultStore.currentInfo = resultStore.default_info
                return 
            }
            // 获取字典中的第一个值作为默认结果ID
            const keys = Object.keys(newTypeDataID);
            if (keys.length > 0) {
                const firstKey = keys[0]!;
                const dataId = newTypeDataID[firstKey];
                
                // 检查是否是有效数字
                if (typeof dataId === 'number' && !isNaN(dataId)) {
                    resultStore.currentInfo = resultStore.default_info;
                    resultStore.currentResult = resultStore.default_dataview;
                    
                    // 获取新结果
                    const result = await resultStore.getResultCacheContent(dataId);
                    resultStore.currentResult = result;
                    console.log("@@@newResult:", resultStore.currentResult);
                }
            }
            
        } catch (error) {
            console.error('Result: 加载结果失败:', error);
            resultStore.currentInfo = graphStore.currentNode?.data?.param || {};
            resultStore.currentResult = resultStore.default_dataview;
        }
    }, { immediate: true, deep: true });

    async function handleChooseResult(key: string){
        console.log("@@@@@@@currentTypeDataID[key]", resultStore.currentTypeDataID[key])
        resultStore.currentResult = await resultStore.getResultCacheContent(resultStore.currentTypeDataID[key]!)
    }

</script>
<template>
    <div :style="{width: '100%',height: '100%'}">
        <div class = "result-control">
            <el-button v-for="key in Object.keys(resultStore.currentTypeDataID)" :key="key" @click="()=>handleChooseResult(key)">{{ key }}</el-button>
        </div>
        <div class = "result-container">
            <!-- 显示loading状态 -->
            <div v-if="resultStore.loading" class="loading-container">
                <Loading :active="true" :size="50" />
            </div>
            <!-- 显示结果内容 -->
            <div class="if-result" v-else-if="resultStore.currentResult !== resultStore.default_dataview">
                <TableView v-if="resultStore.currentResult.type === 'Table'"
                            :value="resultStore.currentResult.value"
                            class = "view-content chart-view">
                </TableView>
                <FileView  v-else-if="resultStore.currentResult.type === 'File'"
                            :value="resultStore.currentResult.value"
                            class = "view-content file-view">
                </FileView>
                <ValueView v-else-if="resultStore.currentResult.type === 'int'
                            || resultStore.currentResult.type  === 'str'
                            || resultStore.currentResult.type  === 'bool'
                            || resultStore.currentResult.type  === 'float'
                            || resultStore.currentResult.type  === 'Datetime'"
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
        color: grey;
        padding: 20px;
        padding-top: 10px;
        border-radius: 10px;
        position: relative; /* 添加相对定位 */
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
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
    }
</style>