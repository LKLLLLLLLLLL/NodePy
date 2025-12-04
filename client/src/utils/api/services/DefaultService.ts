/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_upload_file_api_files_upload__project_id__post } from '../models/Body_upload_file_api_files_upload__project_id__post';
import type { DataView } from '../models/DataView';
import type { ExploreList } from '../models/ExploreList';
import type { File } from '../models/File';
import type { LoginRequest } from '../models/LoginRequest';
import type { Project } from '../models/Project';
import type { ProjectList } from '../models/ProjectList';
import type { ProjectSetting } from '../models/ProjectSetting';
import type { ProjUIState } from '../models/ProjUIState';
import type { SignupRequest } from '../models/SignupRequest';
import type { TaskResponse } from '../models/TaskResponse';
import type { TokenResponse } from '../models/TokenResponse';
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
     * Copy Project
     * Copy a read only project, and create a new project under the current user.
     * Return new project id.
     * @param projectId
     * @returns number Project copied successfully
     * @throws ApiError
     */
    public static copyProjectApiProjectCopyProjectIdPost(
        projectId: number,
    ): CancelablePromise<number> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/project/copy/{project_id}',
            path: {
                'project_id': projectId,
            },
            errors: {
                400: `Project name already exists`,
                404: `Project not found`,
                422: `Validation Error`,
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
     * Get Project Setting
     * Get the settings of a project.
     * @param projectId
     * @returns ProjectSetting Project setting retrieved successfully
     * @throws ApiError
     */
    public static getProjectSettingApiProjectSettingProjectIdGet(
        projectId: number,
    ): CancelablePromise<ProjectSetting> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/project/setting/{project_id}',
            path: {
                'project_id': projectId,
            },
            errors: {
                403: `User has no access to this project`,
                404: `Project not found`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Update Project Setting
     * Update the settings of a project.
     * @param projectId
     * @param requestBody
     * @returns any Project setting updated successfully
     * @throws ApiError
     */
    public static updateProjectSettingApiProjectUpdateSettingPost(
        projectId: number,
        requestBody: ProjectSetting,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/project/update_setting',
            query: {
                'project_id': projectId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Project setting update failed`,
                403: `User has no access to this project`,
                404: `Project not found`,
                422: `Validation Error`,
                423: `Project is locked, it may be being edited by another process`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Sync Project Ui
     * Only save the ui of a project. Make sure the ui_state corresponds to the workflow in last sync.
     * @param projectId
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static syncProjectUiApiProjectSyncUiPost(
        projectId: number,
        requestBody: ProjUIState,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/project/sync_ui',
            query: {
                'project_id': projectId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
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
     * Signup
     * sign up a new user, return a JWT token (no need to login again)
     * @param requestBody
     * @returns TokenResponse Successful Response
     * @returns any User created successfully
     * @throws ApiError
     */
    public static signupApiAuthSignupPost(
        requestBody: SignupRequest,
    ): CancelablePromise<TokenResponse | any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/auth/signup',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Username or email already registered`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Login
     * Login user and return JWT tokens
     * @param requestBody
     * @returns TokenResponse Login successful
     * @throws ApiError
     */
    public static loginApiAuthLoginPost(
        requestBody: LoginRequest,
    ): CancelablePromise<TokenResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/auth/login',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Invalid username or password`,
                422: `Validation Error`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Refresh Access Token
     * Use Refresh Token to get a new Access Token if access token expired
     * @returns TokenResponse Access token refreshed successfully
     * @throws ApiError
     */
    public static refreshAccessTokenApiAuthRefreshPost(): CancelablePromise<TokenResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/auth/refresh',
            errors: {
                401: `Invalid refresh token`,
                500: `Internal server error`,
            },
        });
    }
    /**
     * Logout
     * Logout user by clearing the Refresh Token
     * @returns string Logged out successfully
     * @throws ApiError
     */
    public static logoutApiAuthLogoutPost(): CancelablePromise<Record<string, string>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/auth/logout',
        });
    }
    /**
     * Get Explore Projects
     * Get the list of projects that are marked as 'show in explore'.
     * @returns ExploreList Successful Response
     * @throws ApiError
     */
    public static getExploreProjectsApiExploreExploreProjectsGet(): CancelablePromise<ExploreList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/explore/explore/projects',
        });
    }
    /**
     * Get Current User Info
     * Get current authenticated user's information.
     * @returns any Current user information retrieved successfully
     * @throws ApiError
     */
    public static getCurrentUserInfoApiUserMeGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/user/me',
            errors: {
                401: `Unauthorized`,
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
