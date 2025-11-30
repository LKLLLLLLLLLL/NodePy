<template>
    <div class="PlotNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="visualize">绘图节点</NodeTitle>
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
            <div class="y_col">
                <div class="param-description" :class="{'node-has-paramerr': y_colHasErr.value}">y轴列名</div>
                <NodepySelectMany
                :options="y_col_hint"
                :default-selected="y_col_default_selected"
                @select-change="onUpdateY_col"
                @clear-select="clearSelectY"
                class="nodrag"
                />
            </div>
            <div class="plot_type">
                <div class="param-description" :class="{'node-has-paramerr': plot_typeHasErr.value}">图形类型</div>
                <NodepySelectMany
                    :options="plot_type_options_chinese"
                    :default-selected="defaultSelected"
                    @select-change="onSelectChange"
                    class="nodrag"
                />
            </div>
            <div class="title">
                <div class="param-description">图像标题</div>
                <NodepyStringInput v-model="title" @update-value="onUpdateTitle" class="nodrag" placeholder="图像标题"/>
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
    import type { PlotNodeData } from '@/types/nodeTypes'
    import type { Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Handle, Position } from '@vue-flow/core'
    import { computed, ref, watch } from 'vue'
    import { getInputType } from '../getInputType'
    import { handleExecError, handleParamError, handleValidationError, handleOutputError } from '../handleError'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'


    const props = defineProps<NodeProps<PlotNodeData>>()
    const x_col_hint = computed(() => props.data.hint?.x_col_choices || [''])
    const y_col_hint = computed(() => props.data.hint?.y_col_choices || [''])
    const x_col = ref(props.data.param.x_col)   // used for x_col_default_selected
    const y_col = ref(props.data.param.y_col)   // used for y_col_default_selected
    const x_col_default_selected = computed(() => x_col_hint.value.indexOf(x_col.value))
    const y_col_default_selected = computed(() => y_col_hint.value.indexOf(y_col.value))
    const title = ref(props.data.param.title || '')
    const plot_type_options = ['bar', 'line', 'scatter', 'pie']
    const plot_type_options_chinese = ['条形图', '折线图', '散点图', '饼状图']
    const defaultSelected = plot_type_options.indexOf(props.data.param.plot_type)
    const table_type = computed(() => getInputType(props.id, 'input'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['plot']?.type || 'default')
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


    const onSelectChange = (e: any) => {
        const selected_plot_type = plot_type_options[e] as 'bar'| 'line'| 'scatter' | 'pie'
        props.data.param.plot_type = selected_plot_type
    }

    const onUpdateX_col = (e: any) => {
        props.data.param.x_col = x_col_hint.value[e]
    }

    const onUpdateY_col = (e: any) => {
        props.data.param.y_col = y_col_hint.value[e]
    }

    const onUpdateTitle = () => {
        props.data.param.title = title.value
    }

    const clearSelectX = (resolve: any) => {
        props.data.param.x_col = ''
        x_col.value = props.data.param.x_col
        resolve()
    }

    const clearSelectY = (resolve: any) => {
        props.data.param.y_col = ''
        y_col.value = props.data.param.y_col
        resolve()
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
    .PlotNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .x_col, .y_col, .plot_type, .title {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>
