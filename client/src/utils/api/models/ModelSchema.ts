/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ColType } from './ColType';
import type { server__models__schema__ModelSchema__Type } from './server__models__schema__ModelSchema__Type';
/**
 * The schema of Model data, including model type and other metadata.
 */
export type ModelSchema = {
    model_type: server__models__schema__ModelSchema__Type;
    input_cols: Record<string, ColType>;
    output_cols: Record<string, ColType>;
};

