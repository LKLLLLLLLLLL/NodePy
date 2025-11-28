<script lang="ts" setup>
    import { useUserStore } from '@/stores/userStore';
    import type { ExploreListItem } from '@/utils/api';
    import { computed } from 'vue';
    import { useRouter } from 'vue-router';

    const props = defineProps<{
        item: ExploreListItem
    }>()

    const router = useRouter()

    const userStore = useUserStore()

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
            params: { projectId: props.item.project_id }
        });
        window.open(route.href, '_blank');
    }

    function handleCopy(){
        // TODO: 实现复制功能
    }

</script>
<template>
    <div class="project-card" @click="handleOpenExample">
        <!-- 缩略图区域 -->
        <div class="project-thumb">
            <div class="thumb-content">
                <template v-if="thumbSrc">
                    <img :src="thumbSrc" alt="thumb" class="thumb-img" />
                </template>
                <template v-else>
                    <div class="thumb-placeholder-large">{{ (props.item.project_name || '').charAt(0) || 'E' }}</div>
                </template>
            </div>
        </div>

        <!-- 项目信息区域 -->
        <div class="project-info">
            <div class="project-title">{{ item.project_name }}</div>
            <div class="project-meta">
                <span class="meta-item">修改: {{ formatDate(item.updated_at) }}</span>
                <span class="meta-item">创建: {{ formatDate(item.created_at) }}</span>
                <span class="meta-item">作者: {{ item.owner_name }}</span>
            </div>
        </div>
    </div>
</template>
<style lang="scss" scoped>
.project-card{
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
.project-card:focus{
    outline: 2px solid rgba(26,115,190,0.12);
    outline-offset: 2px;
}
.project-card:hover{
    transform: translateY(-4px) scale(1.015);
    box-shadow: 0 12px 28px rgba(31,45,61,0.12);
}
.project-thumb{
    position: relative;
    width: 100%;
    padding-top: 56.25%; /* 16:9 */
    display: block;
    background: #f6f9fb;
}
.thumb-content{
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}
.thumb-content > img.thumb-img{
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.thumb-img{
    width:100%;
    height:100%;
    object-fit:cover;
}
.thumb-placeholder-large{
    width:100%;
    height:100%;
    display:flex;
    align-items:center;
    justify-content:center;
    color: #4b5d6a;
    font-size:48px;
    font-weight:700;
}
.project-info{
    padding: 14px 16px;
    display:flex;
    flex-direction:column;
    gap:6px;
    min-height: 75px; /* ensure new-card height matches cards with meta */
}
.project-title{
    font-weight:700;
    font-size:15px;
    color:#102335;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}
.project-meta{
    display:flex;
    gap:10px;
    font-size:12px;
    color:#6b7f8f;
}
.meta-item{opacity:0.95}

@media (max-width: 480px){
    .project-card{ max-width: 100%; }
}
</style>
