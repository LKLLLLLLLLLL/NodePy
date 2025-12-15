import { defineStore } from 'pinia'
import { useModalStore } from './modalStore';
import {ref} from 'vue'
import PyEditorModal from '@/components/PyEditor/PyEditorModal.vue';

export const useEditorStore = defineStore('editor', () => {

    const editWidth = 400;
    const editHeight = 600;

    const default_script: string = ''

    const currentScript = ref<string>(default_script)

    const modalStore = useModalStore()

    function createEditorModal() {
        modalStore.createModal({
            component: PyEditorModal,
            title: '编辑代码',
            isActive: true,
            isResizable: true,
            isDraggable: true,
            position: {
            x: window.innerWidth / 2 - editWidth / 2,
            y: window.innerHeight / 2 - editHeight / 2
            },
            size: {
            width: editWidth,
            height: editHeight
            },
            id: 'edit-modal',
        })
    }

    function applyChange(){
        const simpleEvent = new Event('ApplyEditorChanges');
        window.dispatchEvent(simpleEvent);
    }

    function confirmChange(){
        modalStore.deactivateModal('edit-modal')
        modalStore.destroyModal('edit-modal')
        applyChange()
    }

    function cancelChange(){
        modalStore.deactivateModal('edit-modal')
        modalStore.destroyModal('edit-modal')
        currentScript.value = default_script
    }
    
    return{
        currentScript,
        createEditorModal,
        confirmChange,
        cancelChange,
    }
})