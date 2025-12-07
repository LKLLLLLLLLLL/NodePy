<template>
    <div class="StrToDatetimeNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='datetimeProcess'>字符串时间转换节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-value port">
                <div class="input-port-description">
                    字符串输入
                </div>
                <Handle id="value" type="target" :position="Position.Left" :class="[`${value_type}-handle-color`, {'node-errhandle': valueHasErr.value}]"/>
            </div>
            <div class="output-datetime port">
                <div class="output-port-description">
                    时间输出
                </div>
                <Handle id="datetime" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': datetimeHasErr}]"/>
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
    import type { BaseData } from '../../../types/nodeTypes'
    import { getInputType } from '../getInputType'
    import { handleExecError, handleValidationError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'


    const props = defineProps<NodeProps<BaseData>>()
    const value_type = computed(() => getInputType(props.id, 'value'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['datetime']?.type || 'default')
    const datetimeHasErr = computed(() => handleOutputError(props.id, 'datetime'))
    const errMsg = ref<string[]>([])
    const valueHasErr = ref({
        handleId: 'value',
        value: false
    })


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleValidationError(props.id, props.data.error, errMsg, valueHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .StrToDatetimeNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-value {
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $str-color;
    }
</style>