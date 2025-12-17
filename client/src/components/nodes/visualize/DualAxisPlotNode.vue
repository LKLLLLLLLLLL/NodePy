<template>
    <div class="DualAxisPlotNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="visualize">双轴绘图</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-input port">
                <div class="input-port-description">表格输入</div>
                <Handle id="input" type="target" :position="Position.Left" :class="[`${input_type}-handle-color`, {'node-errhandle': inputHasErr.value}]"/>
            </div>
            <div class="title">
                <div class="param-description">图像标题</div>
                <NodepyStringInput :allow-null="true" v-model="title" @update-value="() => updateSimpleStringNumberBoolValue(data.param, 'title', title)" class="nodrag" placeholder="图像标题"/>
            </div>
            <div class="x_col">
                <div class="param-description" :class="{'node-has-paramerr': x_colHasErr.value}">x轴列</div>
                <NodepySelectMany
                :options="x_col_hint"
                :default-selected="x_col_default_selected"
                @select-change="(e: any) => updateSimpleSelectMany(data.param, 'x_col', x_col_hint, e)"
                @clear-select="clearSelectX"
                class="nodrag"
                />
            </div>
            <div class="left_y_col">
                <div class="param-description" :class="{'node-has-paramerr': left_y_colHasErr.value}">左y轴列</div>
                <NodepySelectMany
                :options="left_y_col_hint"
                :default-selected="left_y_col_default_selected"
                @select-change="(e: any) => updateSimpleSelectMany(data.param, 'left_y_col', left_y_col_hint, e)"
                @clear-select="clearSelectLeft_y_col"
                class="nodrag"
                />
            </div>
            <div class="left_plot_type">
                <div class="param-description" :class="{'node-has-paramerr': left_plot_typeHasErr.value}">
                    图像类型
                </div>
                <NodepySelectFew
                    :options="plot_type_options_chinese"
                    :default-selected="defaultSelectedLeft_plot_type"
                    @select-change="(e: any) => updateSimpleSelectFew(data.param, 'left_plot_type', plot_type_options, e)"
                    class="nodrag"
                />
            </div>
            <div class="right_y_col">
                <div class="param-description" :class="{'node-has-paramerr': right_y_colHasErr.value}">右y轴列</div>
                <NodepySelectMany
                :options="right_y_col_hint"
                :default-selected="right_y_col_default_selected"
                @select-change="(e: any) => updateSimpleSelectMany(data.param, 'right_y_col', right_y_col_hint, e)"
                @clear-select="clearSelectRight_y_col"
                class="nodrag"
                />
            </div>
            <div class="right_plot_type">
                <div class="param-description" :class="{'node-has-paramerr': right_plot_typeHasErr.value}">
                    图像类型
                </div>
                <NodepySelectFew
                    :options="plot_type_options_chinese"
                    :default-selected="defaultSelectedRight_plot_type"
                    @select-change="(e: any) => updateSimpleSelectFew(data.param, 'right_plot_type', plot_type_options, e)"
                    class="nodrag"
                />
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
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import { updateSimpleStringNumberBoolValue, updateSimpleSelectFew, updateSimpleSelectMany } from '../updateParam'
    import type { DualAxisPlotNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<DualAxisPlotNodeData>>()
    const plot_type_options = ["bar", "line"]
    const plot_type_options_chinese = ['条形图', '折线图']
    const defaultSelectedLeft_plot_type = [plot_type_options.indexOf(props.data.param.left_plot_type)]
    const defaultSelectedRight_plot_type = [plot_type_options.indexOf(props.data.param.right_plot_type)]
    const x_col_hint = computed(() => {
        if(props.data.hint?.x_col_choices?.length === 0) return ['']
        return props.data.hint?.x_col_choices || ['']
    })
    const x_col_default_selected = ref(x_col_hint.value.indexOf(props.data.param.x_col))

    const left_y_col_hint = computed(() => {
        if(props.data.hint?.left_y_col_choices?.length === 0) return ['']
        return props.data.hint?.left_y_col_choices || ['']
    })
    const left_y_col_default_selected = ref(left_y_col_hint.value.indexOf(props.data.param.left_y_col))

    const right_y_col_hint = computed(() => {
        if(props.data.hint?.right_y_col_choices?.length === 0) return ['']
        return props.data.hint?.right_y_col_choices || ['']
    })
    const right_y_col_default_selected = ref(right_y_col_hint.value.indexOf(props.data.param.right_y_col))

    const title = ref(props.data.param.title)
    const input_type = computed(() => getInputType(props.id, 'input'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['plot']?.type || 'default')
    const plotHasErr = computed(() => handleOutputError(props.id, 'plot'))
    const errMsg = ref<string[]>([])
    const inputHasErr = ref({
        handleId: 'input',
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


    const clearSelectX = (resolve: any) => {
        props.data.param.x_col = ''
        x_col_default_selected.value = -1
        resolve()
    }
    const clearSelectLeft_y_col = (resolve: any) => {
        props.data.param.left_y_col = ''
        left_y_col_default_selected.value = -1
        resolve()
    }
    const clearSelectRight_y_col = (resolve: any) => {
        props.data.param.right_y_col = ''
        right_y_col_default_selected.value = -1
        resolve()
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, x_colHasErr, left_y_colHasErr, left_plot_typeHasErr, right_y_colHasErr, right_plot_typeHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputHasErr)
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
            .input-input {
                margin-bottom: $node-margin;
            }
            .x_col, .left_y_col, .right_y_col, .left_plot_type, .right_plot_type, .title {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>