import { useVueFlow } from "@vue-flow/core"


export const hasInputEdge = (nodeId: string, handleId: string): boolean => {
    const {getEdges} = useVueFlow('main')
    return getEdges.value.some(e => e.target === nodeId && e.targetHandle === handleId)
}