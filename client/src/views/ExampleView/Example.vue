<script lang="ts" setup>
    import { useRouter } from 'vue-router'
    import { ref } from 'vue';
    import ExampleDemoFrame from './ExampleDemoFrame.vue';

    const default_name: string = 'default_name'

</script>
<template>
    <div class="example-container">
        <div class="example-info-container">
            <h2>Suppose there exists an example and you can open it by clicking the button below</h2>
        </div>
        <ExampleDemoFrame :name="default_name"></ExampleDemoFrame>
    </div>
</template>
<style lang="scss" scoped>
    .example-container{
        display: flex;
        flex: 1;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    .example-info-container{
        text-align: center;
        height: 50px;
        width: 100%;
    }
</style>