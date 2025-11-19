<template>
    <div class="PlotNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <div class="node-title-visualize nodes-topchild-border-radius">{{`绘图节点${props.id.split('_')[1]}`}}</div>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">表格输入端口</div>
                <Handle id="input" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': tableHasErr.value}]"/>
            </div>
            <div class="x_col">
                <div class="param-description" :class="{'node-has-paramerr': x_colHasErr.value}">x轴列名</div>
                <NodepyStringInput v-model="x_col" @update-value="onUpdateX_col" class="nodrag"/>
            </div>
            <div class="y_col">
                <div class="param-description" :class="{'node-has-paramerr': y_colHasErr.value}">y轴列名</div>
                <NodepyStringInput v-model="y_col" @update-value="onUpdateY_col" class="nodrag"/>
            </div>
            <div class="plot_type">
                <div class="param-description" :class="{'node-has-paramerr': plot_typeHasErr.value}">图形类型</div>
                <NodepySelectFew
                    :options="plot_type_options"
                    :select-max-num="1"
                    :defualt-selected="defaultSelected"
                    @select-change="onSelectChange"
                    item-width="90px"
                    class="nodrag"
                />
            </div>
            <div class="title">
                <div class="param-description">图形标题</div>
                <NodepyStringInput v-model="title" @update-value="onUpdateTitle" class="nodrag"/>
            </div>
            <div class="output-plot port">
                <div class="output-port-description">图形输出端口</div>
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
    import { getInputType } from './getInputType'
    import { handleExecError, handleParamError, handleValidationError, handleOutputError } from './handleError'
    import NodepyStringInput from './tools/Nodepy-StringInput.vue'
    import NodepySelectFew from './tools/Nodepy-selectFew.vue'
    import ErrorMsg from './tools/ErrorMsg.vue'


    const props = defineProps<NodeProps<PlotNodeData>>()
    const x_col = ref(props.data.param.x_col)
    const y_col = ref(props.data.param.y_col)
    const title = ref(props.data.param.title || '')
    const plot_type_options = ['bar', 'line', 'scatter']
    const defaultSelected = [plot_type_options.indexOf(props.data.param.plot_type)]
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
        const selected_plot_type = plot_type_options[e] as 'bar'| 'line'| 'scatter'
        props.data.param.plot_type = selected_plot_type
    }

    const onUpdateX_col = () => {
        props.data.param.x_col = x_col.value
    }

    const onUpdateY_col = () => {
        props.data.param.y_col = y_col.value
    }

    const onUpdateTitle = () => {
        props.data.param.title = title.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, x_colHasErr, y_colHasErr, plot_typeHasErr)
        handleValidationError(props.id, props.data.error, errMsg, tableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .PlotNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding;
            padding-bottom: 5px;
            .input-table {
                margin-bottom: $node-margin;
            }
            .x_col, .y_col, .plot_type, .title {
                padding: 0 $node-padding;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>
