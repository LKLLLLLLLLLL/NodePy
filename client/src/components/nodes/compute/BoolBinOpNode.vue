<template>
    <div class="BoolBinOpNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="compute">布尔二元运算节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-x port">
                <div class="input-port-description">
                    x输入
                </div>
                <Handle id="x" type="target" :position="Position.Left" :class="[`${x_type}-handle-color`, {'node-errhandle': xHasErr.value}]"/>
            </div>
            <div class="input-y port">
                <div class="input-port-description">
                    y输入
                </div>
                <Handle id="y" type="target" :position="Position.Left" :class="[`${y_type}-handle-color`, {'node-errhandle': yHasErr.value}]"/>
            </div>
            <div class="op">
                <div class="param-description" :class="{'node-has-paramerr': opHasErr.value}">
                    运算类型
                </div>
                <NodepySelectMany
                    :options="opChinese"
                    :default-selected="defaultSelected"
                    @select-change="onSelectChange"
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
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import type {BoolBinOpNodeData} from '@/types/nodeTypes'


    const props = defineProps<NodeProps<BoolBinOpNodeData>>()
    const op = ['AND', 'OR', 'XOR', 'SUB']
    const opChinese = ['与', '或', '异或', '减']
    const defaultSelected = op.indexOf(props.data.param.op)
    const x_type = computed(() => getInputType(props.id, 'x'))
    const y_type = computed(() => getInputType(props.id, 'y'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['result']?.type || 'default')
    const resultHasErr = computed(() => handleOutputError(props.id, 'result'))
    const errMsg = ref<string[]>([])
    const opHasErr = ref({
        id: 'op',
        value: false
    })
    const xHasErr = ref({
        handleId: 'x',
        value: false
    })
    const yHasErr = ref({
        handleId: 'y',
        value: false
    })


    const onSelectChange = (e: any) => {
        const selected_op = op[e] as 'AND' | 'OR' | 'XOR' | 'SUB'
        props.data.param.op = selected_op
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, opHasErr)
        handleValidationError(props.id, props.data.error, errMsg, xHasErr, yHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .BoolBinOpNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-x, .input-y {
                margin-bottom: $node-margin;
            }
            .op {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $bool-color;
    }
</style>
