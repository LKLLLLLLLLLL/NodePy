/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FileItem } from './FileItem';
/**
 * The list of files owned by a user.
 */
export type UserFileList = {
    user_id: number;
    files: Array<FileItem>;
    total_size: number;
    used_size: number;
};

