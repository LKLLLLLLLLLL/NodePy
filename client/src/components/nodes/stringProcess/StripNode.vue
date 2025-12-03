<template>
    <div class="StripNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='stringProcess'>首尾字符清洗节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-input port">
                <div class="input-port-description">
                    字符串输入
                </div>
                <Handle id="input" type="target" :position="Position.Left" :class="[`${input_type}-handle-color`, {'node-errhandle': inputHasErr.value}]"/>
            </div>
            <div class="input-strip_chars port">
                <div class="input-port-description" :class="{'node-has-paramerr': strip_charsHasErr.value}">
                    清洗字符集合输入
                </div>
                <Handle id="strip_chars" type="target" :position="Position.Left" :class="[`${inputStrip_chars_type}-handle-color`, {'node-errhandle': inputStrip_charsHasErr.value}]"/>
            </div>
            <div class="strip_chars">
                <NodepyStringInput
                    v-model="strip_chars"
                    @update-value="onUpdateStrip_chars"
                    :disabled="strip_charsDisabled"
                    class="nodrag"
                    placeholder="清洗字符集合"
                />
            </div>
            <div class="output-output port">
                <div class="output-port-description">
                    字符串输出
                </div>
                <Handle id="output" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': outputHasErr}]"/>
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
    import type { Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import { hasInputEdge } from '../hasEdge'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import type { StripNodeData } from '@/types/nodeTypes'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'


    const props = defineProps<NodeProps<StripNodeData>>()
    const strip_chars = ref(props.data.param.strip_chars || '')
    const strip_charsDisabled = computed(() => hasInputEdge(props.id, 'strip_chars'))
    const input_type = computed(() => getInputType(props.id, 'input'))
    const inputStrip_chars_type = computed(() => getInputType(props.id, 'strip_chars'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['output']?.type || 'default')
    const outputHasErr = computed(() => handleOutputError(props.id, 'output'))
    const errMsg = ref<string[]>([])
    const strip_charsHasErr = ref({
        id: 'strip_chars',
        value: false
    })
    const inputHasErr = ref({
        handleId: 'input',
        value: false
    })
    const inputStrip_charsHasErr = ref({
        handleId: 'strip_chars',
        value: false
    })


    const onUpdateStrip_chars = (e?: Event) => {
        props.data.param.strip_chars = strip_chars.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, strip_charsHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputHasErr, inputStrip_charsHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .StripNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-input {
                margin-bottom: $node-margin;
            }
            .input-strip_chars {
                margin-bottom: 2px;
            }
            .strip_chars {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $str-color;
    }
</style>