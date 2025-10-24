/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProjWorkflow } from './ProjWorkflow';
/**
 * A unified data structure for all data for a project.
 */
export type Project = {
    project_name: string;
    project_id: number;
    user_id: number;
    workflow: ProjWorkflow;
};

