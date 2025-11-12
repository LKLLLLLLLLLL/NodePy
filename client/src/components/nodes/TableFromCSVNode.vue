<template>
    <div class="TableFromCSVNodeLayout nodes-style" :class="{'nodes-selected': selected}">
        <div class="node-title-input nodes-topchild-border-radius">
            CSV表格节点
        </div>
        <div class="data">
            <div class="input-csv_file port">
                <div class="input-port-description">
                    CSV文件输入端口
                </div>
                <Handle
                    id="csv_file"
                    type="target" 
                    :position="Position.Left" 
                    :class="`${csv_file_type}-handle-color`"
                />
            </div>
            <div class="output-table port">
                <div class="output-port-description">
                    表格输出端口
                </div>
                <Handle 
                    id="table" 
                    type="source" 
                    :position="Position.Right" 
                    :class="`${schema_type}-handle-color`"
                />
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import { Position, Handle } from '@vue-flow/core'
    import type { NodeProps } from '@vue-flow/core'
    import { getInputType } from './getInputType'
    import type {BaseData} from '../../types/nodeTypes'
    import type { Type } from '@/utils/api'
    import {computed} from 'vue'


    const props = defineProps<NodeProps<BaseData>>()
    const csv_file_type = computed(() => getInputType(props.id, 'csv_file'))
    const schema_type = computed(():Type|'default' => props.data.schema_out?.['table']?.type || 'default')


</script>

<style lang="scss" scoped>
    @use '../../common/global.scss' as *;
    @use '../../common/node.scss' as *;
    .TableFromCSVNodeLayout {
        height: 100%;
        width: $node-width;
        background: white;
        .data {
            padding-top: $node-padding;
            padding-bottom: 5px;
            .output-table {
                margin-top: $node-margin;
            }
        }
    }
    .all-handle-color {
        background: $file-color;
    }
</style>