import { defineStore } from 'pinia';
import { ref,markRaw } from 'vue';
import type { ModalInstance } from '@/types/modalType';

let baseZIndex = 1000;

export const useModalStore = defineStore('modal', () => {
    const modals = ref<ModalInstance[]>([]);

    function findModal(id: string){
        return modals.value.find(m => m.id === id);
    }
    
    function createModal(modal:ModalInstance){
        if(findModal(modal.id)){
            activateModal(modal.id);
            return;
        }
        const newModal:ModalInstance = {
            id: modal.id,
            title: modal.title,
            content: modal.content,
            isActive: modal.isActive,
            isResizable: modal.isResizable,
            isDraggable: modal.isDraggable,
            props: modal.props,
            zIndex: baseZIndex++,
            position: modal.position || { x: 100, y: 100 },
            size: modal.size || { width: 200, height: 200 },
            minSize: modal.minSize || { width: 100, height: 100 },
            maxSize: modal.maxSize,
            component: modal.component?markRaw(modal.component):undefined,
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
        const modal = findModal(id);
        if(modal){
            modal.isActive = true;
        }
    }

    function deactivateModal(id:string){
        const modal = findModal(id);
        if(modal){
            modal.isActive = false;
        }
    }

    function updateModalInfo(id:string,info:Partial<ModalInstance>){
        const modal = findModal(id);
        if(modal){
            Object.assign(modal,info);
        }
    }

    function bringToFront(id:string){
        const modal = findModal(id);
        if(modal){
            modal.zIndex = baseZIndex++;
        }
    }

    function updateModalPosition(id:string,position:{x:number,y:number}){
        const modal = findModal(id);
        if(modal){
            modal.position = position;
        }
    }

    function updateModalSize(id:string,size:{width:number,height:number}){
        const modal = findModal(id);
        if(modal){
            modal.size = size;
        }
    }

    return { modals, findModal, createModal, destroyModal, activateModal, deactivateModal, updateModalInfo , bringToFront, updateModalPosition, updateModalSize };
});