<template>
    <div class="NumBinComputeNodeLayout nodes-style" :class="{'nodes-selected': selected}">
        <div class="node-title-compute nodes-topchild-border-radius">数字二元运算节点</div>
        <div class="data">
            <Handle id="result" type="source" :position="Position.Right" :class="`${schema_type}-handle-color`"/>
            <div class="input-x">
                <div class="x-description">
                    x输入端口
                </div>
                <Handle id="x" type="target" :position="Position.Left" :class="`${x_type}-handle-color`"/>
            </div>
            <div class="input-y">
                <div class="y-description">
                    y输入端口
                </div>
                <Handle id="y" type="target" :position="Position.Left" :class="`${y_type}-handle-color`"/>
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
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {computed} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import type {NumberBinOpNodeData} from '../../types/nodeTypes'
    import NodepySelectMany from './tools/Nodepy-selectMany.vue'
    import { getInputType } from './getInputType'
    import type { Type } from '@/utils/api'


    const props = defineProps<NodeProps<NumberBinOpNodeData>>()
    const op = ['ADD', 'SUB', 'MUL', 'DIV', 'POW']
    const defaultSelected = op.indexOf(props.data.param.op)
    const x_type = computed(() => getInputType(props.id, 'x'))
    const y_type = computed(() => getInputType(props.id, 'y'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['result']?.type || 'default')


    const onSelectChange = (e: any) => {
        const selected_op = op[e] as 'ADD' | 'SUB' | 'MUL' | 'DIV' | 'POW'
        props.data.param.op = selected_op
    }

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .NumBinComputeNodeLayout {
        height: 100%;
        width: $node-width;
        background: white;
        .data {
            position: relative;
            padding: 10px 0;
            .input-x {
                position: relative;
                margin-bottom: 10px;
                .x-description {
                    padding-left: $node-padding-left;
                }
            }
            .input-y {
                position: relative;
                .y-description {
                    padding-left: $node-padding-left;
                }
                margin-bottom: 10px;
            }
            .op {
                padding: 0 $node-padding-left;
            }
        }
    }
    .all-handle-color {
        background: linear-gradient(to bottom, $int-color 0 50%, $float-color 50% 100%);
    }
</style>