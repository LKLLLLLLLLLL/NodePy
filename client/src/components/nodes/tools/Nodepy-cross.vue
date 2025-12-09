<template>
    <span class="NodepyCrossLayout" @click.stop="handleClick" :style="{width, height}">
        <SvgIcon type="mdi" :path="close_path" :size="size" />
    </span>
</template>

<script lang="ts" setup>
    //@ts-ignore
    import SvgIcon from '@jamescoyle/vue-icon'
    import { mdiClose } from '@mdi/js'
    const close_path = mdiClose
    const props = withDefaults(defineProps<{
        handleClick: (...args: any[]) => void
        width?: string
        height?: string
        size?: string
    }>(), {
        width: 'auto',
        height: 'auto',
        size: "12"
    })
</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    @use './tools.scss' as *;
</style>