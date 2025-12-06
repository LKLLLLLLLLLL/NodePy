<template>
    <div class="RangeNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="input">范围表格生成节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-start port">
                <div class="input-port-description">
                    起始值
                </div>
                <Handle id="start" type="target" :position="Position.Left" :class="[`${start_type}-handle-color`, {'node-errhandle': startHasErr.value}]"/>
            </div>
            <div class="input-end port">
                <div class="input-port-description">
                    结束值
                </div>
                <Handle id="end" type="target" :position="Position.Left" :class="[`${end_type}-handle-color`, {'node-errhandle': endHasErr.value}]"/>
            </div>
            <div class="input-step port">
                <div class="input-port-description">
                    步长(默认为1)
                </div>
                <Handle id="step" type="target" :position="Position.Left" :class="[`${step_type}-handle-color`, {'node-errhandle': stepHasErr.value}]"/>
            </div>
            <div class="col_name">
                <div class="param-description" :class="{'node-has-paramerr': col_nameHasErr.value}">
                    列名
                </div>
                <NodepyStringInput 
                v-model="col_name"
                placeholder="列名"
                @update-value="onUpdateValue"
                class="nodrag"
                />
            </div>
            <div class="col_type">
                <div class="param-description" :class="{'node-has-paramerr': col_typeHasErr.value}">
                    列的数据类型
                </div>
                <NodepySelectFew
                    :options="col_typeChinese"
                    :default-selected="defaultSelected"
                    @select-change="onSelectChange"
                    class="nodrag"
                />
            </div>
            <div class="output-table port">
                <div class="output-port-description">
                    输出的表格
                </div>
                <Handle id="table" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': tableHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import NodeTitle from '../tools/NodeTitle.vue'
    import type { Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Handle, Position } from '@vue-flow/core'
    import { computed, ref, watch } from 'vue'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import Timer from '../tools/Timer.vue'
    import { getInputType } from '../getInputType'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import NodepySelectFew from '../tools/Nodepy-selectFew.vue'
    import type { RangeNodeData } from '@/types/nodeTypes'
    import { dataTypeColor } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<RangeNodeData>>()
    const col_type = ['int', 'float', 'Datetime']
    const col_typeChinese = ['整数', '浮点数', '时间']
    const defaultSelected = [col_type.indexOf(props.data.param.col_type)]
    const col_name = ref(props.data.param.col_name)
    const start_type = computed(() => getInputType(props.id, 'start'))
    const end_type = computed(() => getInputType(props.id, 'end'))
    const step_type = computed(() => getInputType(props.id, 'step'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['table']?.type || 'default')
    const tableHasErr = computed(() => handleOutputError(props.id, 'table'))
    const col_nameHasErr = ref({
        id: 'col_name',
        value: false
    })
    const col_typeHasErr = ref({
        id: 'col_type',
        value: false
    })
    const startHasErr = ref({
        handleId: 'start',
        value: false
    })
    const endHasErr = ref({
        handleId: 'end',
        value: false
    })
    const stepHasErr = ref({
        handleId: 'step',
        value: false
    })
    const errMsg = ref<string[]>([])
    const min_max_all_handle_color = computed(() => {
        switch(props.data.param.col_type) {
            case 'int':
                return dataTypeColor.int
            case 'float':
                return dataTypeColor.float
            case 'Datetime':
                return dataTypeColor.Datetime
            default:
                return `conic-gradient(${dataTypeColor.int} 0 120deg, ${dataTypeColor.float} 0 240deg, ${dataTypeColor.Datetime} 0 360deg)`
        }
    })


    const onSelectChange = (e: any) => {
        props.data.param.col_type = col_type[e[0]] as 'int'|'float'
    }

    const onUpdateValue = (e: any) => {
        props.data.param.col_name = col_name.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, col_nameHasErr, col_typeHasErr)
        handleValidationError(props.id, props.data.error, errMsg, startHasErr, endHasErr, stepHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .RangeNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-start, .input-end, .input-step {
                margin-bottom: $node-margin;
            }
            .col_name, .col_type {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: v-bind(min_max_all_handle_color);
    }
</style>