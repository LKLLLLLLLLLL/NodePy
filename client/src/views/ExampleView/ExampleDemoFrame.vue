<script lang="ts" setup>
    import type { ExploreListItem } from '@/utils/api';
    import { useRouter } from 'vue-router';
    import { computed } from 'vue';

    const props = defineProps<{
        item: ExploreListItem
    }>()

    const router = useRouter()

    // 计算属性：将 Base64 转换为完整的 Data URL
    const thumbSrc = computed(() => {
        if (!props.item.thumb) return null
        
        // 如果已经是 Data URL，直接返回
        if (props.item.thumb.startsWith('data:image')) {
            return props.item.thumb
        }
        
        // 如果是纯 Base64，添加前缀
        return `data:image/png;base64,${props.item.thumb}`
    })

    function parseDate(v: number | null) {
        if (!v) return null;
        const d = new Date(v);
        if (isNaN(d.getTime())) return null;
        return d;
    }

    function formatDate(v: number | null) {
        const d = parseDate(v);
        if (!d) return '';
        return new Intl.DateTimeFormat('zh-CN', { 
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit' 
        }).format(d);
    }

    async function handleOpenExample(){
        const route = router.resolve({
            name: 'editor-example',
            params: { exampleName: props.item.project_name }
        });
        window.open(route.href, '_blank');
    }

    function handleCopy(){
        // TODO: 实现复制功能
    }

</script>
<template>
    <div class="example-card">
        <!-- 缩略图区域 -->
        <div class="example-thumb">
            <div v-if="thumbSrc" class="thumb-content">
                <img :src="thumbSrc" alt="项目缩略图" class="thumb-img">
            </div>
            <div v-else class="thumb-placeholder">
                E
            </div>
        </div>

        <!-- 项目信息区域 -->
        <div class="example-info">
            <div class="example-title">{{ item.project_name }}</div>
            <div class="example-meta">
                <span class="meta-item">修改: {{ formatDate(item.updated_at) }}</span>
                <span class="meta-item">创建: {{ formatDate(item.created_at) }}</span>
            </div>
        </div>

        <!-- 操作按钮区域 -->
        <div class="example-actions">
            <el-button type="primary" @click="handleOpenExample">打开示例</el-button>
            <!-- <el-button @click="handleCopy">复制</el-button> -->
        </div>
    </div>
</template>
<style lang="scss" scoped>
    .example-card {
        width: 100%;
        max-width: 420px;
        background: #ffffff;
        border-radius: 12px;
        color: #1f2d3d;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        cursor: pointer;
        box-shadow: 0 6px 25px rgba(31,45,61,0.08);
        transition: transform 140ms cubic-bezier(.2,.9,.3,1), box-shadow 140ms cubic-bezier(.2,.9,.3,1);
    }

    .example-card:hover {
        transform: translateY(-4px) scale(1.015);
        box-shadow: 0 12px 28px rgba(31,45,61,0.12);
    }

    .example-thumb {
        position: relative;
        width: 100%;
        padding-top: 56.25%; /* 16:9 */
        display: block;
        background: #f6f9fb;
    }

    .thumb-content {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .thumb-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .thumb-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 28px;
        color: #6b7f8f;
    }

    .example-info {
        padding: 16px;
        flex: 1;
        display: flex;
        flex-direction: column;
    }

    .example-title {
        color: #102335;
        font-weight: 600;
        font-size: 18px;
        margin-bottom: 12px;
        word-break: break-word;
    }

    .example-meta {
        display: flex;
        flex-direction: column;
        gap: 6px;
        font-size: 12px;
        color: #6b7f8f;
        margin-top: auto;
    }

    .meta-item {
        display: flex;
        align-items: center;
    }

    .example-actions {
        padding: 0 16px 16px;
        display: flex;
        gap: 10px;
    }

    .example-actions .el-button {
        flex: 1;
    }
</style>