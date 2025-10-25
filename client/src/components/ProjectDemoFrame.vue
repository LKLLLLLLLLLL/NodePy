<script lang="ts" setup>
    import { Plus } from '@element-plus/icons-vue';
    const props = defineProps<{
        handleOpenExistingProject?: (id:number)=>void
        handleCreateNewProject?: ()=>void
        id: number
    }>()
</script>

<template>
    <div class="project-demo-container">
        <div class="project-demo-picture">
            <slot name="picture">
                <div class="default-picture"
                    @click="props.handleCreateNewProject">
                    <el-icon 
                        :size="60" 
                        color="grey"
                    >
                        <Plus />
                    </el-icon>
                </div>
            </slot>
        </div>
        <div class="'project-demo-info'">
            <slot name="info">
            </slot>
        </div>
    </div>
</template>

<style lang="scss" scoped>
    .project-demo-container {
        width: 240px;
        height: 150px;
        border-radius: 16px;
        display: flex;
        color: white;
        background-color: rgb(44, 152, 218);
        flex-shrink: 0;
        flex-direction: column;
    }
    .project-demo-picture{
        width: 100%;
        height: 120px;
        justify-content: center;
        align-items: center;
    }
    .project-demo-info{
        width: 100%;
        height: 30px;
    }
    .default-picture{
        justify-content: center;
        align-items: center;
    }
</style>