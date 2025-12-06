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
        const newPosition = { ...resizeStartModalPosition.value };

        // 获取最大最小限制
        const maxWidth = props.modal.maxSize?.width ?? Number.MAX_SAFE_INTEGER;
        const maxHeight = props.modal.maxSize?.height ?? Number.MAX_SAFE_INTEGER;
        const minWidth = props.modal.minSize?.width ?? 100;
        const minHeight = props.modal.minSize?.height ?? 100;

        // 对于Result弹窗的特殊处理：只允许向左调整大小
        const isResultModal = (props.modal as any).isResultModal;

        // 根据调整方向计算新尺寸和位置
        switch(resizeDirection.value) {
            case 'right':
                // 如果是Result弹窗，则不允许向右调整大小
                if (!isResultModal) {
                    newWidth = Math.max(minWidth, Math.min(maxWidth, resizeStartSize.value.width + deltaX));
                }
                break;
            case 'left':
                newWidth = Math.max(minWidth, Math.min(maxWidth, resizeStartSize.value.width - deltaX));
                // 只有当宽度实际改变时才更新位置
                if (newWidth !== resizeStartSize.value.width) {
                    newPosition.x = resizeStartModalPosition.value.x + (resizeStartSize.value.width - newWidth);
                }
                break;
            case 'bottom':
                newHeight = Math.max(minHeight, Math.min(maxHeight, resizeStartSize.value.height + deltaY));
                break;
            case 'top':
                // 如果是Result弹窗，则不允许向上调整大小
                if (!isResultModal) {
                    newHeight = Math.max(minHeight, Math.min(maxHeight, resizeStartSize.value.height - deltaY));
                    // 只有当高度实际改变时才更新位置
                    if (newHeight !== resizeStartSize.value.height) {
                        newPosition.y = resizeStartModalPosition.value.y + (resizeStartSize.value.height - newHeight);
                    }
                }
                break;
            case 'top-right':
                // 如果是Result弹窗，则不允许向右或向上调整大小
                if (!isResultModal) {
                    newWidth = Math.max(minWidth, Math.min(maxWidth, resizeStartSize.value.width + deltaX));
                }
                if (!isResultModal) {
                    newHeight = Math.max(minHeight, Math.min(maxHeight, resizeStartSize.value.height - deltaY));
                    // 只有当高度实际改变时才更新位置
                    if (newHeight !== resizeStartSize.value.height) {
                        newPosition.y = resizeStartModalPosition.value.y + (resizeStartSize.value.height - newHeight);
                    }
                }
                break;
            case 'bottom-right':
                // 如果是Result弹窗，则不允许向右调整大小
                if (!isResultModal) {
                    newWidth = Math.max(minWidth, Math.min(maxWidth, resizeStartSize.value.width + deltaX));
                }
                newHeight = Math.max(minHeight, Math.min(maxHeight, resizeStartSize.value.height + deltaY));
                break;
            case 'bottom-left':
                newWidth = Math.max(minWidth, Math.min(maxWidth, resizeStartSize.value.width - deltaX));
                newHeight = Math.max(minHeight, Math.min(maxHeight, resizeStartSize.value.height + deltaY));
                // 只有当宽度实际改变时才更新位置
                if (newWidth !== resizeStartSize.value.width) {
                    newPosition.x = resizeStartModalPosition.value.x + (resizeStartSize.value.width - newWidth);
                }
                break;
            case 'top-left':
                newWidth = Math.max(minWidth, Math.min(maxWidth, resizeStartSize.value.width - deltaX));
                // 如果是Result弹窗，则不允许向上调整大小
                if (!isResultModal) {
                    newHeight = Math.max(minHeight, Math.min(maxHeight, resizeStartSize.value.height - deltaY));
                    // 只有当高度实际改变时才更新位置
                    if (newHeight !== resizeStartSize.value.height) {
                        newPosition.y = resizeStartModalPosition.value.y + (resizeStartSize.value.height - newHeight);
                    }
                }
                // 只有当宽度实际改变时才更新位置
                if (newWidth !== resizeStartSize.value.width) {
                    newPosition.x = resizeStartModalPosition.value.x + (resizeStartSize.value.width - newWidth);
                }
                break;
        }

        // 只有当尺寸实际改变时才更新
        if (newWidth !== props.modal.size?.width || newHeight !== props.modal.size?.height) {
            modalStore.updateModalSize(props.modal.id, {
                width: newWidth,
                height: newHeight
            });
        }

        // 只有当位置实际改变时才更新
        if (newPosition.x !== props.modal.position.x || newPosition.y !== props.modal.position.y) {
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
        // 对于Result弹窗的特殊处理：只允许向左调整大小
        const isResultModal = (props.modal as any).isResultModal;
        
        // 如果是Result弹窗，只允许left、bottom-left、top-left方向的调整
        if (isResultModal) {
            if (direction !== 'left' && direction !== 'bottom-left' && direction !== 'top-left') {
                return;
            }
        }
        
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
    <div class = "modal-container controller-style" v-if="modal.isActive"
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
                    :style="{height: '100%',width: 'max(60px, 10%)',borderRadius: '12px',border: 'none'}"
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

        </div>
    </div>
</template>
<style scoped lang = "scss">
    @use '../common/global.scss' as *;
    .modal-container{
        position: fixed;
        display: flex;
        flex-direction: column;
        border-radius: 15px;
        box-sizing: border-box; /* 添加盒模型计算 */
    }
    .modal-head{
        display: flex;
        min-height: 35px;
        width: 100%;
        cursor: move; /* 头部显示移动光标 */
    }
    .modal-body, .modal-content{
        height: calc(100% - max(30px, 5%) - max(20px, 5%));
        margin-top: 10px;
        margin-left: 20px;
        margin-right: 20px;
        display: flex;
        flex-direction: column;
        overflow: hidden; /* 改为hidden，让内部组件控制滚动 */
    }
    .modal-footer{
        width: 100%;
        min-height: 35px;
        margin-left: 20px;
        margin-right: 20px;
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
    /* 调整大小手柄样式 - 隐藏可见元素，仅保留鼠标样式 */
    .resize-handle {
        position: absolute;
        z-index: 10;
        background: transparent;
    }

    /* 移除所有可见的背景色和边框 */
    .resize-handle-top-right, .resize-handle-bottom-right,
    .resize-handle-bottom-left, .resize-handle-top-left {
        width: 12px;
        height: 12px;
        background: transparent;
        border: none;
    }

    .resize-handle-right, .resize-handle-left {
        width: 6px;
        height: 100%;
        top: 0;
        cursor: ew-resize;
        background: transparent;
    }

    .resize-handle-right {
        right: -3px;
    }

    .resize-handle-left {
        left: -3px;
    }

    .resize-handle-top, .resize-handle-bottom {
        width: 100%;
        height: 6px;
        left: 0;
        cursor: ns-resize;
        background: transparent;
    }

    .resize-handle-top {
        top: -3px;
    }

    .resize-handle-bottom {
        bottom: -3px;
    }

    .resize-handle-top-right {
        top: -6px;
        right: -6px;
        cursor: ne-resize;
    }

    .resize-handle-bottom-right {
        bottom: -6px;
        right: -6px;
        cursor: se-resize;
    }

    .resize-handle-bottom-left {
        bottom: -6px;
        left: -6px;
        cursor: sw-resize;
    }

    .resize-handle-top-left {
        top: -6px;
        left: -6px;
        cursor: nw-resize;
    }
</style>