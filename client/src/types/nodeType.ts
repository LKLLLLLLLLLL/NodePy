export interface NodeInstance{
    id: string;
    name: string;
    type: string;
    position: {x: number, y: number};
    props: Record<string, any>;
    inputs: string[];
    outputs: string[];
    isSelected: boolean;
    isActive: boolean;
    zIndex: number;
    width?: number;
    height?: number;
}