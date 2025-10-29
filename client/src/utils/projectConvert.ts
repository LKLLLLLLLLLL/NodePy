import type { Project, ProjEdge, ProjNode } from './api'
import type { vueFlowProject } from '@/types/vueFlowProject'


export const getProject = (p: vueFlowProject): Project => {
    const graphNodes: ProjNode[] = p.workflow.nodes.value.map(n => {
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
    const graphEdges:ProjEdge[] = p.workflow.edges.value.map(e => {
        return {
            id: e.id,
            src: e.source,
            tar: e.target,
            src_port: e.sourceHandle as string,
            tar_port: e.targetHandle as string
        }
    })
    return {
        project_name: p.project_name,
        project_id: p.project_id,
        user_id: p.user_id,
        workflow: {
            error_message: p.workflow.error_message,
            nodes: graphNodes,
            edges: graphEdges
        },
        updated_at: p.updated_at,
        thumb: p.thumb
    }
}

export const parseProject = (p: Project, tar: vueFlowProject) => {
    const graphNodes = p.workflow.nodes.map(n => {
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
    const graphEdges = p.workflow.edges.map(e => {
        return {
            id: e.id,
            source: e.src,
            sourceHandle: e.src_port,
            target: e.tar,
            targetHandle: e.tar_port,
            type: "NodePyEdge"
        }
    })

    if(tar) {
        tar.project_id = p.project_id
        tar.project_name = p.project_name
        tar.user_id = p.user_id
        tar.workflow.error_message = p.workflow.error_message
        tar.workflow.edges.value = graphEdges
        tar.workflow.nodes.value = graphNodes
        tar.updated_at = p.updated_at
        tar.thumb = p.thumb
    }
}
