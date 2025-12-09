<template>
    <div class="NodepyButtonLayout" :style="{width, height}" @click.stop="handleClick">
        <slot/>
    </div>
</template>

<script lang="ts" setup>
    const props = withDefaults(defineProps<{
        handleClick: (...args: any[]) => void
        width?: string
        height?: string
    }>(), {
        width: 'auto',
        height: '25px',
    })
</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    @use './tools.scss' as *;
    .NodepyButtonLayout {
        @include tool-item-style;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2px 8px;
        cursor: pointer;
        transition: all 0.2s;
        font-size: $node-description-fontsize - 2px;
        font-weight: bold;
        &:hover {
            background-color: #ddd;
        }
        svg {
            margin-right: 100px;
        }
    }
</style>
