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
        height: 'auto',
    })
</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    @use './tools.scss' as *;
    .NodepyButtonLayout {
            @include tool-item-style;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 2px 8px;
            cursor: pointer;
            color: #666;
            transition: all 0.2s;
        &:hover {
            background-color: #ddd;
            color: $stress-color;
        }
    }
</style>