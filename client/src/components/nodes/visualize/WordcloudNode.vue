<template>
    <div class="WordcloudNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="visualize">词云节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-input port">
                <div class="input-port-description">表格输入</div>
                <Handle id="input" type="target" :position="Position.Left" :class="[`${input_type}-handle-color`, {'node-errhandle': inputHasErr.value}]"/>
            </div>
            <div class="word_col">
                <div class="param-description" :class="{'node-has-paramerr': word_colHasErr.value}">词语列名</div>
                <NodepySelectMany
                :options="word_col_hint"
                :default-selected="word_col_default_selected"
                @select-change="onUpdateWord_col"
                @clear-select="clearSelectWord_col"
                class="nodrag"
                />
            </div>
            <div class="frequency_col" v-if="data.param.plot_type !== 'count' && data.param.plot_type !== 'hist'">
                <div class="param-description" :class="{'node-has-paramerr': frequency_colHasErr.value}">频率列名</div>
                <NodepySelectMany
                :options="frequency_col_hint"
                :default-selected="frequency_col_default_selected"
                @select-change="onUpdateFrequency_col"
                @clear-select="clearSelectFrequency_col"
                class="nodrag"
                />
            </div>
            <div class="output-wordcloud_image port">
                <div class="output-port-description">图像输出</div>
                <Handle id="wordcloud_image" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': wordcloud_imageHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import type { Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Handle, Position } from '@vue-flow/core'
    import { computed, ref, watch } from 'vue'
    import { getInputType } from '../getInputType'
    import { handleExecError, handleParamError, handleValidationError, handleOutputError } from '../handleError'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import type { WordcloudNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<WordcloudNodeData>>()
    const word_col_hint = computed(() => {
        if(props.data.hint?.word_col_choices?.length === 0) return ['']
        return props.data.hint?.word_col_choices || ['']
    })
    const frequency_col_hint = computed(() => {
        if(props.data.hint?.frequency_col_choices?.length === 0) return ['']
        return props.data.hint?.frequency_col_choices || ['']
    })
    const word_col = ref(props.data.param.word_col)   // used for word_col_default_selected
    const frequency_col = ref(props.data.param.frequency_col)   // used for frequency_col_default_selected
    const word_col_default_selected = computed(() => word_col_hint.value.indexOf(word_col.value))
    const frequency_col_default_selected = computed(() => frequency_col_hint.value.indexOf(frequency_col.value))
    const input_type = computed(() => getInputType(props.id, 'input'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['wordcloud_image']?.type || 'default')
    const wordcloud_imageHasErr = computed(() => handleOutputError(props.id, 'wordcloud_image'))
    const errMsg = ref<string[]>([])
    const inputHasErr = ref({
        handleId: 'input',
        value: false
    })
    const word_colHasErr = ref({
        id: 'word_col',
        value: false
    })
    const frequency_colHasErr = ref({
        id: 'frequency_col',
        value: false
    })


    const onUpdateWord_col = (e: any) => {
        props.data.param.word_col = word_col_hint.value[e]
    }
    const onUpdateFrequency_col = (e: any) => {
        props.data.param.frequency_col = frequency_col_hint.value[e]
    }
    const clearSelectWord_col = (resolve: any) => {
        props.data.param.word_col = ''
        word_col.value = props.data.param.word_col
        resolve()
    }
    const clearSelectFrequency_col = (resolve: any) => {
        props.data.param.frequency_col = ''
        frequency_col.value = props.data.param.frequency_col
        resolve()
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, word_colHasErr, frequency_colHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .WordcloudNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-input {
                margin-bottom: $node-margin;
            }
            .word_col, .frequency_col {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>