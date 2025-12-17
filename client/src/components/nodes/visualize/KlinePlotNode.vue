<template>
    <div class="KlinePlotNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="visualize">K线图</NodeTitle>
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
            <div class="open_col">
                <div class="param-description" :class="{'node-has-paramerr': open_colHasErr.value}">开盘价列</div>
                <NodepySelectMany
                :options="open_col_hint"
                :default-selected="open_col_default_selected"
                @select-change="(e: any) => updateSimpleSelectMany(data.param, 'open_col', open_col_hint, e)"
                @clear-select="clearSelectOpen_col"
                class="nodrag"
                />
            </div>
            <div class="high_col">
                <div class="param-description" :class="{'node-has-paramerr': high_colHasErr.value}">最高价列</div>
                <NodepySelectMany
                :options="high_col_hint"
                :default-selected="high_col_default_selected"
                @select-change="(e: any) => updateSimpleSelectMany(data.param, 'high_col', high_col_hint, e)"
                @clear-select="clearSelectHigh_col"
                class="nodrag"
                />
            </div>
            <div class="low_col">
                <div class="param-description" :class="{'node-has-paramerr': low_colHasErr.value}">最低价列</div>
                <NodepySelectMany
                :options="low_col_hint"
                :default-selected="low_col_default_selected"
                @select-change="(e: any) => updateSimpleSelectMany(data.param, 'low_col', low_col_hint, e)"
                @clear-select="clearSelectLow_col"
                class="nodrag"
                />
            </div>
            <div class="close_col">
                <div class="param-description" :class="{'node-has-paramerr': close_colHasErr.value}">收盘价列</div>
                <NodepySelectMany
                :options="close_col_hint"
                :default-selected="close_col_default_selected"
                @select-change="(e: any) => updateSimpleSelectMany(data.param, 'close_col', close_col_hint, e)"
                @clear-select="clearSelectClose_col"
                class="nodrag"
                />
            </div>
            <div class="volume_col">
                <div class="param-description" :class="{'node-has-paramerr': volume_colHasErr.value}">成交量列</div>
                <NodepySelectMany
                :options="volume_col_hint"
                :default-selected="volume_col_default_selected"
                @select-change="(e: any) => updateSimpleSelectMany(data.param, 'volume_col', volume_col_hint, e)"
                @clear-select="clearSelectVolume_col"
                class="nodrag"
                />
            </div>
            <div class="style_mode">
                <div class="param-description" :class="{'node-has-paramerr': style_modeHasErr.value}">
                    配色风格
                </div>
                <NodepySelectFew
                    :options="style_mode_options_chinese"
                    :default-selected="defaultSelectedStyle_mode"
                    @select-change="(e: any) => updateSimpleSelectFew(data.param, 'style_mode', style_mode_options, e)"
                    class="nodrag"
                />
            </div>
            <div class="output-kline_plot port">
                <div class="output-port-description">图像输出</div>
                <Handle id="kline_plot" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': kline_plotHasErr}]"/>
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
    import type { KlinePlotNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<KlinePlotNodeData>>()
    const style_mode_options = ["CN", "US"]
    const style_mode_options_chinese = ['中式', '美式']
    const defaultSelectedStyle_mode = [style_mode_options.indexOf(props.data.param.style_mode)]
    const x_col_hint = computed(() => {
        if(props.data.hint?.x_col_choices?.length === 0) return ['']
        return props.data.hint?.x_col_choices || ['']
    })
    const x_col_default_selected = ref(x_col_hint.value.indexOf(props.data.param.x_col))

    const open_col_hint = computed(() => {
        if(props.data.hint?.open_col_choices?.length === 0) return ['']
        return props.data.hint?.open_col_choices || ['']
    })
    const open_col_default_selected = ref(open_col_hint.value.indexOf(props.data.param.open_col))

    const high_col_hint = computed(() => {
        if(props.data.hint?.high_col_choices?.length === 0) return ['']
        return props.data.hint?.high_col_choices || ['']
    })
    const high_col_default_selected = ref(high_col_hint.value.indexOf(props.data.param.high_col))

    const low_col_hint = computed(() => {
        if(props.data.hint?.low_col_choices?.length === 0) return ['']
        return props.data.hint?.low_col_choices || ['']
    })
    const low_col_default_selected = ref(low_col_hint.value.indexOf(props.data.param.low_col))

    const close_col_hint = computed(() => {
        if(props.data.hint?.close_col_choices?.length === 0) return ['']
        return props.data.hint?.close_col_choices || ['']
    })
    const close_col_default_selected = ref(close_col_hint.value.indexOf(props.data.param.close_col))

    const volume_col_hint = computed(() => {
        if(props.data.hint?.volume_col_choices?.length === 0) return ['']
        return props.data.hint?.volume_col_choices || ['']
    })
    const volume_col_default_selected = ref(volume_col_hint.value.indexOf(props.data.param.volume_col))

    const title = ref(props.data.param.title)
    const input_type = computed(() => getInputType(props.id, 'input'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['kline_plot']?.type || 'default')
    const kline_plotHasErr = computed(() => handleOutputError(props.id, 'kline_plot'))
    const errMsg = ref<string[]>([])
    const inputHasErr = ref({
        handleId: 'input',
        value: false
    })
    const x_colHasErr = ref({
        id: 'x_col',
        value: false
    })
    const open_colHasErr = ref({
        id: 'open_col',
        value: false
    })
    const high_colHasErr = ref({
        id: 'high_col',
        value: false
    })
    const low_colHasErr = ref({
        id: 'low_col',
        value: false
    })
    const close_colHasErr = ref({
        id: 'close_col',
        value: false
    })
    const volume_colHasErr = ref({
        id: 'volume_col',
        value: false
    })
    const style_modeHasErr = ref({
        id: 'style_mode',
        value: false
    })


    const clearSelectX = (resolve: any) => {
        props.data.param.x_col = 'Open Time'
        x_col_default_selected.value = x_col_hint.value.indexOf(props.data.param.x_col)
        resolve()
    }
    const clearSelectOpen_col = (resolve: any) => {
        props.data.param.open_col = 'Open'
        open_col_default_selected.value = open_col_hint.value.indexOf(props.data.param.open_col)
        resolve()
    }
    const clearSelectHigh_col = (resolve: any) => {
        props.data.param.high_col = 'High'
        high_col_default_selected.value = high_col_hint.value.indexOf(props.data.param.high_col)
        resolve()
    }
    const clearSelectLow_col = (resolve: any) => {
        props.data.param.low_col = 'Low'
        low_col_default_selected.value = low_col_hint.value.indexOf(props.data.param.low_col)
        resolve()
    }
    const clearSelectClose_col = (resolve: any) => {
        props.data.param.close_col = 'Close'
        close_col_default_selected.value = close_col_hint.value.indexOf(props.data.param.close_col)
        resolve()
    }
    const clearSelectVolume_col = (resolve: any) => {
        props.data.param.volume_col = 'Volume'
        volume_col_default_selected.value = volume_col_hint.value.indexOf(props.data.param.volume_col)
        resolve()
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, x_colHasErr, open_colHasErr, high_colHasErr, low_colHasErr, close_colHasErr, volume_colHasErr, style_modeHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .KlinePlotNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-input {
                margin-bottom: $node-margin;
            }
            .x_col, .open_col, .high_col, .low_col, .close_col, .volume_col, .title, .style_mode {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>