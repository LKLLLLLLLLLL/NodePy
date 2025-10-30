<template>
    <div class="ConstNodeLayout nodes-style" :class="{'nodes-selected': selected}">
        <div class="title nodes-topchild-border-radius">ConstNode</div>
        <div class="data">
            <Handle id="const" type="source" :position="Position.Right" :class="`${schema_type}-handle-color`"/>
            <div class="value">
                 <NodepyNumberInput v-model="value" class="nodrag" @update-value="onUpdateValue"/>
            </div>
            <div class="data_type">
                <select v-model="data_type" class="border-radius nodrag">
                    <option v-for="item in data_type_options">{{ item }}</option>
                </select>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref, watch, computed } from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import type {ConstNodeData} from '../../types/nodeTypes'
    import type { Type } from '@/utils/api'
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'


    const props = defineProps<NodeProps<ConstNodeData>>()
    const value = ref(props.data.param.value)
    const data_type = ref(props.data.param.data_type)
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['const']?.type || 'default')
    const data_type_options = ['int', 'float']

    watch(data_type, (newValue, oldValue) => {
        props.data.param.data_type = data_type.value
        props.data.param.value = Number(value.value)
    })


    const onUpdateValue = () => {
        props.data.param.data_type = data_type.value
        props.data.param.value = Number(value.value)        
    }

</script>

<style lang="scss" scoped>
    @use '../../common/style/global.scss' as *;
    @use '../../common/style/node.scss' as *;

    .ConstNodeLayout {
        height: 100%;
        width: 200px;
        background: white;
        .title {
            background: #ccc;
            text-align: left;
            padding-left: 8px;
            height: 30px;
        }
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
                margin-top: 5px;
                display: flex;
                justify-content: center;
                select {
                    border: 1px solid #ccc;
                    appearance: auto;
                    padding-left: 10px;
                    height: 24px;
                }
            }
        }    
    }

</style>
