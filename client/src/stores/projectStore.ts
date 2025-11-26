import { defineStore } from 'pinia';
import { ref } from 'vue';
import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory';
import { useModalStore } from './modalStore';
import { ApiError, type ProjectListItem, type ProjectSetting } from '@/utils/api';
import notify from '@/components/Notification/notify';
import { type ProjectList, type Project, type ProjUIState } from '@/utils/api';

export const useProjectStore = defineStore('project', () => {

    const default_pname: string = "default_name"
    const default_pid: number = 10086
    const default_uid: number = 114514
    const default_updated: number = 0
    const default_puistate: ProjUIState = {nodes: []}
    const default_project: Project = {
        project_name: default_pname,
        project_id: default_pid,
        user_id: default_uid,
        workflow: {
            nodes: [],
            edges: []
        },
        updated_at: default_updated,
        ui_state: default_puistate
    }

    const default_delete_pid: number = 11111111
    const default_delete_pname: string = 'toBeDeleted'
    const default_rename_pid: number = 22222222
    const default_rename_pname: string = 'toBeRenamed'//原名
    const default_whether_show: boolean = false//默认不公开
    const default_project_setting: ProjectSetting = {
        project_name: default_pname,
        show_to_explore: default_whether_show
    }

    const projectList = ref<ProjectList>({userid: default_uid,projects: []});
    const currentProjectName = ref<string>(default_pname);
    const currentProjectId = ref<number>(default_pid);
    const currentProject = ref<Project>(default_project);
    const currentWhetherShow = ref<boolean>(default_whether_show)
    const toBeDeleted = ref<{id: number,name: string}>({id: default_delete_pid,name: default_delete_pname});
    const toBeRenamed = ref<{id: number,name: string}>({id: default_rename_pid,name: default_rename_pname});
    const toBeUpdated = ref<ProjectSetting>(default_project_setting)

    // 项目ID到名称的映射
    const projectIdToNameMap = ref<Map<number, string>>(new Map());

    const modalStore = useModalStore();
    const authService = AuthenticatedServiceFactory.getService();

    // async function openProject(id: number){
    //     console.log('Openning project by ID:',id)
    //     try{
    //         const success = await getProject(id);
    //         return success;
    //     }
    //     catch(error){
    //         notify('Unknown error occurred.(open)');
    //         return false;
    //     }
    // }

    function refresh(){
        currentProject.value = default_project;
        currentProjectId.value = default_pid;
        currentProjectName.value = default_pname;
        currentWhetherShow.value = default_whether_show
        toBeDeleted.value = {
            id: default_delete_pid,
            name: default_delete_pname
        };
        toBeRenamed.value = {
            id: default_rename_pid,
            name: default_rename_pname
        };
        toBeUpdated.value = default_project_setting
    }

    // 更新项目ID到名称的映射
    function updateProjectIdToNameMap(projects: ProjectListItem[]) {
        projectIdToNameMap.value.clear();
        projects.forEach(project => {
            projectIdToNameMap.value.set(project.project_id, project.project_name);
        });
    }

    async function initializeProjects(){
        console.log('Getting all projects');
        try{
            const response = await authService.listProjectsApiProjectListGet();
            projectList.value = response;
            // 初始化项目ID到名称的映射
            updateProjectIdToNameMap(response.projects);
            refresh();
            return true;
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(500):
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
                        break;
                }
            }
            else{
                notify({
                    message: 'Unknown error occurred',
                    type: 'error'
                });
            }
            return false;
        }
    }

    async function createProject(){
        console.log('Creating project by name:', currentProjectName.value);
        try{
            const name = currentProjectName.value
            const response = await authService.createProjectApiProjectCreatePost(currentProjectName.value);
            if(response){
                notify({
                    message: '项目' + name + '创建成功',
                    type: 'success'
                });
                // 在映射中添加新创建的项目
                projectIdToNameMap.value.set(response, name);
            }
            currentProjectId.value = response;
            return true;
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(400):
                        notify({
                            message: '项目名称已存在',
                            type: 'error'
                        });
                        break;
                    case(404):
                        notify({
                            message: '用户未找到',
                            type: 'error'
                        });
                        break;
                    case(422):
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    case(500):
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
                        break;
                }
            }
            else{
                notify({
                    message: 'Unknown error occurred',
                    type: 'error'
                });
            }
            return false;
        }
    }

    async function deleteProject(id: number){
        try{
            // 获取要删除的项目名称
            const projectName = projectIdToNameMap.value.get(id) || '未知项目';
            const response = await authService.deleteProjectApiProjectProjectIdDelete(id);
            if(response==null){
                notify({
                    message: '项目' + projectName + '删除成功',
                    type: 'success'
                });
                // 从映射中删除项目
                projectIdToNameMap.value.delete(id);
            }
            return true;
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(403):
                        notify({
                            message: '没有访问权限',
                            type: 'error'
                        });
                        break;
                    case(404):
                        notify({
                            message: '找不到项目',
                            type: 'error'
                        });
                        break;
                    case(422):
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    case(423):
                        notify({
                            message: '项目被锁定，可能正在被其他进程访问',
                            type: 'error'
                        });
                        break;
                    case(500):
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
                        break;
                }
            }
            else{
                notify({
                    message: 'Unknown error occurred',
                    type: 'error'
                });
            }
            return false;
        }
    }

    async function getProject(id: number){
        console.log('Getting project by ID:', id)
        try{
            const response = await authService.getProjectApiProjectProjectIdGet(id);
            if(response){
                notify({
                    message: '项目' + id + '获取成功',
                    type: 'info'
                });
            }
            currentProject.value=response;
            return true;
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(403):
                        notify({
                            message: '没有访问权限',
                            type: 'error'
                        });
                        break;
                    case(404):
                        notify({
                            message: '找不到项目',
                            type: 'error'
                        });
                        break;
                    case(422):
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    case(500):
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
                        break;
                }
            }
            else{
                notify({
                    message: 'Unknown error occurred',
                    type: 'error'
                });
            }
            return false;
        }
    }

    async function getProjectSettings(id: number){
        console.log('Getting project:', id)
        try{
            const response = await authService.getProjectSettingApiProjectSettingProjectIdGet(id)
            toBeUpdated.value = response
            currentWhetherShow.value = response.show_to_explore!
            currentProjectName.value = response.project_name
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(403):
                        notify({
                            message: '没有访问权限',
                            type: 'error'
                        });
                        break;
                    case(404):
                        notify({
                            message: '找不到项目',
                            type: 'error'
                        });
                        break;
                    case(422):
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    case(500):
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
                        break;
                }
            }
            else{
                notify({
                    message: 'Unknown error occurred',
                    type: 'error'
                });
            }
        }
    }

    async function updateProjectSetting(id: number){
        console.log('Updating project:',id);
        try{
            const setting: ProjectSetting = {
                project_name: currentProjectName.value,
                show_to_explore: currentWhetherShow.value
            }
            const response = await authService.updateProjectSettingApiProjectUpdateSettingPost(id,setting);
            
            // 更新映射中的项目名称
            if (projectIdToNameMap.value.has(id)) {
                projectIdToNameMap.value.set(id, currentProjectName.value);
            }
            
            notify({
                message: '项目' + setting.project_name + '更新成功',
                type: 'success'
            });
            return response;
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(400):
                        notify({
                            message: '项目信息更新失败',
                            type: 'error'
                        })
                        break;
                    case(403):
                        notify({
                            message: '没有访问权限',
                            type: 'error'
                        });
                        break;
                    case(404):
                        notify({
                            message: '找不到项目',
                            type: 'error'
                        });
                        break;
                    case(422):
                        notify({
                            message: '验证错误',
                            type: 'error'
                        });
                        break;
                    case(423):
                        notify({
                            message: '项目被锁定，可能正在被其他进程访问',
                            type: 'error'
                        })
                        break;
                    case(500):
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        });
                        break;
                }
            }
            else{
                notify({
                    message: 'Unknown error occurred',
                    type: 'error'
                });
            }
        }
    }

    return{
        projectList,
        currentProjectId,
        currentProjectName,
        currentProject,
        currentWhetherShow,
        toBeDeleted,
        toBeRenamed,
        toBeUpdated,
        projectIdToNameMap, // 导出映射
        getProject,
        createProject,
        deleteProject,
        getProjectSettings,
        updateProjectSetting,
        initializeProjects
    }
});