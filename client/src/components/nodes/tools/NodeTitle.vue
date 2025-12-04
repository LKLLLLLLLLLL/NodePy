<template>
    <div :class="`node-title-${nodeCategory}`">
        <svg-icon type="mdi" :path="import_path" v-if="nodeCategory == 'input'"></svg-icon>
        <svg-icon type="mdi" :path="math_compass_path" v-if="nodeCategory == 'compute'"></svg-icon>
        <svg-icon type="mdi" :path="file_outline_path" v-if="nodeCategory == 'file'"></svg-icon>
        <svg-icon type="mdi" :path="chart_scatter_plot_path" v-if="nodeCategory == 'visualize'"></svg-icon>
        <svg-icon type="mdi" :path="alphabetical_variant_path" v-if="nodeCategory == 'stringProcess'"></svg-icon>
        <svg-icon type="mdi" :path="table_path" v-if="nodeCategory == 'tableProcess'"></svg-icon>
        <slot/>
    </div>
</template>

<script lang="ts" setup>
    //@ts-ignore
    import SvgIcon from '@jamescoyle/vue-icon'
    import { mdiAlphabeticalVariant, mdiChartScatterPlot, mdiFileOutline, mdiImport, mdiMathCompass, mdiTable } from '@mdi/js'


    const props = defineProps<{
        nodeCategory:
            'input'
            | 'compute'
            | 'control'
            | 'file'
            | 'stringProcess'
            | 'tableProcess'
            | 'analysis'
            | 'visualize'
            | 'datetimeProcess'
    }>()
    const file_outline_path = mdiFileOutline
    const import_path = mdiImport
    const chart_scatter_plot_path = mdiChartScatterPlot
    const math_compass_path = mdiMathCompass
    const alphabetical_variant_path = mdiAlphabeticalVariant
    const table_path = mdiTable

</script>

<style lang="scss" scoped>
    @use 'tools.scss' as *;
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
</style>
