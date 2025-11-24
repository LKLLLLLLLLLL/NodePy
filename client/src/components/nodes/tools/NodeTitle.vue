<template>
    <div :class="`node-title-${nodeCategory}`">
        <svg-icon type="mdi" :path="import_path" v-if="nodeCategory == 'input'"></svg-icon>
        <svg-icon type="mdi" :path="math_compass_path" v-if="nodeCategory == 'compute'"></svg-icon>
        <svg-icon type="mdi" :path="file_outline_path" v-if="nodeCategory == 'file'"></svg-icon>
        <svg-icon type="mdi" :path="chart_scatter_plot_path" v-if="nodeCategory == 'visualize'"></svg-icon>
        <slot/>
    </div>
</template>

<script lang="ts" setup>
    //@ts-ignore
    import SvgIcon from '@jamescoyle/vue-icon'
    import { mdiFileOutline, mdiImport, mdiChartScatterPlot, mdiMathCompass } from '@mdi/js'


    const props = defineProps<{
        nodeCategory: 
            'input' 
            | 'compute' 
            | 'control' 
            | 'file' 
            | 'stringProcess' 
            | 'tableProcess' 
            | 'util' 
            | 'visualize'
    }>()
    const file_outline_path = mdiFileOutline
    const import_path = mdiImport
    const chart_scatter_plot_path = mdiChartScatterPlot
    const math_compass_path = mdiMathCompass

</script>

<style lang="scss" scoped>
    @use 'tools.scss' as *;
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
</style>