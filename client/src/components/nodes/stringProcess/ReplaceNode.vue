<template>
    <div class="ReplaceNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='stringProcess'>字符串替换</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-input port">
                <div class="input-port-description">
                    字符串输入
                </div>
                <Handle id="input" type="target" :position="Position.Left" :class="[`${input_type}-handle-color`, {'node-errhandle': inputHasErr.value}]"/>
            </div>
            <div class="input-old port">
                <div class="input-port-description" :class="{'node-has-paramerr': oldHasErr.value}">
                    旧字符串
                </div>
                <Handle id="old" type="target" :position="Position.Left" :class="[`${inputOld_type}-handle-color`, {'node-errhandle': inputOldHasErr.value}]"/>
            </div>
            <div class="old">
                <NodepyStringInput
                    v-model="old"
                    @update-value="onUpdateOld"
                    :disabled="oldDisabled"
                    class="nodrag"
                    placeholder="旧字符串"
                />
            </div>
            <div class="input-new port">
                <div class="input-port-description" :class="{'node-has-paramerr': newHasErr.value}">
                    新字符串
                </div>
                <Handle id="new" type="target" :position="Position.Left" :class="[`${inputNew_type}-handle-color`, {'node-errhandle': inputNewHasErr.value}]"/>
            </div>
            <div class="new">
                <NodepyStringInput
                    v-model="New"
                    @update-value="onUpdateNew"
                    :disabled="newDisabled"
                    class="nodrag"
                    placeholder="新字符串"
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
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import { hasInputEdge } from '../hasEdge'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import type { ReplaceNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<ReplaceNodeData>>()
    const old = ref(props.data.param.old)
    const oldDisabled = computed(() => hasInputEdge(props.id, 'old'))
    const New = ref(props.data.param.new)
    const newDisabled = computed(() => hasInputEdge(props.id, 'new'))
    const input_type = computed(() => getInputType(props.id, 'input'))
    const inputOld_type = computed(() => getInputType(props.id, 'old'))
    const inputNew_type = computed(() => getInputType(props.id, 'new'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['output']?.type || 'default')
    const outputHasErr = computed(() => handleOutputError(props.id, 'output'))
    const errMsg = ref<string[]>([])
    const oldHasErr = ref({
        id: 'old',
        value: false
    })
    const newHasErr = ref({
        id: 'new',
        value: false
    })
    const inputHasErr = ref({
        handleId: 'input',
        value: false
    })
    const inputOldHasErr = ref({
        handleId: 'old',
        value: false
    })
    const inputNewHasErr = ref({
        handleId: 'new',
        value: false
    })


    const onUpdateOld = (e: any) => {
        props.data.param.old = old.value
    }
    const onUpdateNew = (e: any) => {
        props.data.param.new = New.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, oldHasErr, newHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputHasErr, inputOldHasErr, inputNewHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .ReplaceNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-input {
                margin-bottom: $node-margin;
            }
            .input-old, .input-new {
                margin-bottom: 2px;
            }
            .old, .new {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $str-color;
    }
</style>
