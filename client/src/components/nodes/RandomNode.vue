<template>
    <div class="RandomNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="input">随机表格生成节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-row_count port">
                <div class="input-port-description">
                    行数
                </div>
                <Handle id="row_count" type="target" :position="Position.Left" :class="[`${row_count_type}-handle-color`, {'node-errhandle': row_countHasErr.value}]"/>
            </div>
            <div class="input-min_value port" v-if="selected_col_type !== 'str' && selected_col_type !== 'bool'">
                <div class="input-port-description">
                    最小值
                </div>
                <Handle id="min_value" type="target" :position="Position.Left" :class="[`${min_value_type}-handle-color`, {'node-errhandle': min_valueHasErr.value}]"/>
            </div>
            <div class="input-max_value port" v-if="selected_col_type !== 'str' && selected_col_type !== 'bool'">
                <div class="input-port-description">
                    最大值
                </div>
                <Handle id="max_value" type="target" :position="Position.Left" :class="[`${max_value_type}-handle-color`, {'node-errhandle': max_valueHasErr.value}]"/>
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
                <NodepySelectMany
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
    import NodeTitle from './tools/NodeTitle.vue'
    import type { Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Handle, Position, useVueFlow } from '@vue-flow/core'
    import { computed, ref, watch } from 'vue'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from './handleError'
    import ErrorMsg from './tools/ErrorMsg.vue'
    import Timer from './tools/Timer.vue'
    import NodepyStringInput from './tools/Nodepy-StringInput.vue'
    import NodepySelectMany from './tools/Nodepy-selectMany.vue'
    import { getInputType } from './getInputType'
    import type { RandomNodeData } from '@/types/nodeTypes'


    const {removeEdges} = useVueFlow('main')
    const props = defineProps<NodeProps<RandomNodeData>>()
    const col_type = ['int', 'float', 'str', 'bool']
    const col_typeChinese = ['整数', '浮点数', '字符串', '布尔值']
    const defaultSelected = col_type.indexOf(props.data.param.col_type)
    const selected_col_type = computed(() => props.data.param.col_type)
    const col_name = ref(props.data.param.col_name)
    const row_count_type = computed(() => getInputType(props.id, 'row_count'))
    const min_value_type = computed(() => getInputType(props.id, 'min_value'))
    const max_value_type = computed(() => getInputType(props.id, 'max_value'))
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
    const row_countHasErr = ref({
        handleId: 'row_count',
        value: false
    })
    const min_valueHasErr = ref({
        handleId: 'min_value',
        value: false
    })
    const max_valueHasErr = ref({
        handleId: 'max_value',
        value: false
    })
    const errMsg = ref<string[]>([])


    const onSelectChange = (e: any) => {
        const oldType = props.data.param.col_type
        const newType = col_type[e]   
        if((oldType === 'int' || oldType === 'float') && (newType === 'str' || newType === 'bool')) {
            removeEdges(edges => edges.filter(e => e.target === props.id && (e.targetHandle === 'min_value' || e.targetHandle === 'max_value')))
        }   //  if from 'int'|'float' to 'str'|'bool'，remove min_value and max_value connections(if exists)
        props.data.param.col_type = newType as 'int'|'float'|'str'|'bool'
    }

    const onUpdateValue = (e: any) => {
        props.data.param.col_name = col_name.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, col_nameHasErr, col_typeHasErr)
        handleValidationError(props.id, props.data.error, errMsg, row_countHasErr, min_valueHasErr, max_valueHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .RandomNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-row_count, .input-min_value, .input-max_value {
                margin-bottom: $node-margin;
            }
            .col_name, .col_type {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color[data-handleid="row_count"] {
        background: $int-color;
    }
    .all-handle-color[data-handleid="min_value"] {
        background: linear-gradient(to bottom, $int-color 0 50%, $float-color 50% 100%);
    }
    .all-handle-color[data-handleid="max_value"] {
        background: linear-gradient(to bottom, $int-color 0 50%, $float-color 50% 100%);
    }
</style>