<template>
    <div class="NumBinComputeNodeLayout nodes-style" :class="{'nodes-selected': selected}">
        <div class="title nodes-topchild-border-radius">NumBinComputeNode</div>
        <div class="data">
            <Handle id="x" type="target" :position="Position.Left" style="top: 25%"/>
            <Handle id="y" type="target" :position="Position.Left" style="top: 75%"/>
            <Handle id="result" type="source" :position="Position.Right"/>
            <div class="op">
                <select v-model="selected_op" @change="onSelect" class="border-radius nodrag">
                    <option v-for="item in NumBinOpList">{{ item }}</option>
                </select>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import type {NumberBinOpNodeData} from '../../types/nodeTypes'
    import { NumBinOpList } from '../../types/nodeTypes'


    const props = defineProps<NodeProps<NumberBinOpNodeData>>()
    const selected_op = ref(props.data.param.op)


    const onSelect = (e?: Event) => {
        props.data.param.op = selected_op.value
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
                select {
                    border: 1px solid #ccc;
                    padding-left: 5px;
                    appearance: auto;
                    width: 100%;
                }
            }
        }  
    }
</style>

<style lang="scss">
    @import '@vue-flow/node-resizer/dist/style.css';
</style>
