/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ColType } from './ColType';
/**
 * The schema of File data, including file format and other metadata.
 */
export type FileSchema = {
    format: FileSchema.format;
    col_types?: (Record<string, ColType> | null);
};
export namespace FileSchema {
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

