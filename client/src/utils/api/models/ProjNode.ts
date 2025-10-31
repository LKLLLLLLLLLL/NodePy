/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataRef } from './DataRef';
import type { ProjNodeError } from './ProjNodeError';
import type { Schema } from './Schema';
/**
 * Store the node topological state and running results.
 */
export type ProjNode = {
    id: string;
    type: string;
    param: Record<string, any>;
    runningtime?: (number | null);
    schema_out?: Record<string, Schema>;
    data_out?: Record<string, DataRef>;
    error?: (ProjNodeError | null);
};

