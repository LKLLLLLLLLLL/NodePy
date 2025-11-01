<template>
    <div class="NumBinComputeNodeLayout nodes-style" :class="{'nodes-selected': selected}">
        <div class="title nodes-topchild-border-radius">NumberBinOpNode</div>
        <div class="data">
            <Handle id="x" type="target" :position="Position.Left" style="top: 25%" :class="`${x_type}-handle-color`"/>
            <Handle id="y" type="target" :position="Position.Left" style="top: 75%" :class="`${y_type}-handle-color`"/>
            <Handle id="result" type="source" :position="Position.Right" :class="`${schema_type}-handle-color`"/>
            <div class="op">
                <NodepySelectFew
                    :options="op"
                    :defualt-selected="defaultSelected"
                    @select-change="onSelectChange"
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
    import NodepySelectFew from './tools/Nodepy-selectFew.vue'
    import { getInputType } from './getInputType'
    import type { Type } from '@/utils/api'


    const props = defineProps<NodeProps<NumberBinOpNodeData>>()
    const op = ['ADD', 'SUB', 'MUL', 'DIV', 'POW']
    const defaultSelected = [op.indexOf(props.data.param.op)]
    const x_type = computed(() => getInputType(props.id, 'x'))
    const y_type = computed(() => getInputType(props.id, 'y'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['result']?.type || 'default')


    const onSelectChange = (e: any) => {
        const selected_op = op[e.value[0]] as 'ADD' | 'SUB' | 'MUL' | 'DIV' | 'POW'
        props.data.param.op = selected_op
    }

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .NumBinComputeNodeLayout {
        height: 100%;
        width: 100%;
        background: white;
        .title {
            background: #ccc;
            text-align: left;
            padding-left: 8px;
        }
        .data {
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            padding: 10px 0;
            .op {
                padding: 0 10px;
            }
        }  
    }
    .all-handle-color {
        background: conic-gradient($int-color 180deg, $float-color 180deg 360deg);
    }
</style>

<style lang="scss">
    @import '@vue-flow/node-resizer/dist/style.css';
</style>
