import { defineStore } from 'pinia';
import { ref } from 'vue';
import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory';
import { useModalStore } from './modalStore';
import { ApiError, type ProjectSetting } from '@/utils/api';
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

    async function initializeProjects(){
        console.log('Getting all projects');
        try{
            const response = await authService.listProjectsApiProjectListGet();
            projectList.value = response;
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
            }
            currentProjectId.value = response;
            initializeProjects();
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
        console.log('Deleting project by ID:', id);
        try{
            const response = await authService.deleteProjectApiProjectProjectIdDelete(id);
            if(response==null){
                notify({
                    message: '项目' + id + '删除成功',
                    type: 'success'
                });
            }
            initializeProjects();
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
            notify({
                message: '项目' + id + '更新成功',
                type: 'success'
            });
            initializeProjects();
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
        getProject,
        createProject,
        deleteProject,
        getProjectSettings,
        updateProjectSetting,
        initializeProjects
    }
});
