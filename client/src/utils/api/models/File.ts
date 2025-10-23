/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * A abstract file class to represent files managed by FileManager.
 */
export type File = {
    key: string;
    filename: string;
    format: File.format;
    size: number;
};
export namespace File {
    export enum format {
        PNG = 'png',
        JPG = 'jpg',
        PDF = 'pdf',
        CSV = 'csv',
    }
}

