<template>
    <div class="SentimentAnalysisNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='stringProcess'>情感分析</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-text port">
                <div class="input-port-description">
                    字符串
                </div>
                <Handle
                    id="text"
                    type="target"
                    :position="Position.Left"
                    :class="[`${text_type}-handle-color`, {'node-errhandle': textHasErr.value}]"
                />
            </div>
            <div class="output-score port">
                <div class="output-port-description">
                    评分
                </div>
                <Handle
                    id="score"
                    type="source"
                    :position="Position.Right"
                    :class="[`${schema_type}-handle-color`, {'node-errhandle': scoreHasErr}]"
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
    const text_type = computed(() => getInputType(props.id, 'text'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['score']?.type || 'default')
    const scoreHasErr = computed(() => handleOutputError(props.id, 'score'))
    const errMsg = ref<string[]>([])
    const textHasErr = ref({
        handleId: 'text',
        value: false
    })


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleValidationError(props.id, props.data.error, errMsg, textHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .SentimentAnalysisNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-text {
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $str-color;
    }
</style>