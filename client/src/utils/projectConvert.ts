import type { BaseNode } from '@/types/nodeTypes'
import type { Project } from './api'
import type { vueFlowProject } from '@/types/vueFlowProject'
import { useVueFlow } from '@vue-flow/core'


const {setNodes, setEdges} = useVueFlow('main')


export const getProject = (vp: vueFlowProject): Project => {
    const nodes = vp.workflow.nodes.map(n => {
        return {
            id: n.id,
            type: n.type,
            param: n.data.param,
            runningtime: n.data.runningtime,
            schema_out: n.data.schema_out,
            data_out: n.data.data_out,
            error: n.data.error,
            hint: n.data.hint
        }
    })
    const ui_state = vp.workflow.nodes.map(n => {
        return {
            id: n.id,
            x: n.position.x,
            y: n.position.y
        }
    })
    const edges = vp.workflow.edges.map(e => {
        return {
            id: e.id,
            src: e.source,
            tar: e.target,
            src_port: e.sourceHandle as string,
            tar_port: e.targetHandle as string
        }
    })
    return {
        project_name: vp.project_name,
        project_id: vp.project_id,
        user_id: vp.user_id,
        workflow: {
            error_message: vp.workflow.error_message,
            nodes: nodes,
            edges: edges
        },
        updated_at: vp.updated_at,
        thumb: vp.thumb,
        ui_state: {
            nodes: ui_state
        },
        editable: vp.editable
    }
}

export const initVueFlowProject = (p: Project, vp: vueFlowProject) => {
    let nodes:BaseNode[] = []
    for(let i = 0; i < p.workflow.nodes.length; i++) {
        nodes.push({
            id: p.workflow.nodes[i]?.id as string,
            type: p.workflow.nodes[i]?.type as string,
            position: {
                x: p.ui_state.nodes[i]?.x as number,
                y: p.ui_state.nodes[i]?.y as number
            },
            data: {
                param: p.workflow.nodes[i]?.param as Record<string, any>,
                runningtime: p.workflow.nodes[i]?.runningtime,
                schema_out: p.workflow.nodes[i]?.schema_out,
                data_out: p.workflow.nodes[i]?.data_out,
                error: p.workflow.nodes[i]?.error,
                hint: p.workflow.nodes[i]?.hint
            }
        })
    }
    const edges = p.workflow.edges.map(e => {
        return {
            id: e.id,
            source: e.src,
            sourceHandle: e.src_port,
            target: e.tar,
            targetHandle: e.tar_port,
            type: "NodePyEdge"
        }
    })


    vp.project_id = p.project_id
    vp.project_name = p.project_name
    vp.user_id = p.user_id
    vp.workflow.error_message = p.workflow.error_message
    setNodes(nodes)
    setEdges(edges)
    vp.updated_at = p.updated_at
    vp.thumb = p.thumb
    vp.editable = p.editable
}

export const writeBackVueFLowProject = (p: Project, vp: vueFlowProject) => {
    if(vp.workflow.nodes.length !== p.workflow.nodes.length) {
        console.log('vp length:', vp.workflow.nodes.length, 'p length:', p.workflow.nodes.length, 'p is out of date')
        return
    }
    for(let i = 0; i < p.workflow.nodes.length; i++) {  //@ts-ignore
        vp.workflow.nodes[i].data.data_out = p.workflow.nodes[i]?.data_out  //@ts-ignore
        vp.workflow.nodes[i].data.error = p.workflow.nodes[i]?.error    //@ts-ignore
        vp.workflow.nodes[i].data.runningtime = p.workflow.nodes[i]?.runningtime    //@ts-ignore
        vp.workflow.nodes[i].data.schema_out = p.workflow.nodes[i]?.schema_out  //@ts-ignore
        vp.workflow.nodes[i].data.hint = p.workflow.nodes[i]?.hint
    }
    vp.workflow.error_message = p.workflow.error_message
}
