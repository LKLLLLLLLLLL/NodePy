<template>
    <div class="PackNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='control'>打包</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-base_row port">
                <div class="input-port-description">
                    原表格行
                </div>
                <Handle id="base_row" type="target" :position="Position.Left" :class="[`${base_row_type}-handle-color`, {'node-errhandle': base_rowHasErr.value}]"/>
            </div>
            <template v-for="(inputPort, idx) in inputPorts" :key="inputPort.id">
                <div class="input-data port">
                    <div class="input-port-description">
                        输入
                        <hr></hr>
                    </div>
                    <Handle :id="inputPort.name" type="target" :position="Position.Left" :class="[`${colTypes[idx]}-handle-color`, {'node-errhandle': inputHasErr[idx]!.value.value}]" :key="inputPort.name"/>
                </div>
                <div class="name">
                    <div class="param-description port-name-description" :class="{'node-has-paramerr': colsHasErr.value}">
                        <span class="input-port-label">名称</span>
                        <NodepyCross v-if="inputPorts.length > 1" :handle-click="() => removeInputPort(idx)" class="port-close"/>
                    </div>
                    <NodepyStringInput
                        v-model="inputPort.name"
                        @update-value="(oldName: string) => onUpdateInputPortName(oldName, idx)"
                        class="nodrag"
                        placeholder="端口名称"
                    />
                </div>
            </template>
            <div class="addInputPort">
                <NodepyButton :handle-click="addInputPort">
                    <NodepyPlus/>
                    添加输入
                </NodepyButton>
            </div>
            <div class="output-packed_row port">
                <div class="output-port-description">
                    结果行
                </div>
                <Handle id="packed_row" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': packed_rowHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import {ref, computed, watch} from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle, useVueFlow } from '@vue-flow/core'
    import { getInputType } from '../getInputType'
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import NodepyButton from '../tools/Nodepy-button.vue'
    import NodepyCross from '../tools/Nodepy-cross.vue'
    import NodepyPlus from '../tools/Nodepy-plus.vue'
    import type { PackNodeData } from '@/types/nodeTypes'


    const {removeEdges, getEdges} = useVueFlow()
    const props = defineProps<NodeProps<PackNodeData>>()
    const inputPorts = ref(props.data.param.cols.map((name, idx) => {
        return {
            id: Date.now().toString()+`_${idx}`,
            name
        }
    }))
    const base_row_type = computed(() => getInputType(props.id, 'base_row'))
    const colTypes = computed(() => {
        return inputPorts.value.map(port => getInputType(props.id, port.name))
    })
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['packed_row']?.type || 'default')
    const packed_rowHasErr = computed(() => handleOutputError(props.id, 'packed_row'))
    const errMsg = ref<string[]>([])
    const base_rowHasErr = ref({
        handleId: 'base_row',
        value: false
    })
    const inputHasErr = inputPorts.value.map((port) => {
        return ref({
            handleId: port.name,
            value: false
        })
    })
    const colsHasErr = ref({
        id: 'cols',
        value: false
    })


    const removeInputPort = (idx: number) => {
        if(inputPorts.value.length > 1) {
            removeEdges(edges => edges.filter(e => e.target === props.id && e.targetHandle === inputPorts.value[idx]!.name))
            inputPorts.value.splice(idx, 1)
            props.data.param.cols.splice(idx, 1)
            inputHasErr.splice(idx, 1)
        }
    }
    const addInputPort = () => {
        inputPorts.value.push({
            id: Date.now().toString()+`_${inputPorts.value.length}`,
            name: '输入'+inputPorts.value.length
        })
        props.data.param.cols.push('输入'+props.data.param.cols.length)
        inputHasErr.push(ref({
            handleId: inputPorts.value[inputHasErr.length]!.name,
            value: false
        }))
    }
    const onUpdateInputPortName = (oldName: string, idx: number) => {
        if(oldName === inputPorts.value[idx]!.name) return
        const curEdge = getEdges.value.find(e => e.target === props.id && e.targetHandle === oldName)
        if(curEdge) {
            removeEdges(curEdge.id)
        }
        props.data.param.cols[idx] = inputPorts.value[idx]!.name
        inputHasErr[idx]!.value.handleId = inputPorts.value[idx]!.name
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, colsHasErr)
        handleValidationError(props.id, props.data.error, errMsg, base_rowHasErr, ...inputHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .PackNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-base_row {
                margin-bottom: $node-margin;
            }
            .input-data {
                margin-bottom: $node-margin - 7px;
            }
            .name, .addInputPort {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
            .name {
                .port-name-description {
                    display: flex;
                    align-items: center;
                    .port-close {
                        display: flex;
                        align-items: center;
                        cursor: pointer;
                        margin-left: auto;
                        border-radius: 4px;
                        &:hover {
                            background-color: #eee;
                        }
                    }
                }
            }
        }
    }
    .input-port-description {
        padding: 0 $node-padding-hor;
    }
    .all-handle-color {
        background: $default-type-color;
    }
    .all-handle-color[data-handleid='base_row'] {
        background: $table-color;
    }
</style>