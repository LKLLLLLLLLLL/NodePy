<template>
    <SvgIcon type="mdi" :path="plus_path" :size="size" />
</template>

<script lang="ts" setup>
    //@ts-ignore
    import SvgIcon from '@jamescoyle/vue-icon'
    import { mdiPlus } from '@mdi/js'
    const plus_path = mdiPlus
    const props = withDefaults(defineProps<{
        size?: string
    }>(), {
        size: "16"
    })
</script>