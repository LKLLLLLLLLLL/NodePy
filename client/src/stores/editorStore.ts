import { defineStore } from 'pinia'
import { useModalStore } from './modalStore';
import PyEditor from '@/components/PyEditor/PyEditor.vue';

export const useEditorStore = defineStore('editor', () => {

    const editWidth = 400;
    const editHeight = 600;

    const modalStore = useModalStore()

    function createEditorModal() {
        modalStore.createModal({
            component: PyEditor,
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
    
    return{
        createEditorModal
    }
})