<template>
    <div class="UploadNodeLayout nodes-style" :class="[{'nodes-selected': selected}, {'nodes-dbclicked': data.dbclicked}]">
        <div class="node-title-file nodes-topchild-border-radius">{{`文件上传节点${props.id.split('_')[1]}`}}</div>
        <div class="data">
            <div class="file">
                <div class="param-description" :class="{'node-has-paramerr': fileHasErr.value}">上传文件</div>
                <svg-icon type="mdi" :path="mdiAddFile" @click="addFile" class="file-icon"></svg-icon>
            </div>
            <div class="output-file port">
                <div class="output-port-description">文件输出端口</div>
                <Handle id="file" type="source" :position="Position.Right" :class="[`${schema_type}-handle-color`, {'node-errhandle': fileOutputHasErr}]"/>
            </div>
        </div>
        <div class="node-err nodrag" @click.stop>
            <div v-for="err in errMsg">
                {{ err }}
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    //@ts-ignore
    import SvgIcon from '@jamescoyle/vue-icon';
    import { mdiFilePlus } from '@mdi/js';
    import {ref, computed, watch } from 'vue'
    import type { NodeProps } from '@vue-flow/core'
    import { Position, Handle } from '@vue-flow/core'
    import type { Type } from '@/utils/api'
    import { handleParamError, handleExecError, handleOutputError } from './handleError'
    import type { UploadNodeData } from '@/types/nodeTypes'
    import { useGraphStore } from '@/stores/graphStore'
    import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory'


    const mdiAddFile: string = mdiFilePlus
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
    .UploadNodeLayout {
        height: 100%;
        .data {
            padding-top: $node-padding;
            padding-bottom: 5px;
            .file {
                padding: 0 $node-padding;
                .file-icon {
                    margin-left: 50%;
                    transform: translateX(-50%);
                }
            }
            .output-file {
                margin-top: $node-margin;
            }
        }
    }
</style>