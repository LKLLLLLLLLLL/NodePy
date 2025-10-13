<script lang = "ts" setup>
    import { useModalStore } from '@/stores/modalStore';
    const modalStore = useModalStore();
    function openModal(){
        modalStore.createModal({
            id: 'node-selector-modal',
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
        width: 15%;
        height: 100%;
        background-color: #1b1b1b;
    }
</style>