<template>
    <div class="NodepyNumberInputLayout">
        <div class="left-arrow">
            <button @click="update(-1)" @pointerdown="handlePointerDown" type="button">
                <span>◀</span>
            </button>
        </div>
        <div class="value" @pointerdown="handlePointerDown">
            <span>{{ (model ?? 0).toFixed(local.fixed) }}</span>
        </div>
        <div class="right-arrow">
            <button @click="update(1)" @pointerdown="handlePointerDown" type="button">
                <span>▶</span>
            </button>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {computed} from 'vue'
    import { usePointerLock } from './usePointerLock';
    import type { NumberFieldProps } from './NumberFieldProps';

    const props = withDefaults(defineProps<NumberFieldProps>(), {
        denominator: 1,
        scale: 2,
    })

    const model = defineModel<number>()

    const local =  computed(() => {
        return {
            denominator: props.denominator,
            fixed: props.scale ?? Math.max(Math.ceil(Math.log10(props.denominator)), 0)
        }
    })


    function normalize(number: number, denominator: number) {
      const frac = denominator / 1;
      return Math.ceil(frac * number) / frac;
    }

    function update(relative: number) {
      if (model.value === undefined) return;
    
      const step = 1 / local.value.denominator;
      const newValue = normalize(model.value + (relative * step), local.value.denominator);
      const min = props.min ?? Number.NEGATIVE_INFINITY;
      const max = props.max ?? Number.POSITIVE_INFINITY;
      model.value = Math.min(Math.max(newValue, min), max);
    }


    const { requestLock } = usePointerLock({
      onMove: relative => update(relative.x)
    });

    function handlePointerDown(e: PointerEvent) {
      requestLock(e.currentTarget as HTMLElement);
    }
</script>

<style lang="scss" scoped>
    @use '../../../common/style/global.scss';
    .NodepyNumberInputLayout {
        width: 100%;
        padding: 0 10px;
        display: flex;
        justify-content: center;
        align-items: center;
        .value {
            width: 100%;
            text-align: center;
        }
    }
</style>