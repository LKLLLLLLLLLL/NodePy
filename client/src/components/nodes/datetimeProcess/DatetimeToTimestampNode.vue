<template>
    <div class="DatetimeToTimestampNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='datetimeProcess'>时间戳转换节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-datetime port">
                <div class="input-port-description">
                    时间输入
                </div>
                <Handle id="datetime" type="target" :position="Position.Left" :class="[`${datetime_type}-handle-color`, {'node-errhandle': datetimeHasErr.value}]"/>
            </div>
            <div class="unit">
                <div class="param-description" :class="{'node-has-paramerr': unitHasErr.value}">
                    单位
                </div>
                <NodepySelectMany
                    :options="unitChinese"
                    :default-selected="defaultSelectedUnit"
                    @select-change="onSelectChangeUnit"
                    class="nodrag"
                />
            </div>
            <div class="output-timestamp port">
                <div class="output-port-description">
                    时间戳输出
                </div>
                <Handle id="timestamp" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': timestampHasErr}]"/>
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
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import type { DatetimeToTimestampNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<DatetimeToTimestampNodeData>>()
    const unit = ["DAYS", "HOURS", "MINUTES", "SECONDS"]
    const unitChinese = ['天', '小时', '分钟', '秒']
    const defaultSelectedUnit = unit.indexOf(props.data.param.unit)
    const datetime_type = computed(() => getInputType(props.id, 'datetime'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['timestamp']?.type || 'default')
    const timestampHasErr = computed(() => handleOutputError(props.id, 'timestamp'))
    const errMsg = ref<string[]>([])
    const unitHasErr = ref({
        id: 'unit',
        value: false
    })
    const datetimeHasErr = ref({
        handleId: 'datetime',
        value: false
    })


    const onSelectChangeUnit = (e: any) => {
        const selected_unit = unit[e] as 'DAYS' | 'HOURS' | 'MINUTES' | 'SECONDS'
        props.data.param.unit = selected_unit
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, unitHasErr)
        handleValidationError(props.id, props.data.error, errMsg, datetimeHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .DatetimeToTimestampNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-datetime {
                margin-bottom: $node-margin;
            }
            .unit {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $datetime-color;
    }
</style>