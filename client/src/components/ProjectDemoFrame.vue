<script lang="ts" setup>
    import { Plus } from '@element-plus/icons-vue';
    const props = defineProps<{
        handleClick: () => void
        id?: string
    }>()
</script>
<template>
    <div class="project-demo-frame">
        <slot>
            <div class="default-content">
                <el-icon 
                    @click="props.handleClick"
                    :size="60" 
                    color="grey"
                >
                    <Plus />
                </el-icon>
            </div>
        </slot>
    </div>
</template>
<style lang="scss" scoped>
    .project-demo-frame {
        width: 240px;
        height: 150px;
        border-radius: 16px;
        justify-content: center;
        align-items: center;
        display: flex;
        color: white;
        background-color: black;
        flex-shrink: 0;
    }
</style>