import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { NodeInstance } from '@/types/nodeType';

//在这里定义节点的状态管理，包括节点的增删改查等操作以及向后端提交数据等，定义后return出去即可
export const useNodeStore = defineStore('node', () => {
    const nodes = ref<NodeInstance[]>([]);
    return {nodes};
});