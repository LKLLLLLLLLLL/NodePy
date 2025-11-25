<template>
    <span class="timer">
        <svg-icon type="mdi" :path="waitingPath" v-if="timerStatus === 'waiting'"></svg-icon>
        <svg-icon type="mdi" :path="runningPath" v-if="timerStatus === 'running'" class="running"></svg-icon>
        <svg-icon type="mdi" :path="finishedPath" v-if="timerStatus === 'finished'"></svg-icon>
        <svg-icon type="mdi" :path="errorPath" v-if="timerStatus === 'error'"></svg-icon>
        {{ timerStatus === 'waiting' ? '' : display }}
    </span>
</template>

<script lang="ts" setup>
    import { onTimerMsg } from '@/utils/task'; //@ts-ignore
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiCached, mdiCheck, mdiClose, mdiUpdate } from '@mdi/js'; // waiting
import { computed, onMounted, onUnmounted, ref } from 'vue';

    const props = defineProps<{
        nodeId: string,
        defaultTime?: number | null
    }>()
    const waitingPath = mdiUpdate
    const runningPath = mdiCached
    const finishedPath = mdiCheck
    const errorPath = mdiClose
    const timerStatus = ref<'waiting' | 'running' | 'finished' | 'error'>((props.defaultTime !== null && props.defaultTime !== undefined) ? 'finished' : 'waiting')
    const startAt = ref(0)
    const now = ref(0)
    let off = () => {}
    let rafId: number | null = null
    const display = computed(() => {
        const ms = now.value - startAt.value          //ms
        if (ms < 100) return `${ms.toFixed(1)}ms`                // < 100 ms
        const s = ms / 1000
        if (s < 60) return `${s.toFixed(1)}s`                    // < 1 min
        const m = Math.floor(s / 60)
        const sec = s - 60 * m
        const displaySec = String(sec.toFixed(1)).padStart(4, '0') + 's'
        return `${m}m ${displaySec === '00.0s' ? '' : displaySec}`
    })


    const tick = () => {
        now.value = performance.now()
        rafId = requestAnimationFrame(tick)
    }
    const startCount = () => {
        stopCount()
        startAt.value = performance.now()
        now.value = startAt.value
        tick()
    }
    const stopCount = () => {
        if (rafId) {
            cancelAnimationFrame(rafId)
            rafId = null
        }
    }
    const timerMsgHandler = (msg: {action: 'start'|'stop'|'error'; nodeId: string}) => {
        if(msg.nodeId !== props.nodeId) return
        msg.action === 'start' ? startCount() : stopCount()
        timerStatus.value = msg.action === 'start' ? 'running' : msg.action === 'stop' ? 'finished' : 'error'
    }


    onMounted(() => {
        if(props.defaultTime) {
            const offsetMs = props.defaultTime
            const tmp = performance.now()
            startAt.value = tmp
            now.value     = tmp + offsetMs
        }
        off = onTimerMsg(timerMsgHandler)
    })
    onUnmounted(() => {
        off()
        stopCount()
    })

</script>

<style lang="scss" scoped>
    @use './tools.scss' as *;
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;

    @keyframes spin {
        from {
            transform: rotate(360deg);
        }
        to {
            transform: rotate(0deg);
        }
    }

    .timer {
        display: flex;
        align-items: center;
        font-size: 13px;
        position: absolute;
        white-space: nowrap;
        pointer-events: none;
        top: 0;
        left: 7px;
        transform: translate(0, -120%);
        color: rgba(0, 0, 0, 0.3);
        font-weight: bold;
        .running {
            animation: spin 1s linear infinite;
        }
        svg {
            margin-right: 4px;
            width: 18px;
            height: 18px;
        }
    }
</style>
