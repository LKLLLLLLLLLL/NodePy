<script lang="ts" setup>
import { DateAdapterSymbol } from 'vuetify/lib/composables/date/date.mjs';

    const props = defineProps<{
        data: any
    }>()
</script>
<template>
    <div class = 'value-view-container'>
        ValueView
        {{ data }}
    </div>
</template>
<style scoped lang="scss">
</style>