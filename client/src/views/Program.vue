<script lang="ts" setup>
    import ProjectDemoFrame from '@/components/ProjectDemoFrame.vue';
    function handleClick(){

    }

    function handleAdd(){

    }

    const ids = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20'];

</script>

<template>
    <div class="program-container">
        <el-row :gutter="20" class="demo-row">
            <el-col 
                :span="6"
                v-for="id in ids"
                :key="id"
                class="demo-column"
            >
                <ProjectDemoFrame 
                    :handleClick="handleClick"
                    :id="id"
                >
                </ProjectDemoFrame>
            </el-col>
            <el-col :span="6" class="demo-column">
                <ProjectDemoFrame :handleClick="handleClick"></ProjectDemoFrame>
            </el-col>
        </el-row>
        
    </div>
</template>

<style lang="scss" scoped>
.program-container{
    min-height: 0;
    width: 100%;
    gap: 40px;
    margin: 20px 20px 20px 20px;
    flex-shrink: 0;
}
.demo-column{
    padding: 30px;
}
.demo-row{
    width: 100%;
}
</style>