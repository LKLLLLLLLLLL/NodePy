export interface NodeInstance{
    id: string;
    name: string;
    type: string;
    position?: {x: number, y: number};
    props?: Record<string, any>;
    inputs: string[];
    outputs: string[];
    isSelected?: boolean;
    isActive?: boolean;
    zIndex?: number;
    width?: number;
    height?: number;
    result?: {
        resultContent?: any,
        resultType?: NodeType
    }
}
export type NodeType = 'file' | 'image' | 'chart' | 'table' | 'number' | 'string' | 'boolean'

import type {Node} from '@vue-flow/core';