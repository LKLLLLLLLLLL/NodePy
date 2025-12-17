<template>
    <div class="JoinNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="tableProcess">连接</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-left_table port">
                <div class="input-port-description">
                    左表格
                </div>
                <Handle id="left_table" type="target" :position="Position.Left" :class="[`${left_table_type}-handle-color`, {'node-errhandle': left_tableHasErr.value}]"/>
            </div>
            <div class="input-right_table port">
                <div class="input-port-description">
                    右表格
                </div>
                <Handle id="right_table" type="target" :position="Position.Left" :class="[`${right_table_type}-handle-color`, {'node-errhandle': right_tableHasErr.value}]"/>
            </div>
            <div class="left_on">
                <div class="param-description" :class="{'node-has-paramerr': left_onHasErr.value}">
                    左键
                </div>
                <NodepySelectMany
                    :options="left_onHint"
                    :default-selected="defaultSelectedLeft_on"
                    @select-change="onSelectChangeLeft_on"
                    @clear-select="clearSelectLeft_on"
                    class="nodrag"
                />
            </div>
            <div class="right_on">
                <div class="param-description" :class="{'node-has-paramerr': right_onHasErr.value}">
                    右键
                </div>
                <NodepySelectMany
                    :options="right_onHint"
                    :default-selected="defaultSelectedRight_on"
                    @select-change="onSelectChangeRight_on"
                    @clear-select="clearSelectRight_on"
                    class="nodrag"
                />
            </div>
            <div class="how">
                <div class="param-description" :class="{'node-has-paramerr': howHasErr.value}">
                    连接方式
                </div>
                <NodepySelectMany
                    :options="howUi"
                    :default-selected="defaultSelectedHow"
                    @select-change="onSelectChangeHow"
                    class="nodrag"
                />
            </div>
            <div class="output-joined_table port">
                <div class="output-port-description">
                    表格输出
                </div>
                <Handle id="joined_table" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': joined_tableHasErr}]"/>
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
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import type { JoinNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<JoinNodeData>>()
    const left_onHint = computed(() => {
        if(props.data.hint?.left_on_choices?.length === 0) return ['']
        return props.data.hint?.left_on_choices || ['']
    })
    const left_on = ref(props.data.param.left_on)   //  used for defaultSelectedLeft_on
    const defaultSelectedLeft_on = computed(() => left_onHint.value.indexOf(left_on.value))
    const right_onHint = computed(() => {
        if(props.data.hint?.right_on_choices?.length === 0) return ['']
        return props.data.hint?.right_on_choices || ['']
    })
    const right_on = ref(props.data.param.right_on)   //  used for defaultSelectedRight_on
    const defaultSelectedRight_on = computed(() => right_onHint.value.indexOf(right_on.value))
    const how = ["INNER", "LEFT", "RIGHT", "OUTER"]
    const howUi = ["内连接", "左连接", "右连接", "外连接"]
    const defaultSelectedHow = how.indexOf(props.data.param.how)
    const left_table_type = computed(() => getInputType(props.id, 'left_table'))
    const right_table_type = computed(() => getInputType(props.id, 'right_table'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['joined_table']?.type || 'default')
    const joined_tableHasErr = computed(() => handleOutputError(props.id, 'joined_table'))
    const errMsg = ref<string[]>([])
    const left_onHasErr = ref({
        id: 'left_on',
        value: false
    })
    const right_onHasErr = ref({
        id: 'right_on',
        value: false
    })
    const howHasErr = ref({
        id: 'how',
        value: false
    })
    const left_tableHasErr = ref({
        handleId: 'left_table',
        value: false
    })
    const right_tableHasErr = ref({
        handleId: 'right_table',
        value: false
    })


    const onSelectChangeLeft_on = (e: any) => {
        props.data.param.left_on = left_onHint.value[e]
    }
    const clearSelectLeft_on = (resolve: any) => {
        props.data.param.left_on = ''
        left_on.value = props.data.param.left_on
        resolve()
    }
    const onSelectChangeRight_on = (e: any) => {
        props.data.param.right_on = right_onHint.value[e]
    }
    const clearSelectRight_on = (resolve: any) => {
        props.data.param.right_on = ''
        right_on.value = props.data.param.right_on
        resolve()
    }
    const onSelectChangeHow = (e: any) => {
        const selected_how = how[e] as 'INNER'|'LEFT'|'RIGHT'|'OUTER'
        props.data.param.how = selected_how
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, left_onHasErr, right_onHasErr, howHasErr)
        handleValidationError(props.id, props.data.error, errMsg, left_tableHasErr, right_tableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .JoinNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-left_table, .input-right_table {
                margin-bottom: $node-margin;
            }
            .left_on, .right_on, .how {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>
