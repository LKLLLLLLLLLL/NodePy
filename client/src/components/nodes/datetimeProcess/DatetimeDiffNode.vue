<template>
    <div class="DatetimeDiffNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='datetimeProcess'>日期差值</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-datetime_x port">
                <div class="input-port-description">
                    日期x
                </div>
                <Handle id="datetime_x" type="target" :position="Position.Left" :class="[`${datetime_x_type}-handle-color`, {'node-errhandle': datetime_xHasErr.value}]"/>
            </div>
            <div class="input-datetime_y port">
                <div class="input-port-description">
                    日期y
                </div>
                <Handle id="datetime_y" type="target" :position="Position.Left" :class="[`${datetime_y_type}-handle-color`, {'node-errhandle': datetime_yHasErr.value}]"/>
            </div>
            <div class="unit">
                <div class="param-description" :class="{'node-has-paramerr': unitHasErr.value}">
                    差值单位
                </div>
                <NodepySelectMany
                    :options="unitChinese"
                    :default-selected="defaultSelectedUnit"
                    @select-change="onSelectChangeUnit"
                    class="nodrag"
                />
            </div>
            <div class="output-difference port">
                <div class="output-port-description">
                    差值输出
                </div>
                <Handle id="difference" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': differenceHasErr}]"/>
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
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import type { DatetimeDiffNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<DatetimeDiffNodeData>>()
    const unit = ["DAYS", "HOURS", "MINUTES", "SECONDS"]
    const unitChinese = ['天', '小时', '分钟', '秒']
    const defaultSelectedUnit = unit.indexOf(props.data.param.unit)
    const datetime_x_type = computed(() => getInputType(props.id, 'datetime_x'))
    const datetime_y_type = computed(() => getInputType(props.id, 'datetime_y'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['difference']?.type || 'default')
    const differenceHasErr = computed(() => handleOutputError(props.id, 'difference'))
    const errMsg = ref<string[]>([])
    const unitHasErr = ref({
        id: 'unit',
        value: false
    })
    const datetime_xHasErr = ref({
        handleId: 'datetime_x',
        value: false
    })
    const datetime_yHasErr = ref({
        handleId: 'datetime_y',
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
        handleValidationError(props.id, props.data.error, errMsg, datetime_xHasErr, datetime_yHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .DatetimeDiffNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-datetime_x, .input-datetime_y {
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
