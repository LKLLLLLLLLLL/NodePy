<template>
    <div class="TokenizeNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category='stringProcess'>分词节点</NodeTitle>
        <Timer :node-id="id" :default-time="data.runningtime"/>
        <div class="data">
            <div class="input-text port">
                <div class="input-port-description">
                    字符串输入
                </div>
                <Handle id="text" type="target" :position="Position.Left" :class="[`${text_type}-handle-color`, {'node-errhandle': textHasErr.value}]"/>
            </div>
            <div class="language">
                <div class="param-description" :class="{'node-has-paramerr': languageHasErr.value}">
                    语言
                </div>
                <NodepySelectFew
                    :options="languageChinese"
                    :default-selected="defaultSelected"
                    @select-change="onSelectChange"
                    class="nodrag"
                />
            </div>
            <div class="delimiter">
                <div class="param-description" :class="{'node-has-paramerr': delimiterHasErr.value}">
                    分隔符
                </div>
                <NodepyStringInput :allow-null="true" v-model="delimiter" @update-value="onUpdateDelimiter" class="nodrag" placeholder="分隔符"/>
            </div>
            <div class="result_col">
                <div class="param-description" :class="{'node-has-paramerr': result_colHasErr.value}">
                    结果列名
                </div>
                <NodepyStringInput :allow-null="true" v-model="result_col" @update-value="onUpdateResult_col" class="nodrag" placeholder="结果列名"/>
            </div>
            <div class="output-tokens port">
                <div class="output-port-description">
                    分词输出
                </div>
                <Handle id="tokens" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': tokensHasErr}]"/>
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
    import type { TokenizeNodeData } from '@/types/nodeTypes'


    const props = defineProps<NodeProps<TokenizeNodeData>>()
    const language = ['ENGLISH', 'CHINESE']
    const languageChinese = ['英文', '中文']
    const defaultSelected = [language.indexOf(props.data.param.language)]
    const delimiter = ref(props.data.param.delimiter)
    const result_col = ref(props.data.param.result_col)
    const text_type = computed(() => getInputType(props.id, 'text'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['tokens']?.type || 'default')
    const tokensHasErr = computed(() => handleOutputError(props.id, 'tokens'))
    const errMsg = ref<string[]>([])
    const languageHasErr = ref({
        id: 'language',
        value: false
    })
    const delimiterHasErr = ref({
        id: 'delimiter',
        value: false
    })
    const result_colHasErr = ref({
        id: 'result_col',
        value: false
    })
    const textHasErr = ref({
        handleId: 'text',
        value: false
    })


    const onSelectChange = (e: any) => {
        props.data.param.language = language[e[0]] as 'ENGLISH' | 'CHINESE'
    }
    const onUpdateDelimiter = () => {
        props.data.param.delimiter = delimiter.value
    }
    const onUpdateResult_col = () => {
        props.data.param.result_col = result_col.value
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, languageHasErr, delimiterHasErr, result_colHasErr)
        handleValidationError(props.id, props.data.error, errMsg, textHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .TokenizeNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: $node-padding-bottom;
            .input-text {
                margin-bottom: $node-margin;
            }
            .language, .delimiter, .result_col {
                padding: 0 $node-padding-hor;
                margin-bottom: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $str-color;
    }
</style>