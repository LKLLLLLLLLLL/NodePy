import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { ModalInstance } from '@/types/modalType';
let baseZIndex = 1000;
const initialPosition = {x: 100, y: 100};
export const useModalStore = defineStore('modal', () => {
    const modals = ref<ModalInstance[]>([]);

    function createModal(modal:ModalInstance){
        if(modals.value.find(m => m.id === modal.id)){
            activateModal(modal.id);
            return;
        }
        const newModal:ModalInstance = {
            id: modal.id,
            title: modal.title,
            content: modal.content,
            isActive: modal.isActive,
            props: modal.props,
            zIndex: baseZIndex++,
            position: modal.position || { ...initialPosition },
            component: modal.component,
            onSubmit: modal.onSubmit
        }
        modals.value.push(newModal);
        activateModal(modal.id);
    }

    function destroyModal(id:string){
        deactivateModal(id);
        modals.value = modals.value.filter(modal => modal.id !== id);
    }

    function activateModal(id:string){
        const modal = modals.value.find(modal => modal.id === id);
        if(modal){
            modal.isActive = true;
        }
    }

    function deactivateModal(id:string){
        const modal = modals.value.find(modal => modal.id === id);
        if(modal){
            modal.isActive = false;
        }
    }

    function updateModalInfo(id:string,info:Partial<ModalInstance>){
        const modal = modals.value.find(modal => modal.id === id);
        if(modal){
            Object.assign(modal,info);
        }
    }

    function bringToFront(id:string){
        const modal = modals.value.find(modal => modal.id === id);
        if(modal){
            modal.zIndex = baseZIndex++;
        }
    }

    function updateModalPosition(id:string,position:{x:number,y:number}){
        const modal = modals.value.find(modal => modal.id === id);
        if(modal){
            modal.position = position;
        }
    }

    return { modals, createModal, destroyModal, activateModal, deactivateModal, updateModalInfo , bringToFront, updateModalPosition };
});