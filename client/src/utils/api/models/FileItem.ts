/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * The file item showed in the file list.
 */
export type FileItem = {
    key: string;
    filename: string;
    format: FileItem.format;
    size: number;
    modified_at: number;
    project_name: string;
};
export namespace FileItem {
    export enum format {
        PNG = 'png',
        JPG = 'jpg',
        PDF = 'pdf',
        WORD = 'word',
        TXT = 'txt',
        CSV = 'csv',
        XLSX = 'xlsx',
        JSON = 'json',
    }
}

