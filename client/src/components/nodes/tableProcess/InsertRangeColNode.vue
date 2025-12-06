<template>
    <div class="InsertRangeColNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="tableProcess">范围数据列添加节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="input-start port">
                <div class="input-port-description">
                    起始值
                </div>
                <Handle id="start" type="target" :position="Position.Left" :class="[`${start_type}-handle-color`, {'node-errhandle': startHasErr.value}]"/>
            </div>
            <div class="input-step port">
                <div class="input-port-description">
                    步长
                </div>
                <Handle id="step" type="target" :position="Position.Left" :class="[`${step_type}-handle-color`, {'node-errhandle': stepHasErr.value}]"/>
            </div>
            <div class="col_name">
                <div class="param-description" :class="{'node-has-paramerr': col_nameHasErr.value}">
                    新增的列名
                </div>
                <NodepyStringInput v-model="col_name" @update-value="onUpdateCol_name" class="nodrag" placeholder="新增的列名"/>
            </div>
            <div class="col_type">
                <div class="param-description" :class="{'node-has-paramerr': col_typeHasErr.value}">
                    列的数据类型
                </div>
                <NodepySelectFew
                    :options="col_typeUi"
                    :default-selected="defaultSelectedCol_type"
                    @select-change="onSelectChangeCol_type"
                    class="nodrag"
                />
            </div>
            <div class="output-table port">
                <div class="output-port-description">
                    表格输出
                </div>
                <Handle id="table" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': outputTableHasErr}]"/>
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
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import { dataTypeColor } from '@/types/nodeTypes'
    import type { InsertRangeColNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<InsertRangeColNodeData>>()
    const col_type = ["int", "float", "Datetime"]
    const col_typeUi = ['整数', '浮点数', '时间']
    const defaultSelectedCol_type = [col_type.indexOf(props.data.param.col_type)]
    const col_name = ref(props.data.param.col_name)
    const table_type = computed(() => getInputType(props.id, 'table'))
    const start_type = computed(() => getInputType(props.id, 'start'))
    const step_type = computed(() => getInputType(props.id, 'step'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['table']?.type || 'default')
    const outputTableHasErr = computed(() => handleOutputError(props.id, 'table'))
    const errMsg = ref<string[]>([])
    const col_nameHasErr = ref({
        id: 'col_name',
        value: false
    })
    const col_typeHasErr = ref({
        id: 'col_type',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })
    const startHasErr = ref({
        handleId: 'start',
        value: false
    })
    const stepHasErr = ref({
        handleId: 'step',
        value: false
    })
    const startAndStepHandleColor = computed(() => {
        switch(props.data.param.col_type) {
            case 'int':
                return dataTypeColor.int
            case 'float':
                return dataTypeColor.float
            case 'Datetime':
                return dataTypeColor.Datetime
        }
    })


    const onUpdateCol_name = () => {
        props.data.param.col_name = col_name.value
    }
    const onSelectChangeCol_type = (e: any) => {
        const selected_col_type = col_type[e[0]] as 'int'|'float'|'Datetime'
        props.data.param.col_type = selected_col_type
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, col_nameHasErr, col_typeHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr, startHasErr, stepHasErr)
    }, {immediate: true})
    
</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .InsertRangeColNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table, .input-start, .input-step {
                margin-bottom: $node-margin;
            }
            .col_name, .col_type {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color[data-handleid="table"] {
        background: $table-color;
    }
    .all-handle-color[data-handleid="start"], .all-handle-color[data-handleid="step"] {
        background: v-bind(startAndStepHandleColor);
    }
</style>