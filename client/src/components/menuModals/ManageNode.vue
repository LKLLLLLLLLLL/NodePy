<script lang="ts" setup>
    // import { useGraphStore } from '@/stores/graphStore';
    // import { ref } from 'vue';

    // const graphStore = useGraphStore();
    // const {getNodes,findNode} = graphStore.vueFlowInstance

    // const isSearching = ref<boolean>(false);
    // const isLoading = ref<boolean>(false);

    // function handleSearch(){
    //     isSearching.value = true;
    // }

    // function handleSearchSubmit(){
    //     isLoading.value = true;
    //     setTimeout(() => {
    //         isSearching.value = false;
    //         isLoading.value = false;
    //     }, 3000);
    // }

    // function handleSearchCancel(){
    //     isSearching.value = false;
    //     isLoading.value = false;
    // }

</script>
<template>
    <div>
        <!-- <div class="search-nodes">
            <el-input @click="handleSearch">搜索框以删除</el-input>
            <el-button @click="handleSearchSubmit" type='primary'>搜索</el-button>
            <el-button @click="handleSearchCancel" type='primary'>返回</el-button>
        </div>
        <div class="show-nodes"
            v-if="!isLoading&&!isSearching"
            v-for="node in getNodes"
            :key="node.id"
        >
            {{node.id}}--{{ node.data }}
        </div>
        <div v-if="isLoading">正在加载搜索结果...</div> -->
    </div>
</template>
<style lang="scss" scoped>
</style>
