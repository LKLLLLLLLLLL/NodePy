import type { Project } from "@/utils/api"
import type { BaseNode } from "./nodeTypes"
import type {Edge} from '@vue-flow/core'
import type {Ref} from 'vue'

export interface vueFlowProject extends Omit<Project, 'workflow'> {
    workflow: {
        error_message?: (string | null),
        nodes: Ref<BaseNode[]>,
        edges: Ref<Edge[]>
    }
}