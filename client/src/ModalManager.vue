<script setup lang = "ts">
    import type { ModalInstance }  from './types/modalType';
    import { useModalStore } from './stores/modalStore';
    import { Teleport } from 'vue';
    import Modal from './components/Modal.vue';
    const modalStore = useModalStore();
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
</style>