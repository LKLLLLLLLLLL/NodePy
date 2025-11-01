import { defineStore } from 'pinia';
import { ref } from 'vue';
import { DefaultService } from '../utils/api/services/DefaultService';
import { useModalStore } from './modalStore';
import { ApiError } from '@/utils/api';
import { ElMessage } from 'element-plus';
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

    const projectList = ref<ProjectList>({userid: default_uid,projects: []});
    const currentProjectName = ref<string>(default_pname);
    const currentProjectId = ref<number>(default_pid);
    const currentProject = ref<Project>(default_project);
    const toBeDeleted = ref<{name: string,id: number}>({id: default_delete_pid,name: default_delete_pname});
    const toBeRenamed = ref<{name: string,id: number}>({id: default_rename_pid,name: default_rename_pname});

    const modalStore = useModalStore();

    // async function openProject(id: number){
    //     console.log('Openning project by ID:',id)
    //     try{
    //         const success = await getProject(id);
    //         return success;
    //     }
    //     catch(error){
    //         ElMessage('Unknown error occurred.(open)');
    //         return false;
    //     }
    // }

    function refresh(){
        currentProject.value = default_project;
        currentProjectId.value = default_pid;
        currentProjectName.value = default_pname;
        toBeDeleted.value = {
            id: default_delete_pid,
            name: default_delete_pname
        };
        toBeRenamed.value = {
            id: default_rename_pid,
            name: default_rename_pname
        };
    }

    async function initializeProjects(){
        console.log('Getting all projects');
        try{
            const response = await DefaultService.listProjectsApiProjectListGet();
            projectList.value = response;
            refresh();
            return true;
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(500):
                        ElMessage('服务器内部错误');
                        break;
                }
            }
            else{
                ElMessage('Unknown error occurred.');
            }
            return false;
        }
    }

    async function createProject(){
        console.log('Creating project by name:', currentProjectName.value);
        try{
            const response = await DefaultService.createProjectApiProjectCreatePost(currentProjectName.value);
            if(response)ElMessage('项目' + currentProjectName.value + '创建成功');
            currentProjectId.value = response;
            initializeProjects();
            return true;
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(400):
                        ElMessage('项目名称已存在');
                        break;
                    case(404):
                        ElMessage('用户未找到');
                        break;
                    case(422):
                        ElMessage('验证错误');
                        break;
                    case(500):
                        ElMessage('服务器内部错误');
                        break;
                }
            }
            else{
                ElMessage('Unknown error occurred.');
            }
            return false;
        }
    }

    async function deleteProject(id: number){
        console.log('Deleting project by ID:', id);
        try{
            const response = await DefaultService.deleteProjectApiProjectProjectIdDelete(id);
            if(response==null)ElMessage('项目' + id + '删除成功');
            initializeProjects();
            return true;
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(403):
                        ElMessage('没有访问权限');
                        break;
                    case(404):
                        ElMessage('找不到项目');
                        break;
                    case(422):
                        ElMessage('验证错误');
                        break;
                    case(423):
                        ElMessage('项目被锁定，可能正在被其他进程访问');
                        break;
                    case(500):
                        ElMessage('服务器内部错误');
                        break;
                }
            }
            else{
                ElMessage('Unknown error occurred.');
            }
            return false;
        }
    }
    
    async function getProject(id: number){
        console.log('Getting project by ID:', id)
        try{
            const response = await DefaultService.getProjectApiProjectProjectIdGet(id);
            if(response)ElMessage('项目' + id + '获取成功');
            currentProject.value=response;
            return true;
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(403):
                        ElMessage('没有访问权限');
                        break;
                    case(404):
                        ElMessage('找不到项目');
                        break;
                    case(422):
                        ElMessage('验证错误');
                        break;
                    case(500):
                        ElMessage('服务器内部错误');
                        break;
                }
            }
            else{
                ElMessage('Unknown error occurred.');
            }
            return false;
        }
    }

    async function renameProject(id: number,name: string){
        console.log('Renaming project:',id,'New name is',name);
        try{
            const response = await DefaultService.renameProjectApiProjectRenamePost(id,name);
            ElMessage('项目' + id + '改名成功');
            initializeProjects();
            return true;
        }
        catch(error){
            if(error instanceof ApiError){
                switch(error.status){
                    case(403):
                        ElMessage('没有访问权限');
                        break;
                    case(404):
                        ElMessage('找不到项目');
                        break;
                    case(422):
                        ElMessage('验证错误');
                        break;
                    case(500):
                        ElMessage('服务器内部错误');
                        break;
                }
            }
            else{
                ElMessage('Unknown error occurred.');
            }
            return false;
        }
    }

    return{
        projectList,
        currentProjectId,
        currentProjectName,
        currentProject,
        toBeDeleted,
        toBeRenamed,
        getProject,
        createProject,
        deleteProject,
        renameProject,
        initializeProjects
    }
});