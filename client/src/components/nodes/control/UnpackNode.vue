<template>
    <div class="UnpackNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='control'>解包</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-row port">
                <div class="input-port-description">
                    表格行
                </div>
                <Handle id="row" type="target" :position="Position.Left" :class="[`${row_type}-handle-color`, {'node-errhandle': rowHasErr.value}]"/>
            </div>
            <div class="cols">
                <div class="param-description" :class="{'node-has-paramerr': colsHasErr.value}">
                    解包列
                </div>
                <NodepyMultiSelectMany
                    :options="colsHint"
                    :default-selected="defaultSelectedCols"
                    @select-change="onSelectChange"
                    @clear-select="clearSelectCols"
                    class="nodrag"
                />
            </div>
            <div class="output-unpacked_row port">
                <div class="output-port-description">
                    剩余列
                </div>
                <Handle id="unpacked_row" type="source" :position="Position.Right" :class="[`${unpacked_rowSchema_type}-handle-color`, {'node-errhandle': unpacked_rowHasErr}]"/>
            </div>
            <div class="output-col port" v-for="(col, idx) in data.param.cols" :key="col" :class="{'not-last-col' : idx !== data.param.cols.length - 1}">
                <div class="output-port-description col-description">
                    <span :class="{'special-table-column': isSpecialColumn(col)}">
                        {{displayColumnName(col)}}
                    </span>
                </div>
                <Handle :id="`${col}`" type="source" :position="Position.Right" :class="[`${colsSchema_type[idx]}-handle-color`, {'node-errhandle': outputColsHasErr[idx]}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import {ref, computed, watch} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle, useVueFlow } from '@vue-flow/core'
    import { getInputType } from '../getInputType'
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepyMultiSelectMany from '../tools/Nodepy-multiSelectMany.vue'
    import { displayColumnName, isSpecialColumn } from '../tableColumnDisplay'
    import type { UnpackNodeData } from '@/types/nodeTypes'


    const {removeEdges} = useVueFlow()
    const props = defineProps<NodeProps<UnpackNodeData>>()
    const colsHint = computed(() => {
        if(props.data.hint?.cols_choices?.length === 0) return ['']
        return props.data.hint?.cols_choices || ['']
    })
    const defaultSelectedCols = ref(props.data.param.cols.map(item => colsHint.value.indexOf(item)).filter(idx => idx !== -1))
    const row_type = computed(() => getInputType(props.id, 'row'))
    const unpacked_rowSchema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['unpacked_row']?.type || 'default')
    const unpacked_rowHasErr = computed(() => handleOutputError(props.id, 'unpacked_row'))
    const colsSchema_type = computed(():(server__models__schema__Schema__Type|'default')[] => {
        return props.data.param.cols.map(item => props.data.schema_out?.[item]?.type || 'default')
    })
    const outputColsHasErr = computed(() => {
        return props.data.param.cols.map(item => handleOutputError(props.id, item))
    })
    const errMsg = ref<string[]>([])
    const colsHasErr = ref({
        id: 'cols',
        value: false
    })
    const rowHasErr = ref({
        handleId: 'row',
        value: false
    })


    const onSelectChange = (e: number[]) => {
        const selectedCols = e.map(i => colsHint.value[i])
        removeEdges(edges => edges.filter(e => e.source === props.id && (!selectedCols.includes(e.sourceHandle))))
        props.data.param.cols = selectedCols
    }
    const clearSelectCols = (resolve: any) => {
        removeEdges(edges => edges.filter(e => e.source === props.id && e.sourceHandle !== 'unpacked_row'))
        props.data.param.cols = []
        defaultSelectedCols.value = []
        resolve()
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, colsHasErr)
        handleValidationError(props.id, props.data.error, errMsg, rowHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .UnpackNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-row {
                margin-bottom: $node-margin;
            }
            .cols {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
            .output-unpacked_row, .output-col.not-last-col {
                margin-bottom: $node-margin;
            }
            .output-col {
                .col-description {
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;                    
                }
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>