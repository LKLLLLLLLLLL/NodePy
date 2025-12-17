<template>
    <div class="SortNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="tableProcess">排序</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="sort_col">
                <div class="param-description" :class="{'node-has-paramerr': sort_colHasErr.value}">
                    排序列
                </div>
                <NodepySelectMany
                    :options="sort_colHint"
                    :default-selected="defaultSelectedSort_col"
                    @select-change="onSelectChangeSort_col"
                    @clear-select="clearSelectSort_col"
                    class="nodrag"
                />
            </div>
            <div class="ascending">
                <NodepyBoolValue
                    v-model="ascending"
                    @update-value="onUpdateAscending"
                    width="20px"
                    height="20px"
                >
                    升序
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
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import NodepyBoolValue from '../tools/Nodepy-boolValue.vue'
    import type { SortNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<SortNodeData>>()
    const sort_colHint = computed(() => {
        if(props.data.hint?.sort_col_choices?.length === 0) return ['']
        return props.data.hint?.sort_col_choices || ['']
    })
    const sort_col = ref(props.data.param.sort_col)   //  used for defaultSelectedSort_col
    const defaultSelectedSort_col = computed(() => sort_colHint.value.indexOf(sort_col.value))
    const ascending = ref(props.data.param.ascending)
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['sorted_table']?.type || 'default')
    const sorted_tableHasErr = computed(() => handleOutputError(props.id, 'sorted_table'))
    const errMsg = ref<string[]>([])
    const sort_colHasErr = ref({
        id: 'sort_col',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })


    const onSelectChangeSort_col = (e: any) => {
        props.data.param.sort_col = sort_colHint.value[e]
    }
    const clearSelectSort_col = (resolve: any) => {
        props.data.param.sort_col = ''
        sort_col.value = props.data.param.sort_col
        resolve()
    }
    const onUpdateAscending = () => {
        props.data.param.ascending = ascending.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, sort_colHasErr)
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
            .sort_col, .ascending {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>
