<script setup lang = "ts">
    import type { ModalInstance } from '../types/modalType';
    import { useModalStore } from '../stores/modalStore';
    const props = defineProps<{
        modal: ModalInstance
    }>();
    const modalStore = useModalStore();
    const closeModal = () => {
        modalStore.deactivateModal(props.modal.id);
        modalStore.destroyModal(props.modal.id);
    };
    const moveModal = () =>{

    }
</script>
<template>
    <div class = "modal-container" v-if="modal.isActive">
        <div class = "modal-head">
            <div class = "modal-title-id">
                <h3>{{ modal.title }}</h3>
                <p>ID: {{ modal.id }}</p>
            </div>
            <div class = "modal-control">
                <button @click = "closeModal">关闭</button>
            </div>
        </div>
        <div class = "modal-body">
            <component 
                v-if="modal.component" 
                :is="modal.component" 
                v-bind="modal.props"
            />
            <div v-else-if="modal.content">
                {{ modal.content }}
            </div>
        </div>
    </div>
</template>
<style scoped lang = "scss">
    .modal-container{

        display: flex;
        flex-direction: column;
        width: 200px;
        height: 200px;
        background-color: grey;
    }
    .modal-head{
        display: flex;
        height: 50px;
        width: 100%;
        background-color: #585858;
        color: black;
    }
    .modal-body{
        display: flex;
        flex-direction: column;
        color: black;
    }
    .modal-control{
        margin-left: auto;
    }
</style>