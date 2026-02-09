<template>
    <div class="NodeContainerLayout"></div>
</template>

<script lang="ts" setup>
    import type { BaseData } from '@/types/nodeTypes'
    import type { NodeProps } from '@vue-flow/core'
    import { useVueFlow } from '@vue-flow/core'
    import {  onMounted, onUnmounted } from 'vue'


    const props = defineProps<NodeProps<BaseData>>()
    let intervalId: any
    const {getNodes, updateNode} = useVueFlow()


    // 计算并更新容器节点的位置
    const updateContainerPosition = () => {
        const containerId = props.id

        // 找到所有groupId等于当前容器id的节点
        const childNodes = getNodes.value.filter(node =>
            node.data.groupId === containerId
        )

        if (childNodes.length === 0) {
            // 如果没有子节点，使用默认位置
            return
        }

        // 计算能包裹所有子节点的最小矩形
        let minX = Infinity
        let minY = Infinity
        let maxX = -Infinity
        let maxY = -Infinity

        childNodes.forEach(node => {
            const nodeX = node.position.x
            const nodeY = node.position.y
            const nodeWidth = node.dimensions.width
            const nodeHeight = node.dimensions.height

            minX = Math.min(minX, nodeX)
            minY = Math.min(minY, nodeY)
            maxX = Math.max(maxX, nodeX + nodeWidth)
            maxY = Math.max(maxY, nodeY + nodeHeight)
        })

        // 添加一些内边距
        const padding_top = 35
        const padding_bottom = 20
        const padding_horizontal = 15
        const containerWidth = maxX - minX + padding_horizontal * 2
        const containerHeight = maxY - minY + padding_top + padding_bottom

        // 更新容器节点的位置和大小
        updateNode(containerId, {
            position: {
                x: minX - padding_horizontal,
                y: minY - padding_top,
            },
            width: containerWidth,
            height: containerHeight,
        })
    }


    onMounted(() => {
        intervalId = setInterval(() => {
            updateContainerPosition()
        }, 1)
    })
    onUnmounted(() => {
        clearInterval(intervalId)
    })

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .NodeContainerLayout {
        width: 100%;
        height: 100%;
        background: $node-container-color;
        border-radius: 30px;
        // box-shadow: 5px 2px 15px rgba(128, 128, 128, 0.1);
    }
</style>

<style lang="scss">
    .vue-flow__node-NodeContainer {
        pointer-events: none !important;
        z-index: -2 !important;
    }
</style>
