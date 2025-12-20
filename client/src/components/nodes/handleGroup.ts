import { useVueFlow } from "@vue-flow/core"


export const setGroupIdsByBFS = () => {

    const {getNodes, getEdges, updateNode} = useVueFlow('main')
    const nodes = getNodes
    const edges = getEdges

    const nodeMap = new Map(nodes.value.map(node => [node.id, node]));
    const edgeMap = new Map();
    
    // 构建邻接表（包含入度和出度）
    edges.value.forEach(edge => {
        if (!edgeMap.has(edge.source)) {
            edgeMap.set(edge.source, []);
        }
        edgeMap.get(edge.source).push({
            target: edge.target,
            sourceHandle: edge.sourceHandle
        });
        
        if (!edgeMap.has(edge.target)) {
            edgeMap.set(edge.target, []);
        }
        edgeMap.get(edge.target).push({
            source: edge.source,
            targetHandle: edge.targetHandle
        });
    });
    
    // 创建更新列表，避免在循环中直接修改响应式数组
    const updates = [];
    
    // 找到所有 BeginNode 和 EndNode
    const beginNodes = nodes.value.filter(n => n.type === 'ForEachRowBeginNode');
    const endNodes = nodes.value.filter(n => n.type === 'ForEachRowEndNode');
    
    // 从每个 BeginNode 开始正向 BFS
    beginNodes.forEach(beginNode => {
        bfsFromBeginNode(beginNode, nodeMap, edgeMap, updates, 'ForEachRowEndNode');
    });
    
    // 从每个 EndNode 开始逆向 BFS
    endNodes.forEach(endNode => {
        bfsFromEndNode(endNode, nodeMap, edgeMap, updates, 'ForEachRowBeginNode');
    });


    // 找到所有 BeginNode2 和 EndNode2
    const beginNodes2 = nodes.value.filter(n => n.type === 'ForRollingWindowBeginNode');
    const endNodes2 = nodes.value.filter(n => n.type === 'ForRollingWindowEndNode');
    // 从每个 BeginNode2 开始正向 BFS
    beginNodes2.forEach(beginNode => {
        bfsFromBeginNode(beginNode, nodeMap, edgeMap, updates, 'ForRollingWindowEndNode');
    });
    
    // 从每个 EndNode2 开始逆向 BFS
    endNodes2.forEach(endNode => {
        bfsFromEndNode(endNode, nodeMap, edgeMap, updates, 'ForRollingWindowBeginNode');
    });
    
    // 应用所有更新
    if (updates.length > 0) {
        updates.forEach(({ id, groupId }) => {
            updateNode(id, node => ({
                data: {
                    ...node.data,
                    groupId: groupId
                }
            }))
        });
    }
};

const bfsFromBeginNode = (beginNode, nodeMap, edgeMap, updates, stopNode) => {
    const queue: any[] = [];
    const visited = new Set([beginNode.id]);
    
    // 获取开始节点的所有边
    const startEdges = edgeMap.get(beginNode.id) || [];
    
    // 从开始节点往后搜索
    startEdges.forEach(edge => {
        if (!visited.has(edge.target)) {
            queue.push({ nodeId: edge.target, groupId: beginNode.data.groupId });
            visited.add(edge.target);
        }
    });
    
    while (queue.length > 0) {
        const { nodeId, groupId } = queue.shift();
        const currentNode = nodeMap.get(nodeId);
        
        if (!currentNode) continue;
        
        // 遇到 stopNode 就停止（不加入后继节点）
        if (currentNode.type === stopNode) {
            continue;
        }
        
        updates.push({ id: currentNode.id, groupId });
        
        // 获取当前节点的所有出边和入边
        const nEdges = edgeMap.get(currentNode.id) || [];
        
        // 加入相邻节点
        nEdges.forEach(edge => {
            if (!visited.has(edge.target)) {
                queue.push({ nodeId: edge.target, groupId });
                visited.add(edge.target);
            }
            if(!visited.has(edge.source)) {
                queue.push({ nodeId: edge.source, groupId });
                visited.add(edge.source);
            }
        });
    }
};

const bfsFromEndNode = (endNode, nodeMap, edgeMap, updates, stopNode) => {
    const queue: any[] = [];
    const visited = new Set([endNode.id]);
    
    // 获取结束节点的所有边
    const startEdges = edgeMap.get(endNode.id) || [];
    
    // 从结束节点往前搜索
    startEdges.forEach(edge => {
        if (!visited.has(edge.source)) {
            queue.push({ nodeId: edge.source, groupId: endNode.data.groupId });
            visited.add(edge.source);
        }
    });
    
    while (queue.length > 0) {
        const { nodeId, groupId } = queue.shift();
        const currentNode = nodeMap.get(nodeId);
        
        if (!currentNode) continue;
        
        // 遇到 stopNode 就停止（不加入前驱节点）
        if (currentNode.type === stopNode) {
            continue;
        }
        
        updates.push({ id: currentNode.id, groupId });
        
        // 获取当前节点的所有出边和入边
        const nEdges = edgeMap.get(currentNode.id) || [];
        
        // 加入相邻节点
        nEdges.forEach(edge => {
            if (!visited.has(edge.source)) {
                queue.push({ nodeId: edge.source, groupId });
                visited.add(edge.source);
            }
            if(!visited.has(edge.target)) {
                queue.push({ nodeId: edge.target, groupId });
                visited.add(edge.target);
            }
        });
    }
};


export const deleteGroupIdWhenDeleteEdge = (removedEdge: any) => {
    const { updateNode, findNode, getNodes } = useVueFlow('main');
    const EXCLUDED_NODE_TYPES = [
    'ForEachRowBeginNode',
    'ForEachRowEndNode', 
    'ForRollingWindowBeginNode',
    'ForRollingWindowEndNode'
    ];
    const { source: src} = removedEdge;
    const source = findNode(src)
    if(source) {
        const groupId = source.data.groupId
        getNodes.value.forEach(node => {
            if(node.data.groupId === groupId && !EXCLUDED_NODE_TYPES.includes(node.type)) {
                updateNode(node.id, n => ({
                    data: {
                        ...n.data,
                        groupId: undefined
                    }
                }))
            }
        })
    }
}


// 处理特殊节点删除
export const handleSpecialNodeDelete = (removedNode: any) => {
    const { updateNode, removeNodes, getNodes } = useVueFlow('main');

    const { id: removedNodeId, type: removedNodeType, data: removedNodeData } = removedNode;
    const removedGroupId = removedNodeData?.groupId;

    if (!removedGroupId) return;

    // 节点类型映射：Begin -> End
    const NODE_TYPE_MAP = {
        'ForEachRowBeginNode': 'ForEachRowEndNode',
        'ForEachRowEndNode': 'ForEachRowBeginNode',
        'ForRollingWindowBeginNode': 'ForRollingWindowEndNode',
        'ForRollingWindowEndNode': 'ForRollingWindowBeginNode'
    };

    // 1. 移除同groupId的其他节点的groupId
    const nodesToUpdate = getNodes.value.filter(node => 
        node.id !== removedNodeId && 
        node.data?.groupId === removedGroupId &&
        !Object.keys(NODE_TYPE_MAP).includes(node.type) // 排除所有特殊节点
    );

    if (nodesToUpdate.length > 0) {
        nodesToUpdate.forEach(node => {
            updateNode(node.id, n => ({
                data: {
                    ...n.data,
                    groupId: undefined
                }
            }))
        })
    }

    // 2. 如果是Begin节点，删除对应的End节点以及容器；反之亦然
    const pairedNodeType = NODE_TYPE_MAP[removedNodeType];
    if (pairedNodeType) {
        const pairedNode = getNodes.value.find(node => 
            node.type === pairedNodeType && 
            node.data?.groupId === removedGroupId
        );
        
        if (pairedNode) {
            // 删除配对节点, 以及容器
            removeNodes([pairedNode.id, removedGroupId]);
        }
    }
};