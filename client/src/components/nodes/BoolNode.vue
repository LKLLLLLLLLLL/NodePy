<template>
    <div class="BoolNodeLayout nodes-style" :class="{'nodes-selected': selected}">
        <div class="node-title nodes-topchild-border-radius">布尔节点</div>
        <div class="data">
            <Handle id="const" type="source" :position="Position.Right" :class="`${schema_type}-handle-color`"/>
            <div class="value">
                <NodepyBoolValue
                    v-model="value"
                    @update-value="onUpdateValue"
                    width="40px"
                    height="40px"
                    class="nodrag"
                />
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import { Position, Handle } from '@vue-flow/core'
    import {ref, computed } from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import type {BoolNodeData} from '../../types/nodeTypes'
    import type { Type } from '@/utils/api'
    import NodepyBoolValue from './tools/Nodepy-boolValue.vue'


     const props = defineProps<NodeProps<BoolNodeData>>()
     const value = ref(props.data.param.value)
     const schema_type = computed(():Type|'default' => props.data.schema_out?.['const']?.type || 'default')


    const onUpdateValue = () => {
        props.data.param.value = value.value
    }

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .BoolNodeLayout {
        height: 100%;
        width: $node-width;
        background: white;
        .data {
            position: relative;
            padding: 5px 0;
            .value {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 0 10px;
            }
        }
    }
</style>