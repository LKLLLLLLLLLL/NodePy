/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FileSchema } from './FileSchema';
import type { ModelSchema } from './ModelSchema';
import type { server__models__schema__Schema__Type } from './server__models__schema__Schema__Type';
import type { TableSchema } from './TableSchema';
export type Schema = {
    type: server__models__schema__Schema__Type;
    tab?: (TableSchema | null);
    file?: (FileSchema | null);
    model?: (ModelSchema | null);
};

