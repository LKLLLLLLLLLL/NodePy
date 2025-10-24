import { defineStore } from 'pinia';
import { ref } from 'vue';
import { DefaultService } from '../utils/api/services/DefaultService';
import { useModalStore } from './modalStore';
import { ApiError } from '@/utils/api';
import { ElMessage } from 'element-plus';

export const useProjectStore = defineStore('project', () => {
    const projects = ref<{id:string,name:string}[]>([]);
    const currentProjectName = ref<string>('我的测试项目1');

    const modalStore = useModalStore();

    function initializeProjects(){

    }

    async function createProject(){
        console.log('Creating project by name:', currentProjectName.value);
        try{
            const response = await DefaultService.createProjectApiProjectCreatePost(currentProjectName.value);
            ElMessage('项目' + currentProjectName.value + '创建成功');
            console.log(response);
            return true;
        }
        catch(error){
            console.log(error);
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
                }
            }
            else{
                ElMessage('Unknown error occurred.')
            }
        }
    }

    async function deleteProject(id: number){
        console.log('Deleting project by ID:', id);
        try{
            const response = await DefaultService.deleteProjectApiProjectProjectIdDelete(id);
            ElMessage('项目' + id + '删除成功');
        }
        catch(error){
            console.log(error);
            if(error instanceof ApiError){

            }
        }
    }
    
    function getProject(id: number){

    }

    function renameProject(){
        console.log('Renaming project:');
    }

    function saveProject(){
        console.log('Saving project:');
    }

    return{
        projects,
        currentProjectName,
        createProject,
        deleteProject,
        getProject,
        renameProject,
        saveProject,
        initializeProjects
    }
});