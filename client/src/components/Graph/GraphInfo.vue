<script lang="ts" setup>
    import { ref, computed } from 'vue';
    import { useGraphStore } from '@/stores/graphStore';
    import SvgIcon from '@jamescoyle/vue-icon';
    import { mdiAlertCircleOutline, mdiCheckCircleOutline } from '@mdi/js';
    import Loading from '../Loading.vue';

    const mdiWarn = mdiAlertCircleOutline;
    const mdiSuccess = mdiCheckCircleOutline;

    const props = defineProps<{
            is_syncing: boolean;
            syncing_err_msg: string;
        }>();

    const graphStore = useGraphStore();

    const lastSyncTime = computed(() => graphStore.project.updated_at);
    const proj_err_msg = computed(() => graphStore.project.workflow.error_message);
</script>
<template>
    <div class="graph-info-container">
        <div class="update-status-block">
            <div class="gi-is-syncing" v-if="is_syncing" style="margin-left: 25px;">
                <span>同步中...</span>
            </div>
            <div class="gi-syncing-err-msg error-message" v-else-if="syncing_err_msg">
                <svg-icon type="mdi" :path=mdiWarn></svg-icon>
                <div>同步失败: {{ syncing_err_msg }}</div>
            </div>
            <div class="gi-last-sync-time" v-else>
                <div class="gi-sync-success success-message">
                    <svg-icon type="mdi" :path="mdiSuccess"></svg-icon>
                    <div>已同步到云端</div>
                </div>

            </div>
            <div style="margin-left: 24px;">上次同步 {{ lastSyncTime ? new Date(lastSyncTime).toLocaleString(undefined, { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) : 'N/A' }}
            </div>
        </div>
        <div class="workflow-status-block">
            <div class="gi-workflow-status-normal success-message" v-if="!proj_err_msg">
                <svg-icon type="mdi" :path="mdiSuccess"></svg-icon>
                <div>未在节点图中检测到问题</div>
            </div>
            <div class="gi-workflow-status-error error-message" v-else>
                <svg-icon type="mdi" :path=mdiWarn></svg-icon>
                <div>节点图运行失败：</div>
            </div>
            <div class="gi-workflow-error-message error-message" v-if="proj_err_msg">
                {{ proj_err_msg }}
            </div>
        </div>
    </div>
</template>
<style lang="scss" scoped>
@use "../../common/global.scss" as *;
.graph-info-container {
    @include info-message();
    color: rgba(0, 0, 0, 0.3);
    padding: 10px 10px;
    margin-left: 10px;
    .gi-workflow-status-error{
        display: flex;
        align-items: center;
    }
    .gi-sync-success {
        display: flex;
        align-items: center;
    }
    .gi-workflow-status-normal {
        display: flex;
        align-items: center;
    }
    .gi-syncing-err-msg {
        display: flex;
        align-items: center;
    }
    svg {
        width: 18px;
        vertical-align: middle;
        margin-right: 5px;
    }
    .update-status-block {
        padding: 0px 0px;
        height: 50px;
    }
    .workflow-status-block {
        padding: 0px 0px;
        height: 50px;
    }

    .gi-workflow-error-message {
        margin-left: 26px;
        max-width: 33vw;
    }
}

</style>
