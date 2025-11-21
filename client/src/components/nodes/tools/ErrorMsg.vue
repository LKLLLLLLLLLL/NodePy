<template>
    <div class="node-err nodrag" @click.stop>
        <div v-for="err in errMsg" class="err-item">
            <svg-icon type="mdi" :path=mdiWarn class="errIcon"></svg-icon>
            <span class="errText">{{ err }}</span>
        </div>
    </div>
</template>

<script lang="ts" setup>
    //@ts-ignore
    import SvgIcon from '@jamescoyle/vue-icon'
    import { mdiAlertCircleOutline } from '@mdi/js'


    const mdiWarn = mdiAlertCircleOutline
    const props = defineProps<{
        errMsg: string[]
    }>()

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;

    .node-err {
        display: flex;
        flex-direction: column;
        gap: 4px;
        .err-item {
            @include info-message;
            color: $error-message-color;
            max-width: 2 * $node-width;
            width: max-content;
            display: flex;
            gap: 4px;
            .errIcon {
                flex-shrink: 0;
                width: 14px; 
            }
            .errText {
                transform: translateY(1.2px);
            }
        }
        max-width: 2 * $node-width;
        position: absolute;
        top: 100%;
        pointer-events: none;
    } //  errmsg style

</style>