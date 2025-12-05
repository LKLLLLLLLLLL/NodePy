<template>
    <div class="DateTimeNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="input">日期时间输入节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="value">
                <div class="param-description" :class="{'node-has-paramerr': valueHasErr.value}">
                    日期时间(ISO 8601格式)
                </div>
                <NodepyStringInput
                    v-model="value"
                    @update-value="onUpdateValue"
                    class="nodrag"
                    placeholder="e.g. 2025-11-25T22:23:28"
                />
            </div>
            <div class="output-datetime port">
                <div class="output-port-description">
                    日期时间输出
                </div>
                <Handle id="datetime" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': datetimeHasErr}]"/>
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
    import { handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import type { DateTimeNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<DateTimeNodeData>>()
    const value = ref(props.data.param.value)
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['datetime']?.type || 'default')
    const datetimeHasErr = computed(() => handleOutputError(props.id, 'datetime'))
    const errMsg = ref<string[]>([])
    const valueHasErr = ref({
        id: 'value',
        value: false
    })


    const onUpdateValue = (e: any) => {
        if(value.value.trim().toLowerCase() === 'now') {
            props.data.param.value = new Date().toISOString()
        }else {
            props.data.param.value = value.value
        }
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, valueHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .DateTimeNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .value {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
</style>