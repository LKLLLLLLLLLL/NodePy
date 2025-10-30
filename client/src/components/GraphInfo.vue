<script lang="ts" setup>
    import { DefaultService } from '@/utils/api';
    import { ref, computed } from 'vue';
    import { useGraphStore } from '@/stores/graphStore';
    import SvgIcon from '@jamescoyle/vue-icon';
    import { mdiAlertCircleOutline, mdiCheckCircleOutline } from '@mdi/js';
    import Loading from './tools/Loading.vue';

    const mdiWarn = mdiAlertCircleOutline;
    const mdiSuccess = mdiCheckCircleOutline;

    const props = defineProps<{
            is_syncing: boolean;
            syncing_err_msg: string;
        }>();

    const graphStore = useGraphStore();

    const lastSyncTime = computed(() => graphStore.project.updated_at);
    // setInterval(() => {console.log('lastSyncTime:', lastSyncTime.value)}, 100);
    const proj_err_msg = computed(() => graphStore.project.workflow.error_message);
</script>
<template>
    <div class="graph-info-container">
        <div class="update-status-block">
            <div class="gi-is-syncing" v-if="is_syncing">
                <span>同步中...</span>
            </div>
            <div class="gi-syncing-err-msg" v-else-if="syncing_err_msg">
                <span class="error-message">Sync Error: {{ syncing_err_msg }}</span>
            </div>
            <div class="gi-last-sync-time" v-else>
                <div class="gi-sync-success"><svg-icon type="mdi" :path="mdiSuccess"></svg-icon><div>同步成功</div></div>
                <div>上次同步 {{ lastSyncTime ? new Date(lastSyncTime).toLocaleString(undefined, { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) : 'N/A' }}</div>
            </div>
        </div>
        <div class="workflow-status-block">
            <div class="gi-workflow-status-normal" v-if="!proj_err_msg">
                <span>Workflow Status: Normal</span>
            </div>
            <div class="gi-workflow-status-error error" v-else>
                <svg-icon type="mdi" :path=mdiWarn></svg-icon><div class="error-message">Error({{ proj_err_msg }})</div>
            </div>
        </div>
    </div>
</template>
<style lang="scss" scoped>
.graph-info-container {
    // background-color: rgba(255, 255, 255, 0.9);
    color: rgba(0, 0, 0, 0.3);
    font-size: 20px;
    // font-weight: 800;
    padding: 10px;
    .gi-workflow-status-error{
        display: flex;
        height: 20px;
        align-items: center;
    }
    .gi-sync-success {
        display: flex;
        align-items: center;
        margin-bottom: 5px;
    }
    svg {
        height: 20px;
        width: 20px;
        vertical-align: middle;
        margin-right: 5px;
    }
    .update-status-block {
        margin: 10px;
    }
    .workflow-status-block {
        margin: 10px;
    }
}

</style>
