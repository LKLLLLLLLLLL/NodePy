import { defineStore } from 'pinia';
import { ref } from 'vue';
import { DefaultService } from '../utils/api/services/DefaultService';
import { useModalStore } from './modalStore';
import { useRouter } from 'vue-router';
import { ApiError } from '@/utils/api';
import { ElMessage } from 'element-plus';
import { type ProjectListItem ,type ProjectList,type Project} from '@/utils/api';

export const useProjectStore = defineStore('project', () => {
    const projectList = ref<ProjectList>({userid: 10086,projects: []});
    const currentProjectName = ref<string>("default_name");
    const currentProjectId = ref<number>(10086);
    const currentProject = ref<Project>();

    const modalStore = useModalStore();

    async function openProject(id: number){
        console.log('Openning project by ID:',id)
        try{
            const success = await getProject(id);
            return success;
        }
        catch(error){
            ElMessage('Unknown error occurred.(open)');
            return false;
        }
    }
    async function initializeProjects(){
        console.log('Getting all projects');
        try{
            const response = await DefaultService.listProjectsApiProjectListGet();
            if(response)ElMessage('获取项目列表成功');
            projectList.value = response
            console.log(response);
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
            currentProjectId.value = response
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
            console.log(response);
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
            currentProject.value=response
            console.log(response);
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
            console.log(response);
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
        openProject,
        createProject,
        deleteProject,
        getProject,
        renameProject,
        initializeProjects
    }
});