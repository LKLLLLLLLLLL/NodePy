<script lang="ts" setup>
    import type { ResultType } from '@/stores/resultStore';
    import TableView from './TableView.vue';
    import FileView from './FileView.vue';
    import ValueView from './ValueView.vue';
    import NodeInfo from './NodeInfo.vue';
    import Loading from '../Loading.vue'; // 引入Loading组件
    import { watch, ref, computed, onMounted, onUnmounted } from 'vue';
    import { useResultStore } from '@/stores/resultStore';
    import { useGraphStore } from '@/stores/graphStore';

    const resultStore = useResultStore();
    const graphStore = useGraphStore();

    // 当前激活的标签页
    const activeTab = ref('');

    // 计算标签页数据
    const tabKeys = computed(() => Object.keys(resultStore.currentTypeDataID));

    // 监听窗口大小变化
    const handleWindowResize = () => {
        // 触发resultStore中的窗口大小变化处理
        resultStore['handleWindowResize']?.();
    };

    // 组件挂载时添加事件监听器
    onMounted(() => {
        window.addEventListener('resize', handleWindowResize);
    });

    // 组件卸载时移除事件监听器
    onUnmounted(() => {
        window.removeEventListener('resize', handleWindowResize);
    });

    // 监听currentTypeDataID字典变化
    watch(() => resultStore.currentTypeDataID, async (newTypeDataID, oldTypeDataID) => {
        try {
            if(newTypeDataID === resultStore.default_typedataid){
                resultStore.currentResult = resultStore.default_dataview
                resultStore.currentInfo = resultStore.default_info
                activeTab.value = ''; // 重置激活的标签页
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
                    
                    // 设置默认选中的标签页为第一个
                    activeTab.value = firstKey;
                    handleChooseResult(firstKey);
                }
            }
            
        } catch (error) {
            console.error('Result: 加载结果失败:', error);
            resultStore.currentInfo = graphStore.currentNode?.data?.param || {};
            resultStore.currentResult = resultStore.default_dataview;
            activeTab.value = ''; // 出错时重置激活的标签页
        }
    }, { immediate: true, deep: true });

    async function handleChooseResult(key: string){
        activeTab.value = key;
        resultStore.currentResult = await resultStore.getResultCacheContent(resultStore.currentTypeDataID[key]!)
    }

</script>
<template>
    <div class="result-total-container">
        <el-tabs 
            v-if="tabKeys.length > 0" 
            v-model="activeTab" 
            @tab-click="(tab) => handleChooseResult(tab.props.name)" 
            class="result-control"
        >
            <el-tab-pane 
                v-for="key in tabKeys" 
                :key="key" 
                :label="key[0]!.toUpperCase() + key.slice(1)" 
                :name="key">
            </el-tab-pane>
        </el-tabs>
        <div class = "result-container">
            <!-- 显示loading状态 -->
            <div v-if="resultStore.loading" class="loading-container">
                <Loading :active="true" :size="50" />
            </div>
            <!-- 显示结果内容 -->
            <div class="if-result" v-else-if="resultStore.currentResult !== resultStore.default_dataview">
                <div class="view-content-wrapper">
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
            </div>
            <div class="if-info" v-if="resultStore.currentInfo!=resultStore.default_info">
                <NodeInfo :data="resultStore.currentInfo">
                </NodeInfo>
            </div>
        </div>
    </div>
</template>
<style lang = "scss" scoped>
    .result-total-container{
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 100%;
    }

    .result-container{
        display: flex;
        width: 100%;
        height: calc(100% - 40px); /* 调整高度以适应标签页 */
        color: grey;
        padding: 0;
        border-radius: 10px;
        position: relative;
        overflow: hidden;
    }

    .result-control {
        height: 40px; /* 增加高度以适应标签页 */
        :deep(.el-tabs__header) {
            margin: 0;
        }
        
        :deep(.el-tabs__nav-wrap)::after {
            height: 1px;
        }
        
        :deep(.el-tabs__item) {
            height: 40px;
            line-height: 40px;
            font-weight: 500;
            color: #666;
            transition: all 0.3s ease;
        }
        
        :deep(.el-tabs__item:hover) {
            color: #409eff;
        }
        
        :deep(.el-tabs__item.is-active) {
            color: #409eff;
            font-weight: 600;
        }
        
        :deep(.el-tabs__active-bar) {
            background-color: #409eff;
            transition: all 0.3s ease;
        }
    }

    .if-result{
        flex: 1;
        margin-top: 10px;
        margin-left: 0;
        border-radius: 10px;
        overflow: hidden;
        background: transparent;
    }

    .view-content-wrapper {
        width: 100%;
        height: 100%;
        overflow: auto;
    }

    .view-content{
        width: 100%;
        min-height: 100%;
        border-radius: 10px;
    }
    
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        width: 100%;
        position: absolute;
        top: 0;
        left: 0;
        background: rgba(255, 255, 255, 0.8);
        z-index: 10;
    }
</style>