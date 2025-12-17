<template>
    <div class="TableToFileNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="file">表格转文件</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-table port">
                <div class="input-port-description">
                    表格输入
                </div>
                <Handle
                    id="table"
                    type="target"
                    :position="Position.Left"
                    :class="[`${table_type}-handle-color`, {'node-errhandle': tableHasErr.value}]"
                />
            </div>
            <div class="filename">
                <div class="param-description" :class="{'node-has-paramerr': filenameHasErr.value}">
                    文件名
                </div>
                <NodepyStringInput
                    v-model="filename"
                    @update-value="onUpdateFilename"
                    class="nodrag"
                    placeholder="文件名"
                />
            </div>
            <div class="format">
                <div class="param-description" :class="{'node-has-paramerr': formatHasErr.value}">
                    文件类型
                </div>
                <NodepySelectFew
                    :options="format"
                    :default-selected="defaultSelected"
                    @select-change="onSelectChange"
                    class="nodrag"
                />
            </div>
            <div class="output-file port">
                <div class="output-port-description">
                    文件输出
                </div>
                <Handle
                    id="file"
                    type="source"
                    :position="Position.Right"
                    :class="[`${schema_type}-handle-color`, {'node-errhandle': fileHasErr}]"
                />
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import type { NodeProps } from '@vue-flow/core'
    import { Handle, Position } from '@vue-flow/core'
    import { computed, ref, watch } from 'vue'
    import { getInputType } from '../getInputType'
    import { handleExecError, handleValidationError, handleOutputError, handleParamError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepySelectFew from '../tools/Nodepy-selectFew.vue'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import type { TableToFileNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<TableToFileNodeData>>()
    const filename = ref(props.data.param.filename || '')
    const format = ["csv", "xlsx", "json"]
    const defaultSelected = [format.indexOf(props.data.param.format)]
    const table_type = computed(() => getInputType(props.id, 'table'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['file']?.type || 'default')
    const fileHasErr = computed(() => handleOutputError(props.id, 'file'))
    const errMsg = ref<string[]>([])
    const filenameHasErr = ref({
        id: 'filename',
        value: false
    })
    const formatHasErr = ref({
        id: 'format',
        value: false
    })
    const tableHasErr = ref({
        handleId: 'table',
        value: false
    })


    const onUpdateFilename = (e?: Event) => {
        props.data.param.filename = filename.value
    }
    const onSelectChange = (e: any) => {
        props.data.param.format = format[e[0]] as 'csv'|'xlsx'|'json'
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, filenameHasErr, formatHasErr)
        handleValidationError(props.id, props.data.error, errMsg, tableHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .TableToFileNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-table {
                margin-bottom: $node-margin;
            }
            .filename, .format {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $table-color;
    }
</style>
