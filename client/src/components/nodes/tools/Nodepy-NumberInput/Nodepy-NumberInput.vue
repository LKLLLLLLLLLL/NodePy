<template>
    <div 
        class="NodepyNumberInputLayout nodes-innertool-border-radius" 
        :style="{width: width, height: height}" 
        @click.stop
    >
        <div class="left-arrow" @click="onClick(-1)">
            <span>
                <svg width="10" height="12" viewBox="0 0 8 8">
                    <path d="M6 1 L2 4 L6 7" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </span>
        </div>
        <div v-if="!isEditing" class="value" @pointerdown="handlePointerDown" @click="handleValueClick">
            <span>{{ (model ?? 0).toFixed(local.fixed) }}</span>
        </div>
        <div class="value-input" v-else>
            <input 
            ref="inputEl" 
            v-model="editText" 
            @blur="commitEdit" 
            @keydown.enter="commitEdit" 
            @keydown.esc="cancelEdit" 
            type="text"
            />
        </div>
        <div class="right-arrow" @click="onClick(1)">
            <span>
                <svg width="10" height="12" viewBox="0 0 8 8">
                    <path d="M2 1 L6 4 L2 7" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </span>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {computed, ref, nextTick} from 'vue'
    import { usePointerLock } from './usePointerLock'
    import type { NumberFieldProps } from './NumberFieldProps'

    const props = withDefaults(defineProps<NumberFieldProps>(), {
        denominator: 1,
        scale: 0,
        width: '100%',
        height: '100%'
    })
    const emit = defineEmits(['updateValue'])
    const model = defineModel<number>()
    const local =  computed(() => {
        return {
            denominator: props.denominator,
            fixed: props.scale ?? Math.max(Math.ceil(Math.log10(props.denominator)), 0)
        }
    })
    const isEditing = ref(false)
    const editText = ref('')
    const inputEl = ref<HTMLInputElement>()


    const onClick = (n: number) => {
        update(n)
        emit('updateValue')
    }

    const normalize = (number: number, denominator: number) => {
      const frac = denominator / 1
      return Math.ceil(frac * number) / frac
    }

    const update = (relative: number) => {
      if (model.value === undefined) return
    
      const step = 1 / local.value.denominator;
      const newValue = normalize(model.value + (relative * step), local.value.denominator)
      const min = props.min ?? Number.NEGATIVE_INFINITY
      const max = props.max ?? Number.POSITIVE_INFINITY
      model.value = Math.min(Math.max(newValue, min), max)
    }

    const { requestLock, hasDragged } = usePointerLock({
      onMove: relative => update(relative.x),
      onDragEnd: () => {emit('updateValue')}
    })

    const handlePointerDown = (e: PointerEvent) => {
      requestLock(e.currentTarget as HTMLElement)
    }

    const handleValueClick = () => {
        if(!hasDragged.value) {
            startEdit()
        }
        hasDragged.value = false
    }

    const startEdit = () => {
        editText.value = (model.value ?? 0).toFixed(local.value.fixed)
        isEditing.value = true
        nextTick(() => inputEl.value?.focus())
    }

    const cancelEdit = () => {
        isEditing.value = false
    }

    const commitEdit = () => {
        const n = Number(editText.value)
        if(Number.isFinite(n)) {
            const min = props.min ?? Number.NEGATIVE_INFINITY
            const max = props.max ?? Number.POSITIVE_INFINITY
            model.value = Math.min(Math.max(normalize(n, local.value.denominator), min), max)
        }
        isEditing.value = false
        emit('updateValue')
    }

</script>

<style lang="scss" scoped>
    @use '../../../../common/global.scss';
    @use '../../../../common/node.scss';
    .NodepyNumberInputLayout {
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
        border: 1.5px solid #ccc;
        .left-arrow {
            width: 20px;
            background: #ddd;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .left-arrow:hover {
            background: #ccc;
        }
        .value {
            width: 100%;
            text-align: center;
        }
        .value-input {
            width: 100%;
            input {
                width: 100%;
                text-align: center;
                outline: none;
            }
        }
        .right-arrow {
            width: 20px;
            background: #ddd;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .right-arrow:hover {
            background: #ccc;
        }
    }
</style>