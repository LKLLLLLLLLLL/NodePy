/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { File } from './File';
import type { TableView } from './TableView';
/**
 * A dict-like view of data, for transmitting or json serialization.
 */
export type DataView = {
    type: DataView.type;
    value: (TableView | string | number | boolean | File);
};
export namespace DataView {
    export enum type {
        INT = 'int',
        FLOAT = 'float',
        STR = 'str',
        BOOL = 'bool',
        TABLE = 'Table',
        FILE = 'File',
    }
}

