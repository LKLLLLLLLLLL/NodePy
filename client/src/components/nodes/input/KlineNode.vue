<template>
    <div class="KlineNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='input'>K线数据节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-start_time port">
                <div class="input-port-description" :class="{'node-has-paramerr': start_timeHasErr.value}">
                    开始时间
                </div>
                <Handle id="start_time" type="target" :position="Position.Left" :class="[`${inputStart_time_type}-handle-color`, {'node-errhandle': inputStart_timeHasErr.value}]"/>
            </div>
            <div class="start_time">
                <NodepyStringInput
                    v-model="start_time"
                    @update-value="onUpdateStart_time"
                    :disabled="start_timeDisabled"
                    :allow-null="true"
                    class="nodrag"
                    placeholder="开始时间"
                />
            </div>
            <div class="input-end_time port">
                <div class="input-port-description" :class="{'node-has-paramerr': end_timeHasErr.value}">
                    结束时间
                </div>
                <Handle id="end_time" type="target" :position="Position.Left" :class="[`${inputEnd_time_type}-handle-color`, {'node-errhandle': inputEnd_timeHasErr.value}]"/>
            </div>
            <div class="end_time">
                <NodepyStringInput
                    v-model="end_time"
                    @update-value="onUpdateEnd_time"
                    :disabled="end_timeDisabled"
                    :allow-null="true"
                    class="nodrag"
                    placeholder="结束时间"
                />
            </div>
            <div class="data_type">
                <div class="param-description" :class="{'node-has-paramerr': data_typeHasErr.value}">
                    数据类型
                </div>
                <NodepySelectFew
                    :options="data_typeChinese"
                    :default-selected="defaultSelectedData_type"
                    @select-change="onSelectChangeData_type"
                    class="nodrag"
                />
            </div>
            <div class="symbol">
                <div class="param-description" :class="{'node-has-paramerr': symbolHasErr.value}">
                    代码
                </div>
                <NodepyStringInput
                v-model="symbol"
                placeholder="代码"
                @update-value="onUpdateSymbol"
                class="nodrag"
                />
            </div>
            <div class="interval">
                <div class="param-description" :class="{'node-has-paramerr': intervalHasErr.value}">
                    时间间隔
                </div>
                <NodepySelectFew
                    :options="intervalChinese"
                    :default-selected="defaultSelectedInterval"
                    @select-change="onSelectChangeInterval"
                    class="nodrag"
                />
            </div>
            <div class="output-kline_data port">
                <div class="output-port-description">
                    K线数据表格输出
                </div>
                <Handle id="kline_data" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': kline_dataHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import NodeTitle from '../tools/NodeTitle.vue'
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Handle, Position } from '@vue-flow/core'
    import { computed, ref, watch } from 'vue'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import Timer from '../tools/Timer.vue'
    import { getInputType } from '../getInputType'
    import { hasInputEdge } from '../hasEdge'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import NodepySelectFew from '../tools/Nodepy-selectFew.vue'
    import type { KlineNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<KlineNodeData>>()
    const start_time = ref(props.data.param.start_time)
    const start_timeDisabled = computed(() => hasInputEdge(props.id, 'start_time'))
    const end_time = ref(props.data.param.end_time)
    const end_timeDisabled = computed(() => hasInputEdge(props.id, 'end_time'))
    const data_type = ["stock", "crypto"]
    const data_typeChinese = ['股票', '加密货币']
    const defaultSelectedData_type = [data_type.indexOf(props.data.param.data_type)]
    const interval = ["1m", "1h", "1d"]
    const intervalChinese = ['1分钟', '1小时', '1天']
    const defaultSelectedInterval = [interval.indexOf(props.data.param.interval)]
    const symbol = ref(props.data.param.symbol)
    const inputStart_time_type = computed(() => getInputType(props.id, 'start_time'))
    const inputEnd_time_type = computed(() => getInputType(props.id, 'end_time'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['kline_data']?.type || 'default')
    const kline_dataHasErr = computed(() => handleOutputError(props.id, 'kline_data'))
    const errMsg = ref<string[]>([])
    const data_typeHasErr = ref({
        id: 'data_type',
        value: false
    })
    const symbolHasErr = ref({
        id: 'symbol',
        value: false
    })
    const start_timeHasErr = ref({
        id: 'start_time',
        value: false
    })
    const end_timeHasErr = ref({
        id: 'end_time',
        value: false
    })
    const intervalHasErr = ref({
        id: 'interval',
        value: false
    })
    const inputStart_timeHasErr = ref({
        handleId: 'start_time',
        value: false
    })
    const inputEnd_timeHasErr = ref({
        handleId: 'end_time',
        value: false
    })


    const onUpdateStart_time = (e: any) => {
        props.data.param.start_time = start_time.value
    }
    const onUpdateEnd_time = (e: any) => {
        props.data.param.end_time = end_time.value
    }
    const onSelectChangeData_type = (e: any) => {
        props.data.param.data_type = data_type[e[0]] as 'stock'|'crypto'
    }
    const onSelectChangeInterval = (e: any) => {
        props.data.param.interval = interval[e[0]] as '1m'|'1h'|'1d'
    }
    const onUpdateSymbol = (e: any) => {
        props.data.param.symbol = symbol.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, data_typeHasErr, symbolHasErr, start_timeHasErr, end_timeHasErr, intervalHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputStart_timeHasErr, inputEnd_timeHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .KlineNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-start_time, .input-end_time {
                margin-bottom: 2px;
            }
            .data_type, .symbol, .start_time, .end_time, .interval {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $datetime-color;
    }
</style>
