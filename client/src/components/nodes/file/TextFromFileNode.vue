<template>
    <div class="TextFromFileNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="file">文件文本节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-file port">
                <div class="input-port-description">
                    文件输入
                </div>
                <Handle
                    id="file"
                    type="target"
                    :position="Position.Left"
                    :class="[`${file_type}-handle-color`, {'node-errhandle': fileHaserr.value}]"
                />
            </div>
            <div class="output-text port">
                <div class="output-port-description">
                    文本输出
                </div>
                <Handle
                    id="text"
                    type="source"
                    :position="Position.Right"
                    :class="[`${schema_type}-handle-color`, {'node-errhandle': textHasErr}]"
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
    import type { BaseData } from '../../../types/nodeTypes'
    import { getInputType } from '../getInputType'
    import { handleExecError, handleValidationError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'


    const props = defineProps<NodeProps<BaseData>>()
    const file_type = computed(() => getInputType(props.id, 'file'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['text']?.type || 'default')
    const textHasErr = computed(() => handleOutputError(props.id, 'text'))
    const errMsg = ref<string[]>([])
    const fileHaserr = ref({
        handleId: 'file',
        value: false
    })


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleValidationError(props.id, props.data.error, errMsg, fileHaserr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .TextFromFileNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-file {
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $file-color;
    }
</style>
