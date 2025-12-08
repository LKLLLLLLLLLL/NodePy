<template>
    <div class="FilterNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="tableProcess">表格过滤节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="cond_col">
                <div class="param-description" :class="{'node-has-paramerr': cond_colHasErr.value}">
                    过滤参照列名
                </div>
                <NodepySelectMany
                    :options="cond_colHint"
                    :default-selected="defaultSelectedCond_col"
                    @select-change="onSelectChangeCond_col"
                    @clear-select="clearSelectCond_col"
                    class="nodrag"
                />
            </div>
            <div class="output-true_table port">
                <div class="output-port-description">
                    True表格输出
                </div>
                <Handle id="true_table" type="source" :position="Position.Right" :class="[`${true_table_schema_type}-handle-color`, {'node-errhandle': true_tableHasErr}]"/>
            </div>
            <div class="output-false_table port">
                <div class="output-port-description">
                    False表格输出
                </div>
                <Handle id="false_table" type="source" :position="Position.Right" :class="[`${false_table_schema_type}-handle-color`, {'node-errhandle': false_tableHasErr}]"/>
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
    import type { FilterNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<FilterNodeData>>()
    const cond_colHint = computed(() => {
        if(props.data.hint?.cond_col_choices?.length === 0) return ['']
        return props.data.hint?.cond_col_choices || ['']
    })
    const cond_col = ref(props.data.param.cond_col)   //  used for defaultSelectedCond_col
    const defaultSelectedCond_col = computed(() => cond_colHint.value.indexOf(cond_col.value))
    const table_type = computed(() => getInputType(props.id, 'table'))
    const true_table_schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['true_table']?.type || 'default')
    const false_table_schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['false_table']?.type || 'default')
    const true_tableHasErr = computed(() => handleOutputError(props.id, 'true_table'))
    const false_tableHasErr = computed(() => handleOutputError(props.id, 'false_table'))
    const errMsg = ref<string[]>([])
    const cond_colHasErr = ref({
        id: 'cond_col',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })


    const onSelectChangeCond_col = (e: any) => {
        props.data.param.cond_col = cond_colHint.value[e]
    }
    const clearSelectCond_col = (resolve: any) => {
        props.data.param.cond_col = ''
        cond_col.value = props.data.param.cond_col
        resolve()
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, cond_colHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .FilterNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .cond_col {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
            .output-true_table {
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>
