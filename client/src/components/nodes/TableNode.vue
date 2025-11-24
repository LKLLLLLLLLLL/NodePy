<template>
    <div class="TableNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="input">表格节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <Handle id="table" type="source" :position="Position.Right" class="table-handle-color"/>
            渲染表格的地方
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import type {TableNodeData} from '../../types/nodeTypes'
    import NodeTitle from './tools/NodeTitle.vue'
    import Timer from './tools/Timer.vue'


    const props = defineProps<NodeProps<TableNodeData>>()

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .TableNodeLayout{
        height: 100%;
        width: 100%;
        background: white;
        .data {
            position: relative;
        }
    }
</style>