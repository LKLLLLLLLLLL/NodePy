<script setup lang = "ts">
    import type { ModalInstance } from '../types/modalType';
    import { useModalStore } from '../stores/modalStore';
    import { ref } from 'vue';
    import {Close} from '@element-plus/icons-vue';

    const props = defineProps<{
        modal: ModalInstance
    }>();

    const modalStore = useModalStore();

    const isDragging = ref(false);
    const dragStartPosition = ref<{x: number, y: number}>({x: 0, y: 0});
    const dragStartModalPosition = ref<{x: number, y: number}>(props.modal.position);

    const isResizing = ref(false);
    const resizeDirection = ref('');
    const resizeStartPosition = ref<{x: number, y: number}>({x: 0, y: 0});//光标起始位置
    const resizeStartSize = ref<{width: number, height: number}>(props.modal.size);//弹窗起始尺寸
    const resizeStartModalPosition = ref<{x: number, y: number}>({x: 0, y: 0});

    const closeModal = () => {
        modalStore.deactivateModal(props.modal.id);
        modalStore.destroyModal(props.modal.id);
    };

    const onDrag = (event: MouseEvent) => {
        if(!props.modal.isDraggable)return;
        if (isDragging.value) {

        const deltaX = event.clientX - dragStartPosition.value.x;
        const deltaY = event.clientY - dragStartPosition.value.y;
    
        const newPosition = {
            x: dragStartModalPosition.value.x + deltaX,
            y: dragStartModalPosition.value.y + deltaY
        };
            modalStore.updateModalPosition(props.modal.id, newPosition);
        }
    }; 

    const stopDrag = () => {
        if(!props.modal.isDraggable)return;
        isDragging.value = false;
        window.removeEventListener('mousemove', onDrag);
        window.removeEventListener('mouseup', stopDrag);
    };

    const startDrag = (event: MouseEvent) => {
        if(!props.modal.isDraggable)return;
        if (isResizing.value) return;
        isDragging.value = true;
        dragStartPosition.value = {
            x: event.clientX,
            y: event.clientY
        };

        modalStore.bringToFront(props.modal.id);

        dragStartModalPosition.value = props.modal.position;

        window.addEventListener('mousemove', onDrag);
        window.addEventListener('mouseup', stopDrag);

        event.preventDefault();
    };

    const onResize = (event: MouseEvent) => {
        if (!isResizing.value) return;

        const deltaX = event.clientX - resizeStartPosition.value.x;
        const deltaY = event.clientY - resizeStartPosition.value.y;
    
        let newWidth = resizeStartSize.value.width;
        let newHeight = resizeStartSize.value.height;
        let newPosition = { ...resizeStartModalPosition.value };
    
        // 根据调整方向计算新尺寸和位置
        switch(resizeDirection.value) {
            case 'right':
                newWidth = Math.max(100, resizeStartSize.value.width + deltaX);
                break;
            case 'left':
                newWidth = Math.max(100, resizeStartSize.value.width - deltaX);
                newPosition.x = resizeStartModalPosition.value.x + deltaX;
                break;
            case 'bottom':
                newHeight = Math.max(100, resizeStartSize.value.height + deltaY);
                break;
            case 'top':
                newHeight = Math.max(100, resizeStartSize.value.height - deltaY);
                newPosition.y = resizeStartModalPosition.value.y + deltaY;
                break;
            case 'top-right':
                newWidth = Math.max(100, resizeStartSize.value.width + deltaX);
                newHeight = Math.max(100, resizeStartSize.value.height - deltaY);
                newPosition.y = resizeStartModalPosition.value.y + deltaY;
                break;
            case 'bottom-right':
                newWidth = Math.max(100, resizeStartSize.value.width + deltaX);
                newHeight = Math.max(100, resizeStartSize.value.height + deltaY);
                break;
            case 'bottom-left':
                newWidth = Math.max(100, resizeStartSize.value.width - deltaX);
                newHeight = Math.max(100, resizeStartSize.value.height + deltaY);
                newPosition.x = resizeStartModalPosition.value.x + deltaX;
                break;
            case 'top-left':
                newWidth = Math.max(100, resizeStartSize.value.width - deltaX);
                newHeight = Math.max(100, resizeStartSize.value.height - deltaY);
                newPosition.x = resizeStartModalPosition.value.x + deltaX;
                newPosition.y = resizeStartModalPosition.value.y + deltaY;
                break;
        }
    
        modalStore.updateModalSize(props.modal.id, {
            width: newWidth,
            height: newHeight
        });
    
        if (newPosition.x !== resizeStartModalPosition.value.x || newPosition.y !== resizeStartModalPosition.value.y) {
            modalStore.updateModalPosition(props.modal.id, newPosition);
        }
    };

    const stopResize = () => {
        isResizing.value = false;
        resizeDirection.value = '';
        window.removeEventListener('mousemove', onResize);
        window.removeEventListener('mouseup', stopResize);
    };

    const startResize = (event: MouseEvent, direction: string) => {
        if (!props.modal.isResizable) return
        if (isDragging.value) return;
    
        isResizing.value = true;
        resizeDirection.value = direction;
        resizeStartPosition.value = {
            x: event.clientX,
            y: event.clientY
        };
    
        resizeStartSize.value = {
            width: props.modal.size?.width || 200,
            height: props.modal.size?.height || 200
        };
    
        resizeStartModalPosition.value = {
            x: props.modal.position.x,
            y: props.modal.position.y
        };

        modalStore.bringToFront(props.modal.id);

        window.addEventListener('mousemove', onResize);
        window.addEventListener('mouseup', stopResize);

        event.preventDefault();
        event.stopPropagation(); // 防止触发拖动事件
    };
</script>
<template>
    <div class = "modal-container" v-if="modal.isActive" 
        :style="{ 
            left: modal.position.x + 'px', 
            top: modal.position.y + 'px', 
            width: modal.size?.width + 'px', 
            height: modal.size?.height + 'px', 
            zIndex: modal.zIndex,
            minWidth: modal.minSize?.width ? modal.minSize.width + 'px' : 'none',
            minHeight: modal.minSize?.height ? modal.minSize.height + 'px' : 'none',
            maxWidth: modal.maxSize?.width ? modal.maxSize.width + 'px' : 'none',
            maxHeight: modal.maxSize?.height ? modal.maxSize.height + 'px' : 'none'
        }">
        <div class="resize-handle resize-handle-right" @mousedown="startResize($event, 'right')"></div>
        <div class="resize-handle resize-handle-bottom" @mousedown="startResize($event, 'bottom')"></div>
        <div class="resize-handle resize-handle-left" @mousedown="startResize($event, 'left')"></div>
        <div class="resize-handle resize-handle-top" @mousedown="startResize($event, 'top')"></div>
        <div class="resize-handle resize-handle-top-right" @mousedown="startResize($event, 'top-right')"></div>
        <div class="resize-handle resize-handle-bottom-right" @mousedown="startResize($event, 'bottom-right')"></div>
        <div class="resize-handle resize-handle-bottom-left" @mousedown="startResize($event, 'bottom-left')"></div>
        <div class="resize-handle resize-handle-top-left" @mousedown="startResize($event, 'top-left')"></div>
        <div class = "modal-head" @mousedown="startDrag" >
            <div class = "modal-title-id-container">
                <div class="modal-title-container">
                    <div><b>{{ modal.title }}</b></div>
                </div>
                <!-- <div class="modal-id-container">
                    <div>ID: {{ modal.id }}</div>
                </div> -->
            </div>
            <div class = "modal-control">
                <el-button 
                    @click = "closeModal"
                    :style="{height: '100%',width: 'max(60px, 10%)',borderRadius: '16px'}"
                    type="primary"
                    :icon="Close"
                >
                </el-button>
            </div>
        </div>
        <div class = "modal-body">
            <component 
                v-if="modal.component" 
                :is="modal.component" 
                v-bind="modal.props"
            />
            <div v-else-if="modal.content" class = "modal-content">
                {{ modal.content }}
            </div>
        </div>
        <div class = "modal-footer">
            footer
        </div>
    </div>
</template>
<style scoped lang = "scss">
    .modal-container{
        position: fixed;
        display: flex;
        flex-direction: column;
        background-color: rgb(46, 130, 165);
        color: black;
        border-radius: 16px;
    }
    .modal-head{
        display: flex;
        min-height: 35px;
        height: 10%;
        width: 100%;
    }
    .modal-body, .modal-content{
        height: calc(100% - max(30px, 5%) - max(20px, 5%));
        display: flex;
        flex-direction: column;
    }
    .modal-footer{
        width: 100%;
        min-height: 20px;
        height: 5%;
        margin-left: 20px;
        display: flex;
        align-items: center;
    }
    .modal-control{
        height: 100%;
        display: flex;
        margin-left: auto;
    }
    .modal-title-id-container{
        height: 100%;
        margin-left: 20px;
        display: flex;
        flex-direction: column;
    }
    .modal-title-container{
        margin-top: 8px;
        font-size: calc(max(35px, 10%)*0.75);
        flex: 2;
    }
    .modal-id-container{
        font-size: calc(max(35px, 10%)*0.5*0.40);
        align-items: center;
        flex: 1;
    }
    // /* 调整大小手柄样式 */
    // .resize-handle {
    //     position: absolute;
    //     z-index: 10;
    //     background: transparent;
    // }

    // .resize-handle-right, .resize-handle-left {
    //     width: 6px;
    //     height: 100%;
    //     top: 0;
    //     cursor: ew-resize;
    // }

    // .resize-handle-right {
    //     right: -3px;
    // }

    // .resize-handle-left {
    //     left: -3px;
    // }

    // .resize-handle-top, .resize-handle-bottom {
    //     width: 100%;
    //     height: 6px;
    //     left: 0;
    //     cursor: ns-resize;
    // }

    // .resize-handle-top {
    //     top: -3px;
    // }

    // .resize-handle-bottom {
    //     bottom: -3px;
    // }

    // .resize-handle-top-right, .resize-handle-bottom-right, 
    // .resize-handle-bottom-left, .resize-handle-top-left {
    //     width: 12px;
    //     height: 12px;
    //     background: #585858;
    //     border: 1px solid #fff;
    // }

    // .resize-handle-top-right {
    //     top: -6px;
    //     right: -6px;
    //     cursor: ne-resize;
    // }

    // .resize-handle-bottom-right {
    //     bottom: -6px;
    //     right: -6px;
    //     cursor: se-resize;
    // }

    // .resize-handle-bottom-left {
    //     bottom: -6px;
    //     left: -6px;
    //     cursor: sw-resize;
    // }

    // .resize-handle-top-left {
    //     top: -6px;
    //     left: -6px;
    //     cursor: nw-resize;
    // }
</style>