/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_upload_file_api_files_upload__project_id__post } from '../models/Body_upload_file_api_files_upload__project_id__post';
import type { DataView } from '../models/DataView';
import type { DeleteResponse } from '../models/DeleteResponse';
import type { File } from '../models/File';
import type { Project } from '../models/Project';
import type { ProjectList } from '../models/ProjectList';
import type { TaskResponse } from '../models/TaskResponse';
import type { UserFileList } from '../models/UserFileList';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * List Projects
     * List all projects for the current user.
     * @returns ProjectList List of projects retrieved successfully
     * @throws ApiError
     */
    public static listProjectsApiProjectListGet(): CancelablePromise<ProjectList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/project/list',
            errors: {
                500: `Internal server error`,
            },
        });
    }
    /**
     * Get Project
     * Get the full data structure of a project.
     * @param projectId
     * @returns Project Graph retrieved successfully
     * @throws ApiError
     */
    public static getProjectApiProjectProjectIdGet(
        projectId: number,
    ): CancelablePromise<Project> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/project/{project_id}',
            path: {
                'project_id': projectId,
            },
            errors: {
                403: `User has no access to this project`,
                404: `Project or graph not found`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Delete Project
     * Delete a project.
     * @param projectId
     * @returns void
     * @throws ApiError
     */
    public static deleteProjectApiProjectProjectIdDelete(
        projectId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/project/{project_id}',
            path: {
                'project_id': projectId,
            },
            errors: {
                403: `User has no access to this project`,
                404: `Project not found`,
                422: `Validation Error`,
                423: `Project is locked, it may be being edited by another process`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Create Project
     * Create a new project for a user.
     * Return project id.
     * @param projectName
     * @returns number Project created successfully
     * @throws ApiError
     */
    public static createProjectApiProjectCreatePost(
        projectName: string,
    ): CancelablePromise<number> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/project/create',
            query: {
                'project_name': projectName,
            },
            errors: {
                400: `Project name already exists`,
                404: `User not found`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Rename Project
     * Rename a project.
     * @param projectId
     * @param newName
     * @returns any Project renamed successfully
     * @throws ApiError
     */
    public static renameProjectApiProjectRenamePost(
        projectId: number,
        newName: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/project/rename',
            query: {
                'project_id': projectId,
                'new_name': newName,
            },
            errors: {
                400: `Project name already exists`,
                403: `User has no access to this project`,
                404: `Project not found`,
                422: `Validation Error`,
                423: `Project is locked, it may be being edited by another process`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Sync Project
     * Save a project to the database, if topology changed, enqueue a task to execute it.
     * If decide to execute, enqueues a Celery task. Use
     * the returned `task_id` to subscribe to the websocket status endpoint
     * `/nodes/status/{task_id}`.
     * @param requestBody
     * @returns TaskResponse Task accepted and running
     * @throws ApiError
     */
    public static syncProjectApiProjectSyncPost(
        requestBody: Project,
    ): CancelablePromise<TaskResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/project/sync',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Invalid thumbnail data`,
                403: `User has no access to this project`,
                404: `Project not found`,
                422: `Validation Error`,
                423: `Project is locked, it may be being edited by another process`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Upload File
     * Upload a file to a project. Return the saved file info.
     * @param projectId
     * @param nodeId
     * @param formData
     * @returns File File uploaded successfully
     * @throws ApiError
     */
    public static uploadFileApiFilesUploadProjectIdPost(
        projectId: number,
        nodeId: string,
        formData: Body_upload_file_api_files_upload__project_id__post,
    ): CancelablePromise<File> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/files/upload/{project_id}',
            path: {
                'project_id': projectId,
            },
            query: {
                'node_id': nodeId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                400: `Bad Request - invalid file or parameters`,
                403: `Forbidden - not allowed`,
                422: `Validation Error`,
                500: `Internal Server Error`,
                507: `Insufficient Storage - user storage limit exceeded`,
            },
        });
    }
    /**
     * Get File Content
     * Get the content of a file by its key and project id.
     * The project id is used to verify the access permission.
     *
     * **important: if user want to re upload a file, you need to delete the old file first,
     * otherwise the file space may not be released.**
     * @param key
     * @returns any Binary file content
     * @throws ApiError
     */
    public static getFileContentApiFilesKeyGet(
        key: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/files/{key}',
            path: {
                'key': key,
            },
            errors: {
                403: `Forbidden - not allowed to access this file`,
                404: `File not found`,
                422: `Validation Error`,
                500: `Internal Server Error`,
            },
        });
    }
    /**
     * Delete File
     * Delete a file by its key and project id.
     * The project id is used to verify the access permission.
     * @param key
     * @returns DeleteResponse File deleted successfully
     * @throws ApiError
     */
    public static deleteFileApiFilesKeyDelete(
        key: string,
    ): CancelablePromise<DeleteResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/files/{key}',
            path: {
                'key': key,
            },
            errors: {
                403: `Forbidden - not allowed to access this file`,
                404: `File not found`,
                422: `Validation Error`,
                500: `Internal Server Error`,
            },
        });
    }
    /**
     * List Files
     * @returns UserFileList List of files for the user
     * @throws ApiError
     */
    public static listFilesApiFilesListGet(): CancelablePromise<UserFileList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/files/list',
            errors: {
                404: `Not Found`,
                500: `Internal Server Error`,
            },
        });
    }
    /**
     * Get Node Data
     * Get the data generated by a node.
     * @param dataId
     * @returns DataView Data retrieved successfully
     * @throws ApiError
     */
    public static getNodeDataApiDataDataIdGet(
        dataId: number,
    ): CancelablePromise<DataView> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/data/{data_id}',
            path: {
                'data_id': dataId,
            },
            errors: {
                403: `User has no access to this data`,
                404: `Data not found`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Spa Fallback
     * @param fullPath
     * @returns any Successful Response
     * @throws ApiError
     */
    public static spaFallbackFullPathGet(
        fullPath: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/{full_path}',
            path: {
                'full_path': fullPath,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
