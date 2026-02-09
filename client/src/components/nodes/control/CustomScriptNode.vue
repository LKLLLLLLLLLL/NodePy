<template>
    <div class="CustomScriptNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='control'>自定义脚本</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <template v-for="(inputPort, idx) in inputPorts" :key="inputPort.id">
                <div class="input-data port">
                    <div class="input-port-description">
                        输入
                        <hr></hr>
                    </div>
                    <Handle :id="inputPort.name" type="target" :position="Position.Left" :class="[`${inputPort.type}-handle-color`, {'node-errhandle': inputHasErr[idx]!.value.value}]" :key="inputPort.name"/>
                </div>
                <div class="name">
                    <div class="param-description port-name-description" :class="{'node-has-paramerr': input_portsHasErr.value}">
                        <span class="input-port-label">名称</span>
                        <NodepyCross v-if="inputPorts.length > 1" :handle-click="() => removeInputPort(idx)" class="port-close"/>
                    </div>
                    <NodepyStringInput
                        v-model="inputPort.name"
                        @update-value="(oldName: string) => onUpdateInputPortName(idx, oldName)"
                        class="nodrag"
                        placeholder="端口名称"
                    />
                </div>
                <div class="type">
                    <div class="param-description" :class="{'node-has-paramerr': input_portsHasErr.value}">类型</div>
                    <NodepySelectMany
                        :options="portTypeChinese"
                        :default-selected="inputPort.defaultSelectedType"
                        @select-change="(e) => onUpdateInputPortType(e, idx)"
                        class="nodrag"
                    />
                </div>
            </template>
            <div class="addInputPort">
                <NodepyButton :handle-click="addInputPort">
                    <NodepyPlus/>
                    添加输入
                </NodepyButton>
            </div>
            <div class="script">
                <div class="param-description" :class="{'node-has-paramerr': scriptHasErr.value}">自定义Python脚本</div>
                <NodepyButton :handle-click="openEditorModal">
                    编辑脚本
                </NodepyButton>
            </div>
            <template v-for="(outputPort, idx) in outputPorts" :key="outputPort.id">
                <div class="output-data port">
                    <div class="output-port-description">
                        输出
                        <hr></hr>
                    </div>
                    <Handle :id="outputPort.name" type="source" :position="Position.Right" :class="[`${outputPort.type}-handle-color`, {'node-errhandle': outPutHasErr[idx]}]" :key="outputPort.name"/>
                </div>
                <div class="name">
                    <div class="param-description port-name-description" :class="{'node-has-paramerr': output_portsHasErr.value}">
                        <span class="output-port-label">名称</span>
                        <NodepyCross v-if="outputPorts.length > 1" :handle-click="() => removeOutputPort(idx)" class="port-close"/>
                    </div>
                    <NodepyStringInput
                        v-model="outputPort.name"
                        @update-value="(oldName: string) => onUpdateOutputPortName(oldName, idx)"
                        class="nodrag"
                        placeholder="端口名称"
                    />
                </div>
                <div class="type">
                    <div class="param-description" :class="{'node-has-paramerr': output_portsHasErr.value}">类型</div>
                    <NodepySelectMany
                        :options="portTypeChinese"
                        :default-selected="outputPort.defaultSelectedType"
                        @select-change="(e) => onUpdateOutputPortType(e, idx)"
                        class="nodrag"
                    />
                </div>
            </template>
            <div class="addOutputPort">
                <NodepyButton :handle-click="addOutputPort">
                    <NodepyPlus/>
                    添加输出
                </NodepyButton>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import type { NodeProps } from '@vue-flow/core'
    import { Handle, Position, useVueFlow } from '@vue-flow/core'
    import { computed, ref, watch } from 'vue'
    import { handleExecError, handleParamError, handleValidationError, handleOutputError } from '../handleError'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import NodepySelectMany from '../tools/Nodepy-selectMany.vue'
    import NodepyButton from '../tools/Nodepy-button.vue'
    import NodepyCross from '../tools/Nodepy-cross.vue'
    import NodepyPlus from '../tools/Nodepy-plus.vue'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import type { CustomScriptNodeData } from '@/types/nodeTypes'
    import { useEditorStore } from '@/stores/editorStore'

    const editorStore = useEditorStore()
    const {removeEdges, getEdges} = useVueFlow()
    const props = defineProps<NodeProps<CustomScriptNodeData>>()
    const portType = ["int", "float", "bool", "str", "Datetime"]
    const portTypeChinese = ["整数", "浮点数", "布尔值", "字符串", "时间"]
    const inputPorts = ref(Object.entries(props.data.param.input_ports).map(([name, type], idx) => {
        return {
            id: Date.now().toString()+`_${idx}`,
            name,
            type,
            defaultSelectedType: portType.indexOf(type)
        }
    }))
    const outputPorts = ref(Object.entries(props.data.param.output_ports).map(([name, type], idx) => {
        return {
            id: Date.now().toString()+`_${idx}`,
            name,
            type,
            defaultSelectedType: portType.indexOf(type)
        }
    }))
    const outPutHasErr = computed(() => {
        return outputPorts.value.map((port) => handleOutputError(props.id, port.name))
    })
    const errMsg = ref<string[]>([])
    const inputHasErr = inputPorts.value.map((port) => {
        return ref({
            handleId: port.name,
            value: false
        })
    })
    const input_portsHasErr = ref({
        id: 'input_ports',
        value: false
    })
    const output_portsHasErr = ref({
        id: 'output_ports',
        value: false
    })
    const scriptHasErr = ref({
        id: 'script',
        value: false
    })


    const removeInputPort = (idx: number) => {
        if(inputPorts.value.length > 1) {
            const removedKey = inputPorts.value[idx]!.name
            removeEdges(edges => edges.filter(e => e.target === props.id && e.targetHandle === removedKey))
            inputPorts.value.splice(idx, 1)
            const {[removedKey]: _, ...rest} = props.data.param.input_ports
            props.data.param.input_ports = rest
            inputHasErr.splice(idx, 1)
        }
    }
    const removeOutputPort = (idx: number) => {
        if(outputPorts.value.length > 1) {
            const removedKey = outputPorts.value[idx]!.name
            removeEdges(edges => edges.filter(e => e.source === props.id && e.sourceHandle === removedKey))
            outputPorts.value.splice(idx, 1)
            const {[removedKey]: _, ...rest} = props.data.param.output_ports
            props.data.param.output_ports = rest
        }
    }
    const addInputPort = () => {
        inputPorts.value.push({
            id: Date.now().toString()+`_${inputPorts.value.length}`,
            name: '输入'+inputPorts.value.length,
            type: 'int',
            defaultSelectedType: 0
        })
        props.data.param.input_ports[inputPorts.value[inputPorts.value.length-1]!.name] = 'int'
        inputHasErr.push(ref({
            handleId: inputPorts.value[inputPorts.value.length-1]!.name,
            value: false
        }))
    }
    const addOutputPort = () => {
        outputPorts.value.push({
            id: Date.now().toString()+`_${outputPorts.value.length}`,
            name: '输出'+outputPorts.value.length,
            type: 'int',
            defaultSelectedType: 0
        })
        props.data.param.output_ports[outputPorts.value[outputPorts.value.length-1]!.name] = 'int'
    }
    const openEditorModal = () => {
        window.addEventListener('ApplyEditorChanges', () => {
            updateScript()
        },{once: true})
        editorStore.currentScript = JSON.parse(JSON.stringify(props.data.param.script || props.data.hint?.script_template || ''))
        editorStore.createEditorModal()
    }
    const updateScript = () => {
        props.data.param.script = JSON.parse(JSON.stringify(editorStore.currentScript))
    }
    const onUpdateInputPortName = (idx: number, oldName: string) => {
        if(oldName === inputPorts.value[idx]!.name) return
        const curEdge = getEdges.value.find(e => e.target === props.id && e.targetHandle === oldName)
        if(curEdge) {
            removeEdges(curEdge.id)
        }
        props.data.param.input_ports = inputPorts.value.reduce((acc, cur) => {
            acc[cur.name] = cur.type
            return acc
        }, {})
        inputHasErr[idx]!.value.handleId = inputPorts.value[idx]!.name
    }
    const onUpdateOutputPortName = (oldName: string, idx: number) => {
        if(oldName === outputPorts.value[idx]!.name) return
        const curEdge = getEdges.value.find(e => e.source === props.id && e.sourceHandle === oldName)
        if(curEdge) {
            removeEdges(curEdge.id)
        }
        props.data.param.output_ports = outputPorts.value.reduce((acc, cur) => {
            acc[cur.name] = cur.type
            return acc
        }, {})
    }
    const onUpdateInputPortType = (portTypeIdx: number, idx: number) => {
        props.data.param.input_ports[inputPorts.value[idx]!.name] = portType[portTypeIdx] as 'int' | 'float' | 'bool' | 'str' | 'Datetime'
        inputPorts.value[idx]!.type = portType[portTypeIdx] as 'int' | 'float' | 'bool' | 'str' | 'Datetime'
    }
    const onUpdateOutputPortType = (portTypeIdx: number, idx: number) => {
        props.data.param.output_ports[outputPorts.value[idx]!.name] = portType[portTypeIdx] as 'int' | 'float' | 'bool' | 'str' | 'Datetime'
        outputPorts.value[idx]!.type = portType[portTypeIdx] as 'int' | 'float' | 'bool' | 'str' | 'Datetime'
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, input_portsHasErr, output_portsHasErr, scriptHasErr)
        handleValidationError(props.id, props.data.error, errMsg, ...inputHasErr)
    }, {immediate: true})
    
</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .CustomScriptNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-data {
                margin-bottom: $node-margin - 7px;
            }
            .name, .type, .script, .addInputPort, .addOutputPort {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
            .output-data {
                margin-bottom: $node-margin - 7px;
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
    .input-port-description, .output-port-description {
        padding: 0 $node-padding-hor;
    }
</style>