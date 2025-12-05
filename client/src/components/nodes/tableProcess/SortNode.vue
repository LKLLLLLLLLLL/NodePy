<template>
    <div class="SortNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="tableProcess">表格排序节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="sort_cols">
                <div class="param-description" :class="{'node-has-paramerr': sort_colsHasErr.value}">
                    排序列名
                </div>
                <NodepyMultiSelectMany
                    :options="sort_colsHint"
                    :default-selected="defaultSelectedSort_cols"
                    @select-change="onSelectChangeSort_cols"
                    @clear-select="clearSelectSort_cols"
                    class="nodrag"
                />
            </div>
            <div class="ascending" v-for="(value, idx) in ascending">
                <NodepyBoolValue
                    v-model="value.value"
                    @update-value="onUpdateValue(idx)"
                    width="20px"
                    height="20px"
                >
                    <div class="ascending-item">
                        是否升序
                        <span :class="{'special-table-column': isSpecialColumn(data.param.sort_cols[idx])}">
                            {{displayColumnName(data.param.sort_cols[idx])}}
                        </span>
                    </div>
                </NodepyBoolValue>
            </div>
            <div class="output-sorted_table port">
                <div class="output-port-description">
                    表格输出
                </div>
                <Handle id="sorted_table" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': sorted_tableHasErr}]"/>
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
    import NodepyBoolValue from '../tools/Nodepy-boolValue.vue'
    import { displayColumnName, isSpecialColumn } from '../tableColumnDisplay'
    import type { SortNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<SortNodeData>>()
    const sort_colsHint = computed(() => {
        if(props.data.hint?.sort_col_choices?.length === 0) return ['']
        return props.data.hint?.sort_col_choices || ['']
    })
    const sort_cols = ref(props.data.param.sort_cols)   //  used for defaultSelectedSort_cols
    const defaultSelectedSort_cols = computed(() => {
        const hintArray = sort_colsHint.value
        const selectedArray = sort_cols.value
        return selectedArray.map(item => hintArray.indexOf(item)).filter(idx => idx !== -1)
    })
    const ascending = ref<{value: boolean}[]>(props.data.param.ascending.map(value => ({value})))
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['sorted_table']?.type || 'default')
    const sorted_tableHasErr = computed(() => handleOutputError(props.id, 'sorted_table'))
    const errMsg = ref<string[]>([])
    const sort_colsHasErr = ref({
        id: 'sort_cols',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })


    const onSelectChangeSort_cols = (e: any) => {
        props.data.param.sort_cols = e.map((idx: number) => sort_colsHint.value[idx])
        ascending.value = e.map(() => ({value: true}))
        props.data.param.ascending = ascending.value.map(obj => obj.value)
    }
    const clearSelectSort_cols = (resolve: any) => {
        props.data.param.sort_cols = []
        sort_cols.value = props.data.param.sort_cols
        ascending.value = []
        props.data.param.ascending = []
        resolve()
    }
    const onUpdateValue = (idx: number) => {
        props.data.param.ascending[idx] = ascending.value[idx]!.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, sort_colsHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .SortNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .sort_cols, .ascending {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
            .ascending {
                display: flex;
                align-items: center;
                :deep(.NodePyBoolValueLayout) {
                    flex: 1;
                    min-width: 0;
                    .label {
                        flex: 1;
                        min-width: 0;
                        .ascending-item {
                            display: block;
                            width: 100%;
                            white-space: nowrap;
                            overflow: hidden;
                            text-overflow: ellipsis;
                        }
                    }
                }
            }   // display '...' when the text is too long
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>