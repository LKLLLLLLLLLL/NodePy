<template>
    <div class="GroupNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="tableProcess">表格分组节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="group_cols">
                <div class="param-description" :class="{'node-has-paramerr': group_colsHasErr.value}">
                    分组列名
                </div>
                <NodepyMultiSelectMany
                    :options="group_colsHint"
                    :default-selected="defaultSelectedGroup_cols"
                    @select-change="onSelectChangeGroup_cols"
                    @clear-select="clearSelectGroup_cols"
                    class="nodrag"
                />
            </div>
            <div class="agg_cols">
                <div class="param-description" :class="{'node-has-paramerr': agg_colsHasErr.value}">
                    聚合列名
                </div>
                <NodepyMultiSelectMany
                    :options="agg_colsHint"
                    :default-selected="defaultSelectedAgg_cols"
                    @select-change="onSelectChangeAgg_cols"
                    @clear-select="clearSelectAgg_cols"
                    class="nodrag"
                />
            </div>
            <div class="agg_func">
                <div class="param-description" :class="{'node-has-paramerr': agg_funcHasErr.value}">
                    聚合函数
                </div>
                <NodepySelectMany
                    :options="agg_funcUi"
                    :default-selected="defaultSelectedAgg_func"
                    @select-change="onSelectChangeAgg_func"
                    class="nodrag"
                />
            </div>
            <div class="output-grouped_table port">
                <div class="output-port-description">
                    表格输出
                </div>
                <Handle id="grouped_table" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': grouped_tableHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import {ref, computed, watch} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import { getInputType } from '../getInputType'
    import type { Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepyMultiSelectMany from '../tools/Nodepy-multiSelectMany.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import type { GroupNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<GroupNodeData>>()
    const group_colsHint = computed(() => {
        if(props.data.hint?.group_col_choices?.length === 0) return ['']
        return props.data.hint?.group_col_choices || ['']
    })
    const group_cols = ref(props.data.param.group_cols)   //  used for defaultSelectedGroup_cols
    const defaultSelectedGroup_cols = computed(() => {
        const hintArray = group_colsHint.value
        const selectedArray = group_cols.value
        return selectedArray.map(item => hintArray.indexOf(item)).filter(idx => idx !== -1)
    })
    const agg_colsHint = computed(() => {
        if(props.data.hint?.agg_col_choices?.length === 0) return ['']
        return props.data.hint?.agg_col_choices || ['']
    })
    const agg_cols = ref(props.data.param.agg_cols)   //  used for defaultSelectedAgg_cols
    const defaultSelectedAgg_cols = computed(() => {
        const hintArray = agg_colsHint.value
        const selectedArray = agg_cols.value
        return selectedArray.map(item => hintArray.indexOf(item)).filter(idx => idx !== -1)
    })
    const agg_func = ["SUM", "MEAN", "COUNT", "MAX", "MIN", "STD"]
    const agg_funcUi = ["求和", "平均值", "计数", "最大值", "最小值", "标准差"]
    const defaultSelectedAgg_func = agg_func.indexOf(props.data.param.agg_func)
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['grouped_table']?.type || 'default')
    const grouped_tableHasErr = computed(() => handleOutputError(props.id, 'grouped_table'))
    const errMsg = ref<string[]>([])
    const group_colsHasErr = ref({
        id: 'group_cols',
        value: false
    })
    const agg_colsHasErr = ref({
        id: 'agg_cols',
        value: false
    })
    const agg_funcHasErr = ref({
        id: 'agg_func',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })


    const onSelectChangeGroup_cols = (e: any) => {
        props.data.param.group_cols = e.map((idx: number) => group_colsHint.value[idx])
    }
    const clearSelectGroup_cols = (resolve: any) => {
        props.data.param.group_cols = []
        group_cols.value = props.data.param.group_cols
        resolve()
    }
    const onSelectChangeAgg_cols = (e: any) => {
        props.data.param.agg_cols = e.map((idx: number) => agg_colsHint.value[idx])
    }
    const clearSelectAgg_cols = (resolve: any) => {
        props.data.param.agg_cols = []
        agg_cols.value = props.data.param.agg_cols
        resolve()
    }
    const onSelectChangeAgg_func = (e: any) => {
        const selected_agg_func = agg_func[e] as 'SUM'|'MEAN'|'COUNT'|'MAX'|'MIN'|'STD'
        props.data.param.agg_func = selected_agg_func
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, group_colsHasErr, agg_colsHasErr, agg_funcHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .GroupNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .group_cols, .agg_cols, .agg_func {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>