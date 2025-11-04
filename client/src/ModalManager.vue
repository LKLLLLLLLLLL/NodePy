<script setup lang = "ts">
    import type { ModalInstance }  from './types/modalType';
    import { useModalStore } from './stores/modalStore';
    import { Teleport,onMounted } from 'vue';
    import Modal from './components/Modal.vue';
    import { useResultStore } from './stores/resultStore';
    const modalStore = useModalStore();
    const resultStore = useResultStore();

    onMounted(()=>{
        resultStore.createResultModal();
        modalStore.deactivateModal('result');
    })

</script>
<template>
    <Teleport to="body">
        <div class="modal-manager">
            <Modal
                v-for="modal in modalStore.modals"
                :key="modal.id"
                :modal="modal"
            >
            </Modal>
        </div>
    </Teleport>
</template>
<style scoped lang = "scss">
    .modal-manager{
        position: fixed;
        top: 0;
        left: 0;
        width: 0;
        height: 0;
        pointer-events: none;
        z-index: 1000;
    }
    .modal-manager > * {
        pointer-events: auto;
    }
</style>