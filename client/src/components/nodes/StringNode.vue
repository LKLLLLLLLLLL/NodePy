<template>
    <div class="StringNodeLayout nodes-style" :class="{'nodes-selected': selected}">
        <div class="title nodes-topchild-border-radius">StringNode</div>
        <div class="data">
            <Handle id="string" type="source" :position="Position.Right" class="str-handle-color"/>
            <NodepyStringInput 
                v-model="value" 
                :disabled="false" 
                @update-value="onUpdateValue" 
                class="nodrag"
            />
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import type {StringNodeData} from '../../types/nodeTypes'
    import NodepyStringInput from './tools/Nodepy-StringInput.vue'


    const props = defineProps<NodeProps<StringNodeData>>()
    const value = ref(props.data.param.value)


    const onUpdateValue = (e?: Event) => {
        props.data.param.value = value.value
    }

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .StringNodeLayout{
        height: 100%;
        width: 200px;
        background: white;
        .title {
            background: #ccc;
            text-align: left;
            padding-left: 8px;
        }
        .data {
            padding: 10px 20px;
            position: relative;
            display: flex;
            justify-content: center;
            .input {
                width: 90%;
                height: 20px !important;
            }
        }    
    }
</style>

<style lang="scss">
    @import '@vue-flow/node-resizer/dist/style.css';
</style>
