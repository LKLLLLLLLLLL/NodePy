<template>
    <div class="DatetimeComputeNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='datetimeProcess'>日期偏移</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-datetime port">
                <div class="input-port-description">
                    日期
                </div>
                <Handle id="datetime" type="target" :position="Position.Left" :class="[`${datetime_type}-handle-color`, {'node-errhandle': datetimeHasErr.value}]"/>
            </div>
            <div class="input-value port">
                <div class="input-port-description">
                    数值
                </div>
                <Handle id="value" type="target" :position="Position.Left" :class="[`${value_type}-handle-color`, {'node-errhandle': valueHasErr.value}]"/>
            </div>
            <div class="op">
                <div class="param-description" :class="{'node-has-paramerr': opHasErr.value}">
                    运算
                </div>
                <NodepySelectFew
                    :options="opChinese"
                    :default-selected="defaultSelectedOp"
                    @select-change="onSelectChangeOp"
                    class="nodrag"
                />
            </div>
            <div class="unit">
                <div class="param-description" :class="{'node-has-paramerr': unitHasErr.value}">
                    数值单位
                </div>
                <NodepySelectMany
                    :options="unitChinese"
                    :default-selected="defaultSelectedUnit"
                    @select-change="onSelectChangeUnit"
                    class="nodrag"
                />
            </div>
            <div class="output-result port">
                <div class="output-port-description">
                    结果输出
                </div>
                <Handle id="result" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': resultHasErr}]"/>
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
    import NodepySelectFew from '../tools/Nodepy-selectFew.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import type { DatetimeComputeNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<DatetimeComputeNodeData>>()
    const op = ["ADD", "SUB"]
    const opChinese = ['加法', '减法']
    const defaultSelectedOp = [op.indexOf(props.data.param.op)]
    const unit = ["DAYS", "HOURS", "MINUTES", "SECONDS"]
    const unitChinese = ['天', '小时', '分钟', '秒']
    const defaultSelectedUnit = unit.indexOf(props.data.param.unit)
    const datetime_type = computed(() => getInputType(props.id, 'datetime'))
    const value_type = computed(() => getInputType(props.id, 'value'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['result']?.type || 'default')
    const resultHasErr = computed(() => handleOutputError(props.id, 'result'))
    const errMsg = ref<string[]>([])
    const opHasErr = ref({
        id: 'op',
        value: false
    })
    const unitHasErr = ref({
        id: 'unit',
        value: false
    })
    const datetimeHasErr = ref({
        handleId: 'datetime',
        value: false
    })
    const valueHasErr = ref({
        handleId: 'value',
        value: false
    })


    const onSelectChangeOp = (e: any) => {
        const selected_op = op[e[0]] as 'ADD' | 'SUB'
        props.data.param.op = selected_op
    }
    const onSelectChangeUnit = (e: any) => {
        const selected_unit = unit[e] as 'DAYS' | 'HOURS' | 'MINUTES' | 'SECONDS'
        props.data.param.unit = selected_unit
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, opHasErr, unitHasErr)
        handleValidationError(props.id, props.data.error, errMsg, datetimeHasErr, valueHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .DatetimeComputeNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-datetime, .input-value {
                margin-bottom: $node-margin;
            }
            .op, .unit {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color[data-handleid="datetime"] {
        background: $datetime-color;
    }
    .all-handle-color[data-handleid="value"] {
        background: linear-gradient(to bottom, $int-color 0 50%, $float-color 50% 100%);
    }
</style>
