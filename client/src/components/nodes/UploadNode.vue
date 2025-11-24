<template>
    <div class="UploadNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <NodeTitle node-category="file">文件上传节点</NodeTitle>
        <div class="data">
            <div class="file">
                <div class="param-description" :class="{'node-has-paramerr': fileHasErr.value}">上传文件</div>
                <div class="file-upload-component nodrag" @click.stop="addFile">
                    <div class="file-name" :class="{'has-no-file': !data.param.file}">
                        {{data.param.file ? data.param.file.filename : '点击上传文件'}}
                    </div>
                    <svg-icon type="mdi" :path="mdiAddFile" @click="addFile" class="file-icon"></svg-icon>
                </div>
            </div>
            <div class="output-file port">
                <div class="output-port-description">文件输出端口</div>
                <Handle id="file" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': fileOutputHasErr}]"/>
            </div>
        </div>
        <ErrorMsg :err-msg="errMsg"/>
    </div>
</template>

<script lang="ts" setup>
    //@ts-ignore
    import SvgIcon from '@jamescoyle/vue-icon';
    import { mdiPlus } from '@mdi/js';
    import {ref, computed, watch } from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import type { Type } from '@/utils/api'
    import { handleParamError, handleExecError, handleOutputError } from './handleError'
    import type { UploadNodeData } from '@/types/nodeTypes'
    import { useGraphStore } from '@/stores/graphStore'
    import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory'
    import ErrorMsg from './tools/ErrorMsg.vue'
    import NodeTitle from './tools/NodeTitle.vue'


    const mdiAddFile: string = mdiPlus
    const props = defineProps<NodeProps<UploadNodeData>>()
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['file']?.type || 'default')
    const fileOutputHasErr = computed(() => handleOutputError(props.id, 'file'))
    const errMsg = ref<string[]>([])
    const fileHasErr = ref({
        id: 'file',
        value: false
    })
    const graphStore = useGraphStore()
    const authService = AuthenticatedServiceFactory.getService()


    const addFile = async() => {
        const projectId = graphStore.project.project_id
        const input = document.createElement('input')
        input.type = 'file'
        input.accept = '*'
        input.onchange = async (e) => {
            const file = (e.target as HTMLInputElement).files?.[0]
            console.log(file instanceof Blob)
            if(!file) return

            try {
                const f = await authService.uploadFileApiFilesUploadProjectIdPost(projectId, props.id, {file})
                console.log('文件上传成功:', f)
                props.data.param.file = f
            }catch(err) {
                console.error('文件上传失败:', err)
            }
        }
        input.click()
    }


    watch(() => JSON.stringify(props.data.error), () => {
        errMsg.value = []
        handleExecError(props.data.error, errMsg)
        handleParamError(props.data.error, errMsg, fileHasErr)
    }, {immediate: true})

</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    @use './tools/tools.scss' as *;
    .UploadNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding-top;
            padding-bottom: 5px;
            .file {
                padding: 0 $node-padding-hor;
                .file-upload-component {
                    @include box-tools-style;
                    position: relative;
                    margin-top: 5px;
                    display: flex;
                    align-items: center;
                    cursor: pointer;
                    .file-name {
                        @include tool-item-style;
                        text-align: center;
                        width: 100%;
                    }
                    .has-no-file {
                        color: rgba(0,0,0,0.2);
                    }
                    .file-icon {
                        position:absolute;
                        right: 5px;
                        width:18px;
                        color: rgba(0,0,0,0.4);
                    }
                }
            }
            .output-file {
                margin-top: $node-margin;
            }
        }
    }
</style>
