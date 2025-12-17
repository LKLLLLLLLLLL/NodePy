<template>
    <div class="ToDatetimeNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='datetimeProcess'>转为日期</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-value port">
                <div class="input-port-description">
                    数值输入
                </div>
                <Handle id="value" type="target" :position="Position.Left" :class="[`${value_type}-handle-color`, {'node-errhandle': valueHasErr.value}]"/>
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
            <div class="output-datetime port">
                <div class="output-port-description">
                    日期输出
                </div>
                <Handle id="datetime" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': datetimeHasErr}]"/>
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
    import type { ToDatetimeNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<ToDatetimeNodeData>>()
    const unit = ["DAYS", "HOURS", "MINUTES", "SECONDS"]
    const unitChinese = ['天', '小时', '分钟', '秒']
    const defaultSelectedUnit = unit.indexOf(props.data.param.unit)
    const value_type = computed(() => getInputType(props.id, 'value'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['datetime']?.type || 'default')
    const datetimeHasErr = computed(() => handleOutputError(props.id, 'datetime'))
    const errMsg = ref<string[]>([])
    const unitHasErr = ref({
        id: 'unit',
        value: false
    })
    const valueHasErr = ref({
        handleId: 'value',
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
        handleValidationError(props.id, props.data.error, errMsg, valueHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .ToDatetimeNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-value {
                margin-bottom: $node-margin;
            }
            .unit {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: linear-gradient(to bottom, $int-color 0 50%, $float-color 50% 100%);
    }
</style>
