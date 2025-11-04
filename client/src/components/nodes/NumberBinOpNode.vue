<template>
    <div class="NumBinComputeNodeLayout nodes-style" :class="{'nodes-selected': selected}">
        <div class="node-title nodes-topchild-border-radius">数字二元运算节点</div>
        <div class="data">
            <Handle id="x" type="target" :position="Position.Left" style="top: 25%" :class="`${x_type}-handle-color`"/>
            <Handle id="y" type="target" :position="Position.Left" style="top: 75%" :class="`${y_type}-handle-color`"/>
            <Handle id="result" type="source" :position="Position.Right" :class="`${schema_type}-handle-color`"/>
            <div class="op">
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
            .op {
                display: flex;
                justify-content: center;
                padding: 0 10px;
            }
        }
    }
    .all-handle-color {
        background: linear-gradient(to bottom, $int-color 0 50%, $float-color 50% 100%);
    }
</style>