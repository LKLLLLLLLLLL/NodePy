<script lang="ts" setup>
    const props = defineProps<{
        data: any
    }>()
    const items=[
        {
            name: 'lkl',
            score: 114514
        },
        {
            name: 'xzr',
            score: 10086
        },
        {
            name: 'weh',
            score: 12306
        },
        {
            name: 'lkl',
            score: 114514
        },
        {
            name: 'xzr',
            score: 10086
        },
        {
            name: 'weh',
            score: 12306
        },
        {
            name: 'lkl',
            score: 114514
        },
        {
            name: 'xzr',
            score: 10086
        },
        {
            name: 'weh',
            score: 12306
        },
        {
            name: 'weh',
            score: 12306
        },
        {
            name: 'lklllllllllllllllllllllllllllllllllllllllllllllllllllllll',
            score: 114514
        },
        {
            name: 'xzr',
            score: 10086
        },
        {
            name: 'weh',
            score: 12306
        },
        {
            name: 'weh',
            score: 12306
        },
        {
            name: 'lkl',
            score: 114514
        },
        {
            name: 'xzr',
            score: 10086
        },
        {
            name: 'weh',
            score: 12306
        },
        {
            name: 'weh',
            score: 12306
        },
        {
            name: 'lkl',
            score: 114514
        },
        {
            name: 'xzr',
            score: 10086
        },
        {
            name: 'weh',
            score: 12306
        }
    ]
</script>
<template>
    <div class = 'table-view-container'>
        <v-data-table-virtual 
            :items="items" 
            class = 'result-table'
            striped="even"
            :style="{height:'100%'}"
            :fixed-header="true"
        >
        </v-data-table-virtual>
    </div>
</template>
<style scoped lang="scss">
    .table-view-container{
        height: 100%;
        width: 100%;
    }
</style>