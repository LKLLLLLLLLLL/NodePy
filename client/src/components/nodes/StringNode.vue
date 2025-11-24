<template>
    <div class="StringNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="input">字符串节点</NodeTitle>
        <div class="data">
            <div class="value">
                <div class="param-description" :class="{'node-has-paramerr': valueHasErr.value}">
                    字符串
                </div>
                <NodepyStringInput
                    v-model="value"
                    :disabled="false"
                    @update-value="onUpdateValue"
                    class="nodrag"
                    placeholder="常量字符串"
                />
            </div>
            <div class="output-string port">
                <div class="output-port-description">
                    字符串输出端口
                </div>
                <Handle id="string" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': stringHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import {computed, ref, watch} from 'vue'
    import type { Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import type {StringNodeData} from '../../types/nodeTypes'
    import NodepyStringInput from './tools/Nodepy-StringInput.vue'
    import { handleExecError, handleParamError, handleOutputError } from './handleError'
    import ErrorMsg from './tools/ErrorMsg.vue'
    import NodeTitle from './tools/NodeTitle.vue'


    const props = defineProps<NodeProps<StringNodeData>>()
    const value = ref(props.data.param.value)
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['string']?.type || 'default')
    const stringHasErr = computed(() => handleOutputError(props.id, 'string'))
    const errMsg = ref<string[]>([])
    const valueHasErr = ref({
        id: 'value',
        value: false
    })


    const onUpdateValue = (e?: Event) => {
        props.data.param.value = value.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, valueHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .StringNodeLayout{
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: 5px;
            .value {
                padding: 0 $node-padding-hor;
            }
            .output-string {
                margin-top: $node-margin;
            }
        }
    }
</style>
