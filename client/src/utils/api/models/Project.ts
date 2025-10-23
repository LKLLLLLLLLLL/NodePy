/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProjEdge } from './ProjEdge';
import type { ProjNode } from './ProjNode';
/**
 * A unified data structure for all data for a project.
 */
export type Project = {
    project_name: string;
    project_id: number;
    user_id: number;
    error_message?: (string | null);
    nodes: Array<ProjNode>;
    edges: Array<ProjEdge>;
};

