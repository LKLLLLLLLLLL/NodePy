<script lang="ts" setup>

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

    // 每个标签对应的类型标签与颜色信息
    const tabMeta = ref<Record<string, { label: string; type: string; color: string }>>({});

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
                tabMeta.value = {};
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

            // 异步为所有标签读取类型信息，用于在标签上显示小徽章
            const typeColorMap: Record<string, string> = {
                'int': '#1c6bbf',
                'float': '#ecbc00',
                'str': '#10b981',
                'Table': 'pink',
                'File': '#f97316',
                'bool': '#77b021',
                'Datetime': '#00c8ff',
                'Model': '#9f03c2'
            };

            const typeLabelMap: Record<string, string> = {
                'Table': '表格',
                'File': '文件',
                'int': '整数',
                'str': '字符串',
                'bool': '布尔',
                'float': '浮点',
                'Datetime': '时间',
                'Model': '模型'
            };

            const metaPromises = Object.keys(newTypeDataID).map(async (k) => {
                const id = newTypeDataID[k];
                try {
                    if (typeof id === 'number' && !isNaN(id)) {
                        const r = await resultStore.getResultCacheContent(id);
                        const t = r?.type || '';
                        const label = typeLabelMap[t] || t || '';
                        const color = typeColorMap[t] || '#9b9b9b';
                        tabMeta.value[k] = { label, type: t, color };
                    } else {
                        tabMeta.value[k] = { label: '', type: '', color: '#9b9b9b' };
                    }
                } catch (e) {
                    tabMeta.value[k] = { label: '', type: '', color: '#9b9b9b' };
                }
            });
            await Promise.all(metaPromises);

        } catch (error) {
            console.error('Result: 加载结果失败:', error);
            resultStore.currentInfo = graphStore.currentNode?.data?.param || {};
            resultStore.currentResult = resultStore.default_dataview;
            activeTab.value = ''; // 出错时重置激活的标签页
        }
    }, { immediate: true, deep: true });

    async function handleChooseResult(key: string){
        activeTab.value = key;
        // 点击切换时确保当前结果和当前info也被设置
        const id = resultStore.currentTypeDataID[key]!;
        if (typeof id === 'number') {
            resultStore.currentResult = await resultStore.getResultCacheContent(id);
        }
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
                    @click="handleChooseResult(key)"
                    role="tab"
                    :aria-selected="activeTab === key ? 'true' : 'false'"
                    :title="(key[0]!.toUpperCase() + key.slice(1)) + (tabMeta[key]?.label ? ' — ' + tabMeta[key].label : '')"
                    :style="{ '--type-color': tabMeta[key]?.color || '#9b9b9b' }"
                >
                    <span class="tab-title">{{ key[0]!.toUpperCase() + key.slice(1) }}</span>
                    <span class="tab-badge" v-if="tabMeta[key]">{{ tabMeta[key].label }}</span>
                </button>
            </div>
        </div>
        <!-- 结果类型现在显示在每个标签上 -->
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
            <!-- <div class="no-result-prompt" v-else>
                <div class="prompt-content">
                    <p>当前节点无结果，请检查节点输入或双击其他节点</p>
                </div>
            </div> -->
            <!-- <div class="if-info" v-if="resultStore.currentInfo!=resultStore.default_info">
                <NodeInfo :data="resultStore.currentInfo">
                </NodeInfo>
            </div> -->
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
        padding: 15px;
        padding-top: 0px;
        box-sizing: border-box;
    }

    .result-container{
        display: flex;
        width: 100%;
        // height: calc(100% - 70px); /* 调整高度以适应标签页和类型显示 */
        color: grey;
        padding: 0;
        border-radius: 8px;
        // border: 1px solid #e0e0e0;
        // box-shadow: 0px 1px 20px rgba(128, 128, 128, 0.3);
        position: relative;
        overflow: hidden;
        flex: 1;
        background: white; /* 确保有背景色，否则阴影可能看起来奇怪 */
    }

    .result-control {
        height: 54px;
        display: flex;
        align-items: center;
        padding: 0; /* 取消默认内边距，让标签紧贴左侧 */
        margin-bottom: 4px; /* 增加一点下边距，与内容区隔开 */
    }

    .result-control .tab-list {
        display: flex;
        gap: 10px; /* 增加标签间距，避免阴影重叠 */
        margin: 0; /* 左对齐 */
        align-items: flex-start; /* 顶部对齐 */
        justify-content: flex-start;
        overflow-x: auto;
        overflow-y: hidden; /* 避免垂直滚动 */
        height: 100%; /* 固定高度 */
        box-sizing: border-box;
        padding: 8px 0px 0px 0px;
        scrollbar-gutter: stable;
    }

    .result-control .tab-item {
        height: 34px;
        font-size: 13px; /* 缩小字体 */
        font-weight: bold;
        color: rgba(20,20,20,0.9);
        padding: 6px 8px;
        transition: all 0.18s ease;
        min-width: 90px;
        max-width: 220px;
        text-align: center;
        border-radius: 18px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        justify-content: center;
        // background: transparent;
        border: none;
        cursor: pointer;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        // box-shadow: 0px 3px 7px rgba(128, 128, 128, 0.14);
        background-color: white;
    }

    .result-control .tab-item:hover {
        background-color: rgba(0, 0, 0, 0.06);
        // color: $stress-color;
    }

    .result-control .tab-item.active {
        color: #ffffff;
        background-color: $stress-color;
        box-shadow: 0px 3px 5px rgba(128, 128, 128, 0.2);
    }

    .result-control .tab-item .tab-title{
        display: inline-block;
        max-width: 110px;
        min-width: auto;
        overflow: hidden;
        text-overflow: ellipsis;
        vertical-align: middle;
    }

    .result-control .tab-item .tab-badge{
        display: inline-block;
        font-size: 11px;
        color: white;
        background: var(--type-color, rgba(0,0,0,0.06));
        padding: 2px 8px;
        border-radius: 12px;
        line-height: 1;
        vertical-align: middle;
        opacity: 0.95;
    }

    .result-control .tab-item:focus {
        outline: none;
    }

    /* Hide scrollbar but keep scrollability */
    .result-control .tab-list::-webkit-scrollbar {
        height: 6px;
    }
    .result-control .tab-list::-webkit-scrollbar-thumb {
        background: rgba(0,0,0,0.08);
        border-radius: 3px;
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

    /* 结果类型现在在标签上显示，不需要独立容器样式 */

    .if-result{
        flex: 1;
        // margin-top: 10px;
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
