<script lang="ts" setup>
    import {ref} from 'vue';
    import { useProjectStore } from '@/stores/projectStore';

    const projectStore = useProjectStore();

    function openEditor(id?: string){
        if(id){
            const newWindow = window.open('/editor'+'/'+id, '_blank')
        } 
        else {
            const newWindow = window.open('/editor', '_blank')
        }
    }

    function onCreateProject(){
        projectStore.createProject();
        openEditor();
    }

</script>
<template>
    <el-form class="add-project-container">
        <el-form-item label="Project Name">
            <el-input placeholder="Enter project name" v-model="projectStore.currentProjectName"></el-input>
        </el-form-item>
        <el-form-item label="Description">
            <el-switch></el-switch>
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="onCreateProject">Create Project</el-button>
        </el-form-item>
    </el-form>
</template>
<style lang="scss" scoped>
</style>