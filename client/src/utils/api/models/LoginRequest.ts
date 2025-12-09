/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type LoginRequest = {
    type: LoginRequest.type;
    identifier: string;
    password: string;
};
export namespace LoginRequest {
    export enum type {
        USERNAME = 'username',
        EMAIL = 'email',
    }
}

