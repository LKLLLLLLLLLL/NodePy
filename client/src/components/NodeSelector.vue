<script lang = "ts" setup>
    import { useModalStore } from '@/stores/modalStore';
    const modalStore = useModalStore();
    function openModal(){
        modalStore.createModal({
            id: Date.now().toString(),
            title: 'NodeSelector',
            content: 'This is NodeSelector modal',
            isActive: true
        });
    }
</script>
<template>
    <div class = "node-selector-container">
        NodeSelector
        <button @click = "openModal">点我开弹窗</button>
    </div>
</template>
<style lang = "scss" scoped>
    .node-selector-container{
        width: 100%;
        height: 100%;
        background-color: #1b1b1b;
        color: white;
    }
</style>