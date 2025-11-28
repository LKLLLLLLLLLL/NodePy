<template>
    <div class="ToIntNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="compute">整数转换节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-input port">
                <div class="input-port-description">
                    数据输入
                </div>
                <Handle
                    id="input"
                    type="target"
                    :position="Position.Left"
                    :class="[`${input_type}-handle-color`, {'node-errhandle': inputHaserr.value}]"
                />
            </div>
            <div class="method">
                <div class="param-description" :class="{'node-has-paramerr': methodHasErr.value}">
                    转换方法
                </div>
                <NodepySelectFew
                    :options="methodChinese"
                    :default-selected="defaultSelected"
                    @select-change="onSelectChange"
                    class="nodrag"
                />
            </div>
            <div class="output-output port">
                <div class="output-port-description">
                    字符串输出
                </div>
                <Handle
                    id="output"
                    type="source"
                    :position="Position.Right"
                    :class="[`${schema_type}-handle-color`, {'node-errhandle': outputHasErr}]"
                />
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
    import { getInputType } from './getInputType'
    import { handleExecError, handleValidationError, handleOutputError, handleParamError } from './handleError'
    import ErrorMsg from './tools/ErrorMsg.vue'
    import NodeTitle from './tools/NodeTitle.vue'
    import Timer from './tools/Timer.vue'
    import NodepySelectFew from './tools/Nodepy-selectFew.vue'
    import type { ToIntNodeData } from '../../types/nodeTypes'


    const props = defineProps<NodeProps<ToIntNodeData>>()
    const method = ["FLOOR", "CEIL", "ROUND"]
    const methodChinese = ["下取整", "上取整", "四舍五入"]
    const defaultSelected = [method.indexOf(props.data.param.method)]
    const input_type = computed(() => getInputType(props.id, 'input'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['output']?.type || 'default')
    const outputHasErr = computed(() => handleOutputError(props.id, 'output'))
    const methodHasErr = ref({
        id: 'method',
        value: false
    })
    const errMsg = ref<string[]>([])
    const inputHaserr = ref({
        handleId: 'input',
        value: false
    })


    const onSelectChange = (e: any) => {
        props.data.param.method = method[e[0]] as 'FLOOR'|'CEIL'|'ROUND'
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleValidationError(props.id, props.data.error, errMsg, inputHaserr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .ToIntNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-input {
                margin-bottom: $node-margin;
            }
            .method {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: conic-gradient(
            $float-color 0 120deg, 
            $bool-color 0 240deg, 
            $str-color 0 360deg
        );
    }
</style>