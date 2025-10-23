import type { Node, Edge } from '@vue-flow/core'
import type { Project } from './api'

export const getGraph = (nodes: Node[], edges: Edge[]) => {
    const graphNodes = nodes.map(n => {
        return {
            id: n.id,
            position: n.position,
            type: n.type,
            param: n.data.param,
            runningtime: n.data.runningtime,
            schema_out: n.data.schema_out,
            data_out: n.data.data_out,
            error: n.data.error
        }
    })
    const graphEdges = edges.map(e => {
        return {
            id: e.id,
            src: e.source,
            tar: e.target,
            src_port: e.sourceHandle,
            tar_port: e.targetHandle
        }
    })
    return {
        nodes: graphNodes,
        edges: graphEdges
    }
}

export const parseGraph = (g: Project) => {
    const graphNodes = g.nodes.map(n => {
        return {
            id: n.id,
            type: n.type,
            position: n.position,
            data: {
                param: n.param,
                runningtime: n.runningtime,
                schema_out: n.schema_out,
                data_out: n.data_out,
                error: n.error
            }
        }
    })
    const graphEdges = g.edges.map(e => {
        return {
            id: e.id,
            source: e.src,
            sourceHandle: e.src_port,
            target: e.tar,
            targetHandle: e.tar_port
        }
    })
    return {
        nodes: graphNodes,
        edges: graphEdges
    }
}