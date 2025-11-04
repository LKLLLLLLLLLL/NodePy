<template>
    <div class="ConstNodeLayout nodes-style" :class="{'nodes-selected': selected}">
        <div class="node-title nodes-topchild-border-radius">常量节点</div>
        <div class="data">
            <Handle id="const" type="source" :position="Position.Right" :class="`${schema_type}-handle-color`"/>
            <div class="value">
                 <NodepyNumberInput v-model="value" class="nodrag" @update-value="onUpdateValue"/>
            </div>
            <div class="data_type">
                <NodepySelectFew 
                    :options="data_type_options" 
                    :select-max-num="1" 
                    :defualt-selected="defaultSelected"
                    @select-change="onSelectChange"
                    item-width="90px"
                    class="nodrag"
                />
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref, computed } from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import type {ConstNodeData} from '../../types/nodeTypes'
    import type { Type } from '@/utils/api'
    import NodepyNumberInput from './tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import NodepySelectFew from './tools/Nodepy-selectFew.vue'


    const props = defineProps<NodeProps<ConstNodeData>>()
    const value = ref(props.data.param.value)
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['const']?.type || 'default')
    const data_type_options = ['int', 'float']
    const defaultSelected = [data_type_options.indexOf(props.data.param.data_type)]


    const onSelectChange = (e: any) => {
        const data_type = data_type_options[e.value[0]] as 'int' | 'float'
        props.data.param.data_type = data_type
    }

    const onUpdateValue = () => {
        props.data.param.value = Number(value.value)        
    }

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;

    .ConstNodeLayout {
        height: 100%;
        width: $node-width;
        background: white;
        .data {
            position: relative;
            padding: 5px 0;
            .value {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 0 10px;
            }
            .data_type {
                display: flex;
                justify-content: center;
                margin-top: 5px;
                padding: 0 10px;
            }
        }    
    }

</style>