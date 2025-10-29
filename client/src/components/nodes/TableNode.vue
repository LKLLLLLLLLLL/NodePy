<template>
    <div class="TableNodeLayout nodes-style" :class="{'nodes-selected': selected}">
        <div class="title nodes-topchild-border-radius">TableNode</div>
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


    const props = defineProps<NodeProps<TableNodeData>>()

</script>

<style lang="scss" scoped>
    @use '../../common/style/global.scss' as *;
    @use '../../common/style/node.scss' as *;
    .TableNodeLayout{
        height: 100%;
        width: 100%;
        background: white;
        .title {
            background: #ccc;
            text-align: left;
            padding-left: 8px;
        }
        .data {
            position: relative;
        }
    }
</style>

<style lang="scss">
    @import '@vue-flow/node-resizer/dist/style.css';
</style>
