<template>
    <div class="ConstNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="input">常量节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
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
                    :options="data_type_options_chinese"
                    :default-selected="defaultSelected"
                    @select-change="onSelectChange"
                    class="nodrag"
                />
            </div>
            <div class="output-const port">
                <div class="output-port-description">
                    常量输出
                </div>
                <Handle id="const" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': constHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import type { Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Handle, Position } from '@vue-flow/core'
    import { computed, ref, watch } from 'vue'
    import type { ConstNodeData } from '../../../types/nodeTypes'
    import { handleExecError, handleOutputError, handleParamError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import NodepySelectFew from '../tools/Nodepy-selectFew.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'


    const props = defineProps<NodeProps<ConstNodeData>>()
    const value = ref(props.data.param.value)
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['const']?.type || 'default')
    const constHasErr = computed(() => handleOutputError(props.id, 'const'))
    const data_type_options = ['int', 'float']
    const data_type_options_chinese = ['整数', '浮点数']
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
        props.data.param.value = value.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, valueHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;

    .ConstNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .value {
                padding: 0 $node-padding-hor;
            }
            .data_type {
                margin-top: $node-margin;
                padding: 0 $node-padding-hor;
            }
            .output-const {
                margin-top: $node-margin;
            }
        }
    }

</style>
