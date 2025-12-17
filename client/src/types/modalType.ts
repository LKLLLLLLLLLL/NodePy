import type { Component } from 'vue';

export interface ModalInstance{
    id: string;
    title: string;
    content?: string;
    isActive: boolean;
    isResizable: boolean;
    isDraggable: boolean;
    isResultModal?: boolean;
    isModal?: boolean; // 添加新属性，控制是否启用模态模式
    component?: Component;
    zIndex?: number;
    position: {x: number, y: number};
    size: {width: number, height: number};
    minSize?: {width: number, height: number};
    maxSize?: {width: number, height: number};
    props?: Record<string, any>;
    onSubmit?: () => void;
}