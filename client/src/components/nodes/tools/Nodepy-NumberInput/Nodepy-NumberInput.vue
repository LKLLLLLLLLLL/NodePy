<template>
    <div
        class="NodepyNumberInputLayout nodes-innertool-border-radius"
        :style="{width: width, height: height}"
        @click.stop
        :class="{disabled}"
    >
        <div class="left-arrow" @click="onClick(-1)" :class="{disabled}">
            <SvgIcon type="mdi" :path="mdi_left_path"  />
        </div>
        <div v-if="!isEditing" class="value" @mousedown="handleLeftMouseDown" :class="[{disabled}, {'empty-value' : model == null}]">
            <span>{{ model == null ? '空' : (model ?? 0).toFixed(local.fixed) }}</span>
        </div>
        <div class="value-input" v-else :class="{disabled}">
            <input
            ref="inputEl"
            v-model="editText"
            @blur="commitEdit"
            @keydown.enter="commitEdit"
            @keydown.esc="cancelEdit"
            type="text"
            />
        </div>
        <div class="right-arrow" @click="onClick(1)" :class="{disabled}">
            <SvgIcon type="mdi" :path="mdi_right_path"  />
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {computed, ref, nextTick} from 'vue'
    import { usePointerLock } from './usePointerLock'
    import type { NumberFieldProps } from './NumberFieldProps'
    // @ts-ignore
    import SvgIcon from '@jamescoyle/vue-icon';
    import { mdiMenuLeft, mdiMenuRight } from '@mdi/js';

    const mdi_left_path = mdiMenuLeft;
    const mdi_right_path = mdiMenuRight;

    const props = withDefaults(defineProps<NumberFieldProps>(), {
        denominator: 1,
        width: '100%',
        height: 'auto',
        disabled: false
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
        if (model.value == null) return
        const newValue = model.value + n
        const min = props.min ?? Number.NEGATIVE_INFINITY
        const max = props.max ?? Number.POSITIVE_INFINITY
        model.value = Math.min(Math.max(newValue, min), max)
        emit('updateValue')
    }

    const normalize = (number: number, denominator: number) => {
      const frac = denominator / 1
      return Math.floor(frac * number) / frac
    }

    const update = (relative: number, acceleration: number = 1) => {
      if (model.value == null) return

      const step = 1 / local.value.denominator
      const effectiveMovement = relative * acceleration
      const newValue = normalize(model.value + (effectiveMovement * step), local.value.denominator)
      const min = props.min ?? Number.NEGATIVE_INFINITY
      const max = props.max ?? Number.POSITIVE_INFINITY
      model.value = Math.min(Math.max(newValue, min), max)
    }

    const { requestLock } = usePointerLock({
      onMove: (relative, acceleration) => update(relative.x, acceleration),
      onDragEnd: () => {emit('updateValue')},
      denominator: props.denominator
    })

    const handleLeftMouseDown = (e: MouseEvent) => {
        if(e.button === 0){
            const element = e.currentTarget as HTMLElement
            const startX = e.clientX
            const startY = e.clientY
            let hasMoved = false

            const onMouseMove = (moveEvent: MouseEvent) => {
                const deltaX = Math.abs(moveEvent.clientX - startX)
                const deltaY = Math.abs(moveEvent.clientY - startY)
                if(!hasMoved && (deltaX > 3 || deltaY > 3)) {
                    hasMoved = true
                    requestLock(element)
                }
            }

            const onMouseUp = () => {
                document.removeEventListener('mousemove', onMouseMove)
                document.removeEventListener('mouseup', onMouseUp)
                if(!hasMoved) {
                    startEdit()
                }
            }

            document.addEventListener('mousemove', onMouseMove)
            document.addEventListener('mouseup', onMouseUp)
        }
    }

    const startEdit = () => {
        editText.value = model.value == null ? '' : (model.value ?? 0).toFixed(local.value.fixed)
        isEditing.value = true
        nextTick(() => inputEl.value?.focus())
    }

    const cancelEdit = () => {
        isEditing.value = false
    }

    const commitEdit = () => {
        if(!isEditing.value) return
        const n = Number(editText.value)
        if(editText.value.trim() === '') {
            model.value = undefined
        }else if(Number.isFinite(n)) {
            const min = props.min ?? Number.NEGATIVE_INFINITY
            const max = props.max ?? Number.POSITIVE_INFINITY
            model.value = Math.min(Math.max(normalize(n, local.value.denominator), min), max)
        }
        isEditing.value = false
        emit('updateValue')
    }

</script>

<style lang="scss" scoped>
    @use '../../../../common/global.scss' as *;
    @use '../../../../common/node.scss' as *;
    @use '../tools.scss' as *;
    .NodepyNumberInputLayout {
        @include box-tools-style;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
        font-size: $node-description-fontsize;
        &.disabled {
            cursor: not-allowed;
        }
        .left-arrow {
            width: 20px;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            color: rgba(0,0,0,0.4);
            border-radius: 5px;
            margin-left: 2px;
            &.disabled {
                color: rgba(0, 0, 0, 0.3);
                pointer-events: none;
            }
        }
        .left-arrow:hover {
            background: #ddd;
        }
        .value {
            @include tool-item-style;
            padding: 2px 5px;
            flex-grow: 1;
            flex-basis: 0%;
            text-align: center;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            cursor: ew-resize;
            &.disabled {
                color: rgba(0, 0, 0, 0.3);
                pointer-events: none;
            }
            &.empty-value {
                color: rgba(0, 0, 0, 0.2);
                font-style: italic;
            }
        }
        .value-input {
            @include tool-item-style;
            width: 100%;
            padding: 2px 5px;
            input {
                width: 100%;
                text-align: center;
                outline: none;
            }
            &.disabled {
                color: rgba(0, 0, 0, 0.3);
                pointer-events: none;
            }
        }
        .right-arrow {
            width: 20px;;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            color: rgba(0,0,0,0.4);
            border-radius: 5px;
            margin-right: 2px;
            &.disabled {
                color: rgba(0, 0, 0, 0.3);
                pointer-events: none;
            }
        }
        .right-arrow:hover {
            background: #ddd;
        }
    }
</style>
