<template>
    <span class="timer">
        <svg-icon type="mdi" :path="timerPath"></svg-icon>{{ display }}
    </span>
</template>

<script lang="ts" setup>
    import { ref, computed, onMounted, onUnmounted } from 'vue'
    import { onTimerMsg } from '@/utils/task'   //@ts-ignore
    import SvgIcon from '@jamescoyle/vue-icon'
    import { mdiTimerOutline } from '@mdi/js'
    import { mdiUpdate } from '@mdi/js'; // waiting
    import { mdiCached } from '@mdi/js'; // running
    import { mdiCheckCircleOutline } from '@mdi/js'; // finished

    const props = defineProps<{
        nodeId: string,
        defaultTime?: number | null
    }>()
    const timerPath = mdiTimerOutline
    const startAt = ref(0)
    const now = ref(0)
    let off = () => {}
    let rafId: number | null = null
    const display = computed(() => {
        const ms = now.value - startAt.value          //ms
        if (ms < 100) return `${ms.toFixed(1)}ms`                // < 100 ms
        const s = ms / 1000
        if (s < 60) return `${s.toFixed(1)}s`                    // < 1 min
        const m = Math.floor(Math.floor(s) / 60)
        const sec = Math.floor(s) % 60
        return `${m}:${String(sec).padStart(2, '0')}`
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
    const timerMsgHandler = (msg: {action: 'start'|'stop'; nodeId: string}) => {
        if(msg.nodeId !== props.nodeId) return
        msg.action === 'start' ? startCount() : stopCount()
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
    .timer {
        display: flex;
        align-items: flex-end;
        font-size: 13px;
        position: absolute;
        white-space: nowrap;
        pointer-events: none;
        top: 0;
        left: 0;
        transform: translate(0, -95%);
    }
</style>
