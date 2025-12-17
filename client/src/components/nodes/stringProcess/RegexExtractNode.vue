<template>
    <div class="RegexExtractNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='stringProcess'>正则表达式提取</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-string port">
                <div class="input-port-description">
                    字符串输入
                </div>
                <Handle id="string" type="target" :position="Position.Left" :class="[`${string_type}-handle-color`, {'node-errhandle': stringHasErr.value}]"/>
            </div>
            <div class="pattern">
                <div class="param-description" :class="{'node-has-paramerr': patternHasErr.value}">
                    正则表达式
                </div>
                <NodepyStringInput v-model="pattern" @update-value="onUpdatePattern" class="nodrag" placeholder="正则表达式模式"/>
            </div>
            <div class="output-matches port">
                <div class="output-port-description">
                    提取结果
                </div>
                <Handle id="matches" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': matchesHasErr}]"/>
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
    import type { server__models__schema__Schema__Type } from '@/utils/api'
    import { handleValidationError, handleExecError, handleParamError, handleOutputError } from '../handleError'
    import ErrorMsg from '../tools/ErrorMsg.vue'
    import NodeTitle from '../tools/NodeTitle.vue'
    import Timer from '../tools/Timer.vue'
    import NodepyStringInput from '../tools/Nodepy-StringInput.vue'
    import type { RegexExtractNodeData} from '@/types/nodeTypes'


    const props = defineProps<NodeProps<RegexExtractNodeData>>()
    const pattern = ref(props.data.param.pattern)
    const string_type = computed(() => getInputType(props.id, 'string'))
    const schema_type = computed(():server__models__schema__Schema__Type|'default' => props.data.schema_out?.['matches']?.type || 'default')
    const matchesHasErr = computed(() => handleOutputError(props.id, 'matches'))
    const errMsg = ref<string[]>([])
    const patternHasErr = ref({
        id: 'pattern',
        value: false
    })
    const stringHasErr = ref({
        handleId: 'string',
        value: false
    })


    const onUpdatePattern = () => {
        props.data.param.pattern = pattern.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, patternHasErr)
        handleValidationError(props.id, props.data.error, errMsg, stringHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .RegexExtractNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-string {
                margin-bottom: $node-margin;
            }
            .pattern {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $str-color;
    }
</style>
