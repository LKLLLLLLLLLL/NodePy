<template>
    <div class="LowerOrUpperNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='stringProcess'>大小写转换节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-input port">
                <div class="input-port-description">
                    字符串输入
                </div>
                <Handle id="input" type="target" :position="Position.Left" :class="[`${input_type}-handle-color`, {'node-errhandle': inputHasErr.value}]"/>
            </div>
            <div class="to_case port">
                <div class="param-description" :class="{'node-has-paramerr': to_caseHasErr.value}">
                    转换类型
                </div>
                <NodepySelectFew
                    :options="to_caseChinese"
                    :default-selected="defaultSelected"
                    @select-change="onSelectChange"
                    class="nodrag"
                />
            </div>
            <div class="output-output port">
                <div class="output-port-description">
                    字符串输出
                </div>
                <Handle id="output" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': outputHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import {ref, computed, watch} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import { getInputType } from '../getInputType'
    import type { Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepySelectFew from '../tools/Nodepy-selectFew.vue'
    import type { LowerOrUpperNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<LowerOrUpperNodeData>>()
    const input_type = computed(() => getInputType(props.id, 'input'))
    const to_case = ['lower', 'upper']
    const to_caseChinese = ['小写', '大写']
    const defaultSelected = [to_case.indexOf(props.data.param.to_case)]
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['output']?.type || 'default')
    const outputHasErr = computed(() => handleOutputError(props.id, 'output'))
    const errMsg = ref<string[]>([])
    const to_caseHasErr = ref({
        id: 'to_case',
        value: false
    })
    const inputHasErr = ref({
        handleId: 'input',
        value: false
    })


    const onSelectChange = (e: any) => {
        props.data.param.to_case = to_case[e[0]] as 'lower' | 'upper'
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, to_caseHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .LowerOrUpperNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-input {
                margin-bottom: $node-margin;
            }
            .to_case {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $str-color;
    }
</style>