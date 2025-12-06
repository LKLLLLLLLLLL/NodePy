<template>
    <div class="FillNaNValueNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="tableProcess">表格缺失值填充节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="subset_cols">
                <div class="param-description" :class="{'node-has-paramerr': subset_colsHasErr.value}">
                    检查的列名
                </div>
                <NodepyMultiSelectMany
                    :options="subset_colsHint"
                    :default-selected="defaultSelectedSubset_cols"
                    :clear-toggle="clearToggle"
                    @select-change="onSelectChangeSubset_cols"
                    @clear-select="clearSelectSubset_cols"
                    class="nodrag"
                />
            </div>
            <div class="method">
                <div class="param-description" :class="{'node-has-paramerr': methodHasErr.value}">
                    填充方法
                </div>
                <NodepySelectFew
                    :options="methodUi"
                    :default-selected="defaultSelectedMethod"
                    @select-change="onSelectChangeMethod"
                    class="nodrag"
                />
            </div>
            <div class="fill_value" v-if="data.hint?.subset_col_choices && data.param.method === 'const'" v-for="(value, idx) in fill_value" :key="`${data.param.subset_cols[idx]}_${idx}`"><!-- when the hint is empty, don't show the fill_value to avoid complex errors-->
                <div class="param-description fill_value-description">
                    列
                    <span :class="{'special-table-column': isSpecialColumn(data.param.subset_cols[idx])}">
                        {{displayColumnName(data.param.subset_cols[idx])}}
                    </span>
                </div>
                <div class="param-description" :class="{'node-has-paramerr': fill_valueHasErr.value}">
                    填充值
                    <NodepyBoolValue
                        v-model="value.value"
                        @update-value="onUpdateValue(idx)"
                        width="20px"
                        height="20px"
                        v-if="fill_value_types[subset_colsHint.indexOf(data.param.subset_cols[idx])] === 'bool'"
                    >
                        布尔
                    </NodepyBoolValue>
                </div>
                <NodepyNumberInput
                    v-if="fill_value_types[subset_colsHint.indexOf(data.param.subset_cols[idx])] === 'int'"
                    v-model="value.value"
                    class="nodrag"
                    @update-value="onUpdateValue(idx)"
                 />
                <NodepyNumberInput
                    v-if="fill_value_types[subset_colsHint.indexOf(data.param.subset_cols[idx])] === 'float'"
                    v-model="value.value"
                    class="nodrag"
                    @update-value="onUpdateValue(idx)"
                    :denominator="1000"
                />
                <NodepyStringInput
                    v-model="value.value"
                    @update-value="onUpdateValue(idx)"
                    class="nodrag"
                    placeholder="常量字符串"
                    v-if="fill_value_types[subset_colsHint.indexOf(data.param.subset_cols[idx])] === 'str'"
                />
                <NodepyStringInput
                    v-model="value.value"
                    @update-value="onUpdateValue(idx)"
                    class="nodrag"
                    placeholder="时间"
                    v-if="fill_value_types[subset_colsHint.indexOf(data.param.subset_cols[idx])] === 'Datetime'"
                />
            </div>
            <div class="output-filled_table port">
                <div class="output-port-description">
                    表格输出
                </div>
                <Handle id="filled_table" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': filled_tableHasErr}]"/>
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
    import NodepyMultiSelectMany from '../tools/Nodepy-multiSelectMany.vue'
    import NodepySelectFew from '../tools/Nodepy-selectFew.vue'
    import NodepyBoolValue from '../tools/Nodepy-boolValue.vue'
    import NodepyNumberInput from '../tools/Nodepy-NumberInput/Nodepy-NumberInput.vue'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import { displayColumnName, isSpecialColumn } from '../tableColumnDisplay'
    import type { FillNaNValueNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<FillNaNValueNodeData>>()
    const subset_colsHint = computed(() => {
        if(props.data.hint?.subset_col_choices?.length === 0) return ['']
        return props.data.hint?.subset_col_choices || ['']
    })
    const subset_cols = ref(props.data.param.subset_cols)   //  used for defaultSelectedSubset_cols
    const defaultSelectedSubset_cols = computed(() => {
        const hintArray = subset_colsHint.value
        const selectedArray = subset_cols.value
        return selectedArray.map(item => hintArray.indexOf(item)).filter(idx => idx !== -1)
    })
    const method = ["const", "ffill", "bfill"]
    const methodUi = ['常量', '前向', '后向']
    const defaultSelectedMethod = [method.indexOf(props.data.param.method)]
    const fill_value = ref<({value: number|string|boolean})[]|undefined|null|any>(props.data.param.fill_value?.map(value => ({value})) || [])
    const fill_value_types = computed(() => props.data.hint?.fill_value_types)
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['filled_table']?.type || 'default')
    const filled_tableHasErr = computed(() => handleOutputError(props.id, 'filled_table'))
    const errMsg = ref<string[]>([])
    const subset_colsHasErr = ref({
        id: 'subset_cols',
        value: false
    })
    const methodHasErr = ref({
        id: 'method',
        value: false
    })
    const fill_valueHasErr = ref({
        id: 'fill_value',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })
    const clearToggle = ref(false)


    const onSelectChangeMethod = (e: any) => {
        const oldMethod = JSON.parse(JSON.stringify(props.data.param.method))
        const newMethod = method[e[0]] as 'const'|'ffill'|'bfill'
        props.data.param.method = newMethod
        if (oldMethod !== 'const' && newMethod === 'const') {
            // 从非const切换到const，为当前所有列初始化值
            fill_value.value = props.data.param.subset_cols.map((colName, idx) => {
                const hintIndex = subset_colsHint.value.indexOf(colName)
                if (hintIndex !== -1 && fill_value_types.value && fill_value_types.value[hintIndex]) {
                    switch(fill_value_types.value[hintIndex]) {
                        case 'int':
                            return {value: 0}
                        case 'float':
                            return {value: 0.0}
                        case 'str':
                            return {value: ''}
                        case 'bool':
                            return {value: false}
                        case 'Datetime':
                            return {value: new Date().toISOString()}
                        default:
                            return {value: -1}
                    }
                }
                return {value: -1}
            })
            props.data.param.fill_value = fill_value.value.map((obj: any) => obj.value)
        } else if (oldMethod === 'const' && newMethod !== 'const') {
            // 从const切换到非const，清空fill_value但保留列
            fill_value.value = []
            props.data.param.fill_value = undefined
        }
    }
    const onSelectChangeSubset_cols = (e: any) => {
        const oldColumns = JSON.parse(JSON.stringify(props.data.param.subset_cols || []))
        const newColumns = e.map((idx: number) => subset_colsHint.value[idx])
        props.data.param.subset_cols = newColumns
        if (props.data.param.method !== 'const') {
            return
        }
        const oldFillValues = JSON.parse(JSON.stringify(props.data.param.fill_value || []))
        // 创建新的fill_value数组，保持与newColumns相同的顺序
        const newFillValues = newColumns.map((colName: any, newIndex: any) => {
            // 在旧列中找到相同列名的索引
            const oldIndex = oldColumns.indexOf(colName)
            
            if (oldIndex !== -1) {
                // 列名存在，保留原来的值
                return oldFillValues[oldIndex]
            } else {
                // 新增的列，根据类型初始化默认值
                const hintIndex = subset_colsHint.value.indexOf(colName)
                if (hintIndex !== -1 && fill_value_types.value && fill_value_types.value[hintIndex]) {
                    switch (fill_value_types.value[hintIndex]) {
                        case 'int':
                            return 0
                        case 'float':
                            return 0.0
                        case 'str':
                            return ''
                        case 'bool':
                            return false
                        case 'Datetime':
                            return new Date().toISOString()
                        default:
                            return -1
                    }
                }
                // 无法确定类型时返回-1
                return -1
            }
        })
        props.data.param.fill_value = newFillValues
        fill_value.value = newFillValues.map((value: any) => ({ value }))
    }
    const clearSelectSubset_cols = (resolve: any) => {
        props.data.param.subset_cols = []
        subset_cols.value = props.data.param.subset_cols
        fill_value.value = []
        props.data.param.fill_value = undefined
        resolve()
    }
    const onUpdateValue = (idx: number) => {
        if(props.data.param.fill_value) {
            props.data.param.fill_value[idx] = fill_value.value[idx].value
        }
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, subset_colsHasErr, methodHasErr, fill_valueHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})
    watch(() => JSON.stringify(props.data.hint?.fill_value_types), (newValue, oldValue) => {
        clearToggle.value = !clearToggle.value
    }, {immediate: false})
    
</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .FillNaNValueNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .subset_cols, .method, .fill_value {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
            .fill_value {
                .fill_value-description {
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    margin-bottom: $node-margin;
                }
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>