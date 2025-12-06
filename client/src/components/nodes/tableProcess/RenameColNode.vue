<template>
    <div class="RenameColNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="tableProcess">表格列重命名节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle id="table" type="target" :position="Position.Left" :class="[`${table_type}-handle-color`, {'node-errhandle': inputTableHasErr.value}]"/>
            </div>
            <div class="rename_cols">
                <div class="param-description" :class="{'node-has-paramerr': rename_mapHasErr.value}">
                    修改的列名
                </div>
                <NodepyMultiSelectMany
                    :options="rename_colsHint"
                    :default-selected="defaultSelectedRename_cols"
                    :clear-toggle="clearToggle"
                    @select-change="onSelectChangeRename_cols"
                    @clear-select="clearSelectRename_cols"
                    class="nodrag"
                />
            </div>
            <div class="rename_value" v-if="data.hint?.rename_col_choices" v-for="(value, idx) in rename_value" :key="`${propsRename_cols[idx]}_${idx}`"><!-- when the hint is empty, don't show the rename_value to avoid complex errors-->
                <div class="param-description rename_value-description">
                    旧列名:
                    <span :class="{'special-table-column': isSpecialColumn(propsRename_cols[idx])}">
                        {{displayColumnName(propsRename_cols[idx])}}
                    </span>
                </div>
                <div class="param-description" :class="{'node-has-paramerr': rename_mapHasErr.value}">
                    新列名:
                </div>
                <NodepyStringInput
                    v-model="value.value"
                    @update-value="onUpdateValue(idx)"
                    class="nodrag"
                    placeholder="常量字符串"
                />
            </div>
            <div class="output-renamed_table port">
                <div class="output-port-description">
                    表格输出
                </div>
                <Handle id="renamed_table" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': renamed_tableHasErr}]"/>
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
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import { displayColumnName, isSpecialColumn } from '../tableColumnDisplay'
    import type { RenameColNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<RenameColNodeData>>()
    const rename_colsHint = computed(() => {
        if(props.data.hint?.rename_col_choices?.length === 0) return ['']
        return props.data.hint?.rename_col_choices || ['']
    })
    const rename_cols = ref(Object.keys(props.data.param.rename_map))   //  used for defaultSelectedRename_cols
    const defaultSelectedRename_cols = computed(() => {
        const hintArray = rename_colsHint.value
        const selectedArray = rename_cols.value
        return selectedArray.map(item => hintArray.indexOf(item)).filter(idx => idx !== -1)
    })
    const rename_value = ref<({value: string})[]>(Object.values(props.data.param.rename_map).map(value => ({value})))
    const propsRename_cols = computed(() => Object.keys(props.data.param.rename_map))
    const propsRename_values = computed(() => Object.values(props.data.param.rename_map))
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['renamed_table']?.type || 'default')
    const renamed_tableHasErr = computed(() => handleOutputError(props.id, 'renamed_table'))
    const errMsg = ref<string[]>([])
    const rename_mapHasErr = ref({
        id: 'rename_map',
        value: false
    })
    const inputTableHasErr = ref({
        handleId: 'table',
        value: false
    })
    const clearToggle = ref(false)


    const onSelectChangeRename_cols = (e: any) => {
        const oldColumns = JSON.parse(JSON.stringify(propsRename_cols.value))
        const newColumns = e.map((idx: number) => rename_colsHint.value[idx])
        const oldFillValues = JSON.parse(JSON.stringify(propsRename_values.value))
        // 创建新的rename_values数组，保持与newColumns相同的顺序
        const newFillValues = newColumns.map((colName: any, newIndex: any) => {
            // 在旧列中找到相同列名的索引
            const oldIndex = oldColumns.indexOf(colName)
            
            if (oldIndex !== -1) {
                // 列名存在，保留原来的值
                return oldFillValues[oldIndex]
            } else {
                return colName
            }
        })
        props.data.param.rename_map = newColumns.reduce((acc: any, key: any, idx: any) => {
            acc[key] = newFillValues[idx]
            return acc
        }, {})
        rename_value.value = newFillValues.map((value: any) => ({ value }))
    }
    const clearSelectRename_cols = (resolve: any) => {
        props.data.param.rename_map = {}
        rename_cols.value = []
        rename_value.value = []
        resolve()
    }
    const onUpdateValue = (idx: number) => {
        props.data.param.rename_map[propsRename_cols.value[idx]!] = rename_value.value[idx]!.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, rename_mapHasErr)
        handleValidationError(props.id, props.data.error, errMsg, inputTableHasErr)
    }, {immediate: true})
    watch(() => JSON.stringify(props.data.hint?.fill_value_types), (newValue, oldValue) => {
        clearToggle.value = !clearToggle.value
    }, {immediate: false})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .RenameColNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .rename_cols, .rename_value {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
            .rename_value {
                .rename_value-description {
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>