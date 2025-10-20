<script lang="ts" setup>
    import { useGraphStore } from '@/stores/graphStore';

    const graphStore = useGraphStore();

    const {getNodes,findNode} = graphStore.vueFlowInstance

    const currentNode = findNode('-2')

    console.log(getNodes[0])

    console.log(currentNode.data.label)
</script>
<template>

</template>
<style lang="scss" scoped>
</style>