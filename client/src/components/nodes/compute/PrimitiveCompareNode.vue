<template>
    <div class="PrimitiveCompareNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="compute">比较节点</NodeTitle>
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
    import type { Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import type { PrimitiveCompareNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<PrimitiveCompareNodeData>>()
    const op = ['EQ', 'NEQ', 'LT', 'LTE', 'GT', 'GTE']
    const opChinese = ['等于', '不等于', '小于', '小于等于', '大于', '大于等于']
    const defaultSelected = op.indexOf(props.data.param.op)
    const x_type = computed(() => getInputType(props.id, 'x'))
    const y_type = computed(() => getInputType(props.id, 'y'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['result']?.type || 'default')
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
        const selected_op = op[e] as 'EQ' | 'NEQ' | 'LT' | 'LTE' | 'GT' | 'GTE'
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
    .PrimitiveCompareNodeLayout {
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
        background: conic-gradient(
                $int-color 0 120deg, 
                $float-color 0 240deg, 
                $bool-color 0 360deg
            );
    }
</style>