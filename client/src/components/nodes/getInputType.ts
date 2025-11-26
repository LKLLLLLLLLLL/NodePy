import { useVueFlow } from "@vue-flow/core"
import { Type } from "@/utils/api"
export const getInputType = (nodeId: string, handleId: string): Type | 'all' => {
    const {edges, findNode} = useVueFlow('main')
    const edge = edges.value.find(e => e.target === nodeId && e.targetHandle === handleId)
    const srcNode = edge ? findNode(edge.source) : undefined
    if(srcNode) {
        if(edge?.data === 'error') return 'all'
        return srcNode.data.schema_out?.[edge?.sourceHandle as string]?.type || 'all'
    }else {
        return 'all'
    }
}
