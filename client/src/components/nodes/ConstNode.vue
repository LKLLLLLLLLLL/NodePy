<template>
    <div class="ConstNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <div class="node-title-input nodes-topchild-border-radius">{{`常量节点${props.id.split('_')[1]}`}}</div>
        <div class="data">
            <div class="value">
                <div class="param-description" :class="{'node-has-paramerr': valueHasErr.value}">
                    数值
                </div>
                <NodepyNumberInput 
                    v-if="data_type == 'int'" 
                    v-model="value" 
                    class="nodrag" 
                    @update-value="onUpdateValue"
                 />
                <NodepyNumberInput 
                    v-else-if="data_type == 'float'" 
                    v-model="value" 
                    class="nodrag" 
                    @update-value="onUpdateValue"
                    :denominator="1000"
                />
            </div>
            <div class="data_type">
                <div class="param-description">
                    类型
                </div>
                <NodepySelectFew 
                    :options="data_type_options" 
                    :defualt-selected="defaultSelected"
                    @select-change="onSelectChange"
                    item-width="90px"
                    class="nodrag"
                />
            </div>
            <div class="output-const port">
                <div class="output-port-description">
                    常量输出端口
                </div>
                <Handle id="const" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': constHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import {ref, computed, watch } from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import type {ConstNodeData} from '../../types/nodeTypes'
    import type { Type } from '@/utils/api'
    import NodepyNumberInput from './tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import NodepySelectFew from './tools/Nodepy-selectFew.vue'
    import { handleParamError, handleExecError, handleOutputError } from './handleError'
    import ErrorMsg from './tools/ErrorMsg.vue'


    const props = defineProps<NodeProps<ConstNodeData>>()
    const value = ref(props.data.param.value)
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['const']?.type || 'default')
    const constHasErr = computed(() => handleOutputError(props.id, 'const'))
    const data_type_options = ['int', 'float']
    const defaultSelected = [data_type_options.indexOf(props.data.param.data_type)]
    const data_type = ref(props.data.param.data_type)
    const errMsg = ref<string[]>([])
    const valueHasErr = ref({
        id: 'value',
        value: false
    })


    const onSelectChange = (e: any) => {
        data_type.value = data_type_options[e[0]] as 'int' | 'float'
        props.data.param.data_type = data_type.value
        if(data_type.value == 'int') {
            value.value = Math.floor(value.value)
            props.data.param.value = value.value
        }
    }

    const onUpdateValue = () => {
        props.data.param.value = Number(value.value)        
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, valueHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;

    .ConstNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding;
            padding-bottom: 5px;
            .value {
                padding: 0 $node-padding;
            }
            .data_type {
                margin-top: $node-margin;
                padding: 0 $node-padding;
            }
            .output-const {
                margin-top: $node-margin;
            }
        }    
    }

</style>