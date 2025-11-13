<template>
    <div class="NumBinComputeNodeLayout nodes-style" :class="{'nodes-selected': selected}">
        <div class="node-title-compute nodes-topchild-border-radius">数字二元运算节点</div>
        <div class="data" :class="{'node-has-paramerr': hasParamerr}">
            <div class="input-x port">
                <div class="input-port-description">
                    x输入端口
                </div>
                <Handle id="x" type="target" :position="Position.Left" :class="[`${x_type}-handle-color`, {'node-errhandle': xHasErr.value}]"/>
            </div>
            <div class="input-y port">
                <div class="input-port-description">
                    y输入端口
                </div>
                <Handle id="y" type="target" :position="Position.Left" :class="[`${y_type}-handle-color`, {'node-errhandle': yHasErr.value}]"/>
            </div>
            <div class="op">
                <div class="op-description">
                    运算类型
                </div>
                <NodepySelectMany 
                    :options="op"
                    :default-selected="defaultSelected"
                    @select-change="onSelectChange"
                    width="100%"
                    class="nodrag"
                />
            </div>
            <div class="output-result port">
                <div class="output-port-description">
                    结果输出端口
                </div>
                <Handle id="result" type="source" :position="Position.Right" :class="`${schema_type}-handle-color`"/>
            </div>
        </div>
        <div class="node-err">
            <div v-for="err in errMsg">
                {{ err }}
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref, computed, watch} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import type {NumberBinOpNodeData} from '../../types/nodeTypes'
    import NodepySelectMany from './tools/Nodepy-selectMany.vue'
    import { getInputType } from './getInputType'
    import type { Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError } from './handleError'


    const props = defineProps<NodeProps<NumberBinOpNodeData>>()
    const op = ['ADD', 'SUB', 'MUL', 'DIV', 'POW']
    const defaultSelected = op.indexOf(props.data.param.op)
    const x_type = computed(() => getInputType(props.id, 'x'))
    const y_type = computed(() => getInputType(props.id, 'y'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['result']?.type || 'default')
    const errMsg = ref<string[]>([])
    const hasParamerr = ref(false)
    const xHasErr = ref({
        handleId: 'x',
        value: false
    })
    const yHasErr = ref({
        handleId: 'y',
        value: false
    })


    const onSelectChange = (e: any) => {
        const selected_op = op[e] as 'ADD' | 'SUB' | 'MUL' | 'DIV' | 'POW'
        props.data.param.op = selected_op
    }


    watch(() => JSON.stringify(props.data.error), () => {
        handleExecError(props.data.error, errMsg)
        handleParamError(hasParamerr, props.data.error, errMsg)
        handleValidationError(props.id, props.data.error, errMsg, xHasErr, yHasErr)
    })

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .NumBinComputeNodeLayout {
        height: 100%;
        width: $node-width;
        background: white;
        position: relative;
        .data {
            padding-top: $node-padding;
            padding-bottom: 5px;
            .input-x {
                margin-bottom: $node-margin;
            }
            .input-y {
                margin-bottom: $node-margin;
            }
            .op {
                padding: 0 $node-padding;
            }
            .output-result {
                margin-top: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: linear-gradient(to bottom, $int-color 0 50%, $float-color 50% 100%);
    }
</style>