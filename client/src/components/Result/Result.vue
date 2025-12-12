<script lang="ts" setup>
    import type { ResultType } from '@/stores/resultStore';
    import TableView from './TableView.vue';
    import FileView from './FileView.vue';
    import ValueView from './ValueView.vue';
    import ModelView from './ModelView.vue';
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
    const tabKeys = computed(() => {
        // 如果是默认的无结果状态，返回空数组以显示"无结果"提示
        if (resultStore.currentTypeDataID === resultStore.default_typedataid) {
            return [];
        }
        return Object.keys(resultStore.currentTypeDataID);
    });

    // 计算是否处于无结果状态
    const isNoResult = computed(() => {
        return resultStore.currentTypeDataID === resultStore.default_typedataid ||
               resultStore.currentResult === resultStore.default_dataview;
    });

    // 计算当前结果类型的中文标签
    const currentResultTypeLabel = computed(() => {
        if (!resultStore.currentResult || !resultStore.currentResult.type) return '';

        const typeLabels: Record<string, string> = {
            'Table': '表格',
            'File': '文件',
            'int': '整数',
            'str': '字符串',
            'bool': '布尔值',
            'float': '浮点数',
            'Datetime': '日期时间'
        };

        return typeLabels[resultStore.currentResult.type] || resultStore.currentResult.type;
    });

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
        <!-- 标签控制栏 -->
        <div v-if="isNoResult" class="result-control no-result-control">
            无结果
        </div>
        <div v-else-if="tabKeys.length > 0" class="result-control">
            <div class="tab-list" role="tablist">
                <button
                    v-for="key in tabKeys"
                    :key="key"
                    class="tab-item"
                    :class="{ active: activeTab === key }"
                    @click="() => handleChooseResult(key)"
                    role="tab"
                    :aria-selected="activeTab === key ? 'true' : 'false'"
                >
                    {{ key[0]!.toUpperCase() + key.slice(1) }}
                </button>
            </div>
        </div>
        <!-- 结果类型显示区域 -->
        <div class="result-type-container" v-if="currentResultTypeLabel && !isNoResult">
            当前结果类型: {{ currentResultTypeLabel }}
        </div>
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
                    <ModelView v-else-if="resultStore.currentResult.type === 'Model'"
                                :value="resultStore.currentResult.value"
                                class = "view-content model-view">
                    </ModelView>
                </div>
            </div>
            <!-- 无结果提示 -->
            <div class="no-result-prompt" v-else>
                <div class="prompt-content">
                    <p>当前节点无结果，请检查节点输入或双击其他节点</p>
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
@use '../../common/global.scss' as *;

    .result-total-container{
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 100%;
        flex: 1;
    }

    .result-container{
        display: flex;
        width: 100%;
        // height: calc(100% - 70px); /* 调整高度以适应标签页和类型显示 */
        color: grey;
        padding: 0;
        // border-radius: 10px;
        position: relative;
        overflow: hidden;
        flex: 1;
    }

    .result-control {
        height: 40px; /* match nav bar height */
        display: flex;
        align-items: center;
        padding: 0 12px;
    }

    .result-control .tab-list {
        display: flex;
        gap: 6px;
        margin: 0; /* 左对齐 */
        align-items: center;
        justify-content: flex-start;
    }

    .result-control .tab-item {
        height: 30px;
        font-weight: 700;
        color: rgba(40, 40, 40, 0.76);
        padding: 9px 15px;
        transition: all 0.18s ease;
        min-width: 120px;
        text-align: center;
        border-radius: 20px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: transparent;
        border: none;
        cursor: pointer;
    }

    .result-control .tab-item:hover {
        background-color: rgba(0, 0, 0, 0.06);
        color: $stress-color;
    }

    .result-control .tab-item.active {
        border-radius: 19px;
        color: #ffffff; /* white text for emphasis */
        background-color: $stress-color; /* emphasized background */
        box-shadow: 0px 3px 6px rgba(16, 142, 254, 0.12);
        font-weight: 600;
    }

    // 无结果时的标签栏样式
    .no-result-control {
        height: 40px;
        line-height: 40px;
        padding: 0 15px;
        font-size: 14px;
        color: #999;
        background-color: #f5f7fa;
        border-bottom: 1px solid #e4e7ed;
        font-weight: 500;
    }

    .result-type-container {
        height: 30px;
        line-height: 30px;
        padding: 0 15px;
        font-size: 14px;
        color: #666;
        background-color: #f5f7fa;
        border-bottom: 1px solid #e4e7ed;
    }

    .if-result{
        flex: 1;
        margin-top: 10px;
        margin-left: 0;
        // border-radius: 10px;
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
        // border-radius: 10px;
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

    // 无结果提示样式
    .no-result-prompt {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        height: 100%;
        background-color: #fafafa;
        border-radius: 10px;
    }

    .prompt-content {
        text-align: center;
        color: #999;

        p {
            font-size: 16px;
            margin: 0;
        }
    }
</style>
