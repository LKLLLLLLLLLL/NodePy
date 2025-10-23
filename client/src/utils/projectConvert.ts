import type { Node, Edge } from '@vue-flow/core'
import type { Project } from './api'

export const getProject = (project_name: string, project_id: number, user_id: number, nodes: Node[], edges: Edge[], error_message?: string): Project => {
    const graphNodes = nodes.map(n => {
        return {
            id: n.id,
            position: n.position,
            type: n.type as string,
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
            src_port: e.sourceHandle as string,
            tar_port: e.targetHandle as string
        }
    })
    return {
        project_name,
        project_id,
        user_id,
        error_message,
        nodes: graphNodes,
        edges: graphEdges
    }
}

export const parseProject = (g: Project): {
    nodes: Node[],
    edges: Edge[]
} => {
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