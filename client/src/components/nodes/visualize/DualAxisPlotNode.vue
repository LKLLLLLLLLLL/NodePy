<template>
    <div class="DualAxisPlotNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="visualize">双轴绘图节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">表格输入</div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': tableHasErr.value}]"/>
            </div>
            <div class="title">
                <div class="param-description">图像标题</div>
                <NodepyStringInput :allow-null="true" v-model="title" @update-value="() => updateSimpleStringNumberBoolValue(data.param, 'title', title)" class="nodrag" placeholder="图像标题"/>
            </div>
            <div class="x_col">
                <div class="param-description" :class="{'node-has-paramerr': x_colHasErr.value}">x轴列名</div>
                <NodepySelectMany
                :options="x_col_hint"
                :default-selected="x_col_default_selected"
                @select-change="onUpdateX_col"
                @clear-select="clearSelectX"
                class="nodrag"
                />
            </div>
            <div class="left_y_cols"v-for="(left_y_col, idx) in left_y_cols" :key="left_y_col.id">
                <div class="left_y_col">
                    <hr style="margin-bottom: 4px;"></hr>
                    <div class="param-description left_y_col-description" :class="{'node-has-paramerr': left_y_colHasErr.value}">
                        <span class="left-y-col-label">左y轴列名 {{ idx + 1 }}</span>
                        <NodepyCross v-if="left_y_cols.length > 1" :handle-click="() => removeLeft_y_col(idx)" class="left-y-col-close"/>
                    </div>
                    <NodepySelectMany
                    :options="left_y_col_hint"
                    :default-selected="left_y_col.defaultSelected"
                    @select-change="(e: any) => onUpdateLeft_y_col(e, idx)"
                    @clear-select="(e: any) => clearSelectLeft_y_col(e, idx)"
                    class="nodrag"
                    />
                </div>
                <div class="left_plot_type">
                    <div class="param-description" :class="{'node-has-paramerr': left_plot_typeHasErr.value}">图形类型</div>
                    <NodepySelectFew
                        :options="plot_type_options_chinese"
                        :default-selected="left_y_col.defaultSelectedPlot_type"
                        @select-change="(e: any) => onSelectChangeLeft_plot_type(e, idx)"
                        class="nodrag"
                    />
                </div>
            </div>
            <div class="addLeft_y_col">
                <hr style="margin: 8px 0;"></hr>
                <NodepyButton :handle-click="addLeft_y_col">
                    <NodepyPlus/>
                    添加左y轴
                </NodepyButton>
            </div>
            <div class="right_y_cols"v-for="(right_y_col, idx) in right_y_cols" :key="right_y_col.id">
                <div class="right_y_col">
                    <hr style="margin-bottom: 4px;"></hr>
                    <div class="param-description right_y_col-description" :class="{'node-has-paramerr': right_y_colHasErr.value}">
                        <span class="right-y-col-label">右y轴列名 {{ idx + 1 }}</span>
                        <NodepyCross v-if="right_y_cols.length > 1" :handle-click="() => removeRight_y_col(idx)" class="right-y-col-close"/>
                    </div>
                    <NodepySelectMany
                    :options="right_y_col_hint"
                    :default-selected="right_y_col.defaultSelected"
                    @select-change="(e: any) => onUpdateRight_y_col(e, idx)"
                    @clear-select="(e: any) => clearSelectRight_y_col(e, idx)"
                    class="nodrag"
                    />
                </div>
                <div class="right_plot_type">
                    <div class="param-description" :class="{'node-has-paramerr': right_plot_typeHasErr.value}">图形类型</div>
                    <NodepySelectFew
                        :options="plot_type_options_chinese"
                        :default-selected="right_y_col.defaultSelectedPlot_type"
                        @select-change="(e: any) => onSelectChangeRight_plot_type(e, idx)"
                        class="nodrag"
                    />
                </div>
            </div>
            <div class="addRight_y_col">
                <hr style="margin: 8px 0;"></hr>
                <NodepyButton :handle-click="addRight_y_col">
                    <NodepyPlus/>
                    添加右y轴
                </NodepyButton>
            </div>
            <div class="output-plot port">
                <div class="output-port-description">图像输出</div>
                <Handle id="plot" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': plotHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Handle, Position } from '@vue-flow/core'
    import { computed, ref, watch } from 'vue'
    import { getInputType } from '../getInputType'
    import { handleExecError, handleParamError, handleValidationError, handleOutputError } from '../handleError'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import NodepySelectFew from '../tools/Nodepy-selectFew.vue'
    import NodepyButton from '../tools/Nodepy-button.vue'
    import NodepyCross from '../tools/Nodepy-cross.vue'
    import NodepyPlus from '../tools/Nodepy-plus.vue'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import { updateSimpleStringNumberBoolValue } from '../updateParam'
    import type { DualAxisPlotNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<DualAxisPlotNodeData>>()
    const plot_type_options = ["bar", "line"]
    const plot_type_options_chinese = ['条形图', '折线图']
    const x_col_hint = computed(() => {
        if(props.data.hint?.x_col_choices?.length === 0) return ['']
        return props.data.hint?.x_col_choices || ['']
    })
    const x_col = ref(props.data.param.x_col)   // used for x_col_default_selected
    const x_col_default_selected = computed(() => x_col_hint.value.indexOf(x_col.value))
    const left_y_col_hint = computed(() => {
        if(props.data.hint?.left_y_col_choices?.length === 0) return ['']
        return props.data.hint?.left_y_col_choices || ['']
    })
    const left_y_cols = ref(props.data.param.left_y_col.map((item, idx) => {
        return {
            id: Date.now().toString()+`_${idx}`,
            defaultSelected: left_y_col_hint.value.indexOf(item),
            defaultSelectedPlot_type: [plot_type_options.indexOf(props.data.param.left_plot_type[idx]!)]
        }
    }))
    const right_y_col_hint = computed(() => {
        if(props.data.hint?.right_y_col_choices?.length === 0) return ['']
        return props.data.hint?.right_y_col_choices || ['']
    })
    const right_y_cols = ref(props.data.param.right_y_col.map((item, idx) => {
        return {
            id: Date.now().toString()+`_${idx}`,
            defaultSelected: right_y_col_hint.value.indexOf(item),
            defaultSelectedPlot_type: [plot_type_options.indexOf(props.data.param.right_plot_type[idx]!)]
        }
    }))
    const title = ref(props.data.param.title)
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['plot']?.type || 'default')
    const plotHasErr = computed(() => handleOutputError(props.id, 'plot'))
    const errMsg = ref<string[]>([])
    const tableHasErr = ref({
        handleId: 'table',
        value: false
    })
    const x_colHasErr = ref({
        id: 'x_col',
        value: false
    })
    const left_y_colHasErr = ref({
        id: 'left_y_col',
        value: false
    })
    const right_y_colHasErr = ref({
        id: 'right_y_col',
        value: false
    })
    const left_plot_typeHasErr = ref({
        id: 'left_plot_type',
        value: false
    })
    const right_plot_typeHasErr = ref({
        id: 'right_plot_type',
        value: false
    })



    const onUpdateX_col = (e: any) => {
        props.data.param.x_col = x_col_hint.value[e]
    }
    const clearSelectX = (resolve: any) => {
        props.data.param.x_col = ''
        x_col.value = props.data.param.x_col
        resolve()
    }
    const onSelectChangeLeft_plot_type = (plot_typeIdx: number, y_colsIdx: number) => {
        const selected_plot_type = plot_type_options[plot_typeIdx] as 'line'| 'bar'
        props.data.param.left_plot_type[y_colsIdx] = selected_plot_type
    }
    const onSelectChangeRight_plot_type = (plot_typeIdx: number, y_colsIdx: number) => {
        const selected_plot_type = plot_type_options[plot_typeIdx] as 'line'| 'bar'
        props.data.param.right_plot_type[y_colsIdx] = selected_plot_type
    }
    const onUpdateLeft_y_col = (hintIdx: number, y_colsIdx: number) => {
        props.data.param.left_y_col[y_colsIdx] = left_y_col_hint.value[hintIdx]
    }
    const clearSelectLeft_y_col = (resolve: any, idx: number) => {
        props.data.param.left_y_col[idx] = ''
        props.data.param.left_plot_type[idx] = 'line'
        left_y_cols.value[idx] = {id: Date.now().toString()+`_${idx}`, defaultSelected: -1, defaultSelectedPlot_type: [1]}
        resolve()
    }
    const removeLeft_y_col = (idx: number) => {
        if(left_y_cols.value.length > 1) {
            left_y_cols.value.splice(idx, 1)
            props.data.param.left_y_col.splice(idx, 1)
            props.data.param.left_plot_type.splice(idx, 1)
        }
    }
    const addLeft_y_col = () => {
        left_y_cols.value.push({id: Date.now().toString()+`_${left_y_cols.value.length}`, defaultSelected: -1, defaultSelectedPlot_type: [1]})
        props.data.param.left_y_col.push('')
        props.data.param.left_plot_type.push('line')
    }
    const onUpdateRight_y_col = (hintIdx: number, y_colsIdx: number) => {
        props.data.param.right_y_col[y_colsIdx] = right_y_col_hint.value[hintIdx]
    }
    const clearSelectRight_y_col = (resolve: any, idx: number) => {
        props.data.param.right_y_col[idx] = ''
        props.data.param.right_plot_type[idx] = 'line'
        right_y_cols.value[idx] = {id: Date.now().toString()+`_${idx}`, defaultSelected: -1, defaultSelectedPlot_type: [1]}
        resolve()
    }
    const removeRight_y_col = (idx: number) => {
        if(right_y_cols.value.length > 1) {
            right_y_cols.value.splice(idx, 1)
            props.data.param.right_y_col.splice(idx, 1)
            props.data.param.right_plot_type.splice(idx, 1)
        }
    }
    const addRight_y_col = () => {
        right_y_cols.value.push({id: Date.now().toString()+`_${right_y_cols.value.length}`, defaultSelected: -1, defaultSelectedPlot_type: [1]})
        props.data.param.right_y_col.push('')
        props.data.param.right_plot_type.push('line')
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, x_colHasErr, left_y_colHasErr, left_plot_typeHasErr, right_y_colHasErr, right_plot_typeHasErr)
        handleValidationError(props.id, props.data.error, errMsg, tableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .DualAxisPlotNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .x_col, .left_y_col, .right_y_col, .addLeft_y_col, .addRight_y_col, .left_plot_type, .right_plot_type, .title {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
            .left_y_col {
                .left_y_col-description {
                    display: flex;
                    align-items: center;
                    .left-y-col-close {
                        display: flex;
                        align-items: center;
                        cursor: pointer;
                        margin-left: auto;
                        border-radius: 4px;
                        &:hover {
                            background-color: #eee;
                        }
                    }
                }
            }
            .right_y_col {
                .right_y_col-description {
                    display: flex;
                    align-items: center;
                    .right-y-col-close {
                        display: flex;
                        align-items: center;
                        cursor: pointer;
                        margin-left: auto;
                        border-radius: 4px;
                        &:hover {
                            background-color: #eee;
                        }
                    }
                }
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>