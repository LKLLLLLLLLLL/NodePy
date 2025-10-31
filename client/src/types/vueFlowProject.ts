import type { Project } from "@/utils/api"
import type { BaseNode } from "./nodeTypes"
import type {Edge} from '@vue-flow/core'

export interface vueFlowProject extends Omit<Project, 'workflow'|'ui_state'> {
    workflow: {
        error_message?: (string | null),
        nodes: BaseNode[],
        edges: Edge[]
    }
}