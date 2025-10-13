import type { Component } from 'vue';

export interface ModalInstance{
    id: string;
    title: string;
    content?: string;
    isActive: boolean;
    component?: Component;
    zIndex?: number;
    position?: {x: number, y: number};
    props?: Record<string, any>;
    onSubmit?: () => void;
}