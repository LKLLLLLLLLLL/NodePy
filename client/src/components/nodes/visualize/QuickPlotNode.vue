<template>
    <div class="QuickPlotNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="visualize">快速绘图节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">表格输入</div>
                <Handle id="input" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': tableHasErr.value}]"/>
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
            <div class="y_cols"v-for="(y_col, idx) in y_cols" :key="y_col.id">
                <div class="y_col">
                    <div class="param-description y_col-description" :class="{'node-has-paramerr': y_colHasErr.value}">
                        <span class="y-col-label">y轴列名</span>
                        <NodepyCross v-if="y_cols.length > 1" :handle-click="() => removeY_col(idx)" class="y-col-close"/>
                    </div>
                    <NodepySelectMany
                    :options="y_col_hint"
                    :default-selected="y_col.defaultSelected"
                    @select-change="(e: any) => onUpdateY_col(e, idx)"
                    @clear-select="clearSelectY"
                    class="nodrag"
                    />
                </div>
                <div class="plot_type">
                    <div class="param-description" :class="{'node-has-paramerr': plot_typeHasErr.value}">图形类型</div>
                    <NodepySelectMany
                        :options="plot_type_options_chinese"
                        :default-selected="y_col.defaultSelectedPlot_type"
                        @select-change="(e: any) => onSelectChange(e, idx)"
                        class="nodrag"
                    />
                </div>
            </div>
            <div class="addY_col">
                <NodepyButton :handle-click="addY_col">
                    <NodepyPlus/>
                    添加y轴
                </NodepyButton>
            </div>
            <div class="title">
                <div class="param-description">图像标题</div>
                <NodepyStringInput :allow-null="true" v-model="title" @update-value="onUpdateTitle" class="nodrag" placeholder="图像标题"/>
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
    import type { QuickPlotNodeData } from '@/types/nodeTypes'
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Handle, Position } from '@vue-flow/core'
    import { computed, ref, watch } from 'vue'
    import { getInputType } from '../getInputType'
    import { handleExecError, handleParamError, handleValidationError, handleOutputError } from '../handleError'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import NodepyButton from '../tools/Nodepy-button.vue'
    import NodepyCross from '../tools/Nodepy-cross.vue'
    import NodepyPlus from '../tools/Nodepy-plus.vue'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'


    const props = defineProps<NodeProps<QuickPlotNodeData>>()
    const plot_type_options = ["scatter", "line", "bar", "area"]
    const plot_type_options_chinese = ['散点图', '折线图', '条形图', '面积图']
    const x_col_hint = computed(() => {
        if(props.data.hint?.x_col_choices?.length === 0) return ['']
        return props.data.hint?.x_col_choices || ['']
    })
    const x_col = ref(props.data.param.x_col)   // used for x_col_default_selected
    const x_col_default_selected = computed(() => x_col_hint.value.indexOf(x_col.value))
    const y_col_hint = computed(() => {
        if(props.data.hint?.y_col_choices?.length === 0) return ['']
        return props.data.hint?.y_col_choices || ['']
    })
    const y_cols = ref(props.data.param.y_col.map((item, idx) => {
        return {
            id: Date.now().toString()+`_${idx}`,
            name: item,
            defaultSelected: y_col_hint.value.indexOf(item),
            defaultSelectedPlot_type: plot_type_options.indexOf(props.data.param.plot_type[idx]!)
        }
    }))
    const title = ref(props.data.param.title)
    const table_type = computed(() => getInputType(props.id, 'input'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['plot']?.type || 'default')
    const plotHasErr = computed(() => handleOutputError(props.id, 'plot'))
    const errMsg = ref<string[]>([])
    const tableHasErr = ref({
        handleId: 'input',
        value: false
    })
    const x_colHasErr = ref({
        id: 'x_col',
        value: false
    })
    const y_colHasErr = ref({
        id: 'y_col',
        value: false
    })
    const plot_typeHasErr = ref({
        id: 'plot_type',
        value: false
    })


    const onSelectChange = (plot_typeIdx: number, y_colsIdx: number) => {
        const selected_plot_type = plot_type_options[plot_typeIdx] as 'scatter'| 'line'| 'bar' | 'area'
        props.data.param.plot_type[y_colsIdx] = selected_plot_type
    }
    const onUpdateX_col = (e: any) => {
        props.data.param.x_col = x_col_hint.value[e]
    }
    const clearSelectX = (resolve: any) => {
        props.data.param.x_col = ''
        x_col.value = props.data.param.x_col
        resolve()
    }
    const onUpdateTitle = () => {
        props.data.param.title = title.value
    }
    const onUpdateY_col = (hintIdx: number, y_colsIdx: number) => {
        y_cols.value[y_colsIdx]!.name = y_col_hint.value[hintIdx]
        props.data.param.y_col[y_colsIdx] = y_col_hint.value[hintIdx]
    }
    const clearSelectY = (resolve: any) => {
        props.data.param.y_col = ['']
        props.data.param.plot_type = ['line']
        y_cols.value = [{id: Date.now().toString()+'_0', name: '', defaultSelected: -1, defaultSelectedPlot_type: 1}]
        resolve()
    }
    const removeY_col = (idx: number) => {
        if(y_cols.value.length > 1) {
            y_cols.value.splice(idx, 1)
            props.data.param.y_col.splice(idx, 1)
            props.data.param.plot_type.splice(idx, 1)
        }
    }
    const addY_col = () => {
        y_cols.value.push({id: Date.now().toString()+`_${y_cols.value.length}`, name: '', defaultSelected: -1, defaultSelectedPlot_type: 1})
        props.data.param.y_col.push('')
        props.data.param.plot_type.push('line')
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, x_colHasErr, y_colHasErr, plot_typeHasErr)
        handleValidationError(props.id, props.data.error, errMsg, tableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .QuickPlotNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .x_col, .y_col, .addY_col, .plot_type, .title {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
            .y_col {
                .y_col-description {
                    display: flex;
                    align-items: center;
                    .y-col-close {
                        display: flex;
                        align-items: center;
                        cursor: pointer;
                        opacity: 0.6;
                        &:hover {
                            opacity: 1;
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
