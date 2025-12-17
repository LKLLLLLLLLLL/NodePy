<template>
    <div class="DropNaNValueNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="tableProcess">删除缺失值</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="subset_cols">
                <div class="param-description" :class="{'node-has-paramerr': subset_colsHasErr.value}">
                    选中列
                </div>
                <NodepyMultiSelectMany
                    :options="subset_colsHint"
                    :default-selected="defaultSelectedSubset_cols"
                    @select-change="onSelectChangeSubset_cols"
                    @clear-select="clearSelectSubset_cols"
                    class="nodrag"
                />
            </div>
            <div class="output-cleaned_table port">
                <div class="output-port-description">
                    表格输出
                </div>
                <Handle id="cleaned_table" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': cleaned_tableHasErr}]"/>
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
    import NodepyMultiSelectMany from '../tools/Nodepy-multiSelectMany.vue'
    import type { DropNaNValueNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<DropNaNValueNodeData>>()
    const subset_colsHint = computed(() => {
        if(props.data.hint?.subset_col_choices?.length === 0) return ['']
        return props.data.hint?.subset_col_choices || ['']
    })
    const subset_cols = ref(props.data.param.subset_cols)   //  used for defaultSelectedSubset_cols
    const defaultSelectedSubset_cols = computed(() => {
        const hintArray = subset_colsHint.value
        const selectedArray = subset_cols.value
        return selectedArray.map(item => hintArray.indexOf(item)).filter(idx => idx !== -1)
    })
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['cleaned_table']?.type || 'default')
    const cleaned_tableHasErr = computed(() => handleOutputError(props.id, 'cleaned_table'))
    const errMsg = ref<string[]>([])
    const subset_colsHasErr = ref({
        id: 'subset_cols',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })


    const onSelectChangeSubset_cols = (e: any) => {
        props.data.param.subset_cols = e.map((idx: number) => subset_colsHint.value[idx])
    }
    const clearSelectSubset_cols = (resolve: any) => {
        props.data.param.subset_cols = []
        subset_cols.value = props.data.param.subset_cols
        resolve()
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, subset_colsHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .DropNaNValueNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .subset_cols {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>
