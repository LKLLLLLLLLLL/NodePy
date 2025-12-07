<template>
    <div :class="`node-title-${nodeCategory}`">
        <svg-icon type="mdi" :path="import_path" v-if="nodeCategory === 'input'"></svg-icon>
        <svg-icon type="mdi" :path="math_compass_path" v-else-if="nodeCategory === 'compute'"></svg-icon>
        <svg-icon type="mdi" :path="file_outline_path" v-else-if="nodeCategory === 'file'"></svg-icon>
        <svg-icon type="mdi" :path="chart_scatter_plot_path" v-else-if="nodeCategory === 'visualize'"></svg-icon>
        <svg-icon type="mdi" :path="alphabetical_variant_path" v-else-if="nodeCategory === 'stringProcess'"></svg-icon>
        <svg-icon type="mdi" :path="table_path" v-else-if="nodeCategory === 'tableProcess'"></svg-icon>
        <svg-icon type="mdi" :path="timer_outline_path" v-else-if="nodeCategory === 'datetimeProcess'"></svg-icon>
        <svg-icon type="mdi" :path="ruler_square_path" v-else-if="nodeCategory === 'analysis'"></svg-icon>
        <svg-icon type="mdi" :path="school_outline_path" v-else-if="nodeCategory === 'machineLearning'"></svg-icon>
        <slot/>
    </div>
</template>

<script lang="ts" setup>
    //@ts-ignore
    import SvgIcon from '@jamescoyle/vue-icon'
    import { mdiAlphabeticalVariant, mdiChartScatterPlot, mdiFileOutline, mdiImport, mdiMathCompass, mdiRulerSquare, mdiTable, mdiTimerOutline, mdiSchoolOutline } from '@mdi/js'


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
            | 'machineLearning'
    }>()
    const file_outline_path = mdiFileOutline
    const import_path = mdiImport
    const chart_scatter_plot_path = mdiChartScatterPlot
    const math_compass_path = mdiMathCompass
    const alphabetical_variant_path = mdiAlphabeticalVariant
    const table_path = mdiTable
    const timer_outline_path = mdiTimerOutline
    const ruler_square_path = mdiRulerSquare
    const school_outline_path = mdiSchoolOutline

</script>

<style lang="scss" scoped>
    @use 'tools.scss' as *;
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
</style>
