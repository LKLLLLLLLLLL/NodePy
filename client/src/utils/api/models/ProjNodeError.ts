/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ProjNodeError = {
    type: ProjNodeError.type;
    params: (Array<string> | null);
    inputs: (Array<string> | null);
    message: (Array<string> | string);
};
export namespace ProjNodeError {
    export enum type {
        PARAM = 'param',
        VALIDATION = 'validation',
        EXECUTION = 'execution',
    }
}

