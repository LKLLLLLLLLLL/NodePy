<template>
  <div
    v-if="active"
    class="spinner"
    :style="{'--size': sizePx, '--color': color}"
    role="status"
    :aria-label="ariaLabel"
    aria-live="polite"
  >
    <svg
      :width="s"
      :height="s"
      :viewBox="`0 0 ${s} ${s}`"
      class="spinner-svg"
      focusable="false"
      aria-hidden="true"
    >
      <!-- background track -->
      <circle
        :cx="c"
        :cy="c"
        :r="r"
        :stroke-width="thickness"
        class="spinner-track"
        fill="none"
      />
      <!-- animated arc -->
      <circle
        :cx="c"
        :cy="c"
        :r="r"
        :stroke-width="thickness"
        class="spinner-head"
        fill="none"
        :style="{
          stroke: color,
          strokeDasharray: `${dashArray} ${dashRemainder}`,
          strokeDashoffset: dashOffset + 'px'
        }"
      />
    </svg>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';

const props = defineProps({
  size: { type: [Number, String], default: 40 },         // px or number
  thickness: { type: Number, default: 4 },               // stroke-width in px
  color: { type: String, default: undefined },           // if not provided, use global --stress-color
  active: { type: Boolean, default: true },              // show/hide
  ariaLabel: { type: String, default: 'Loading' },
});

const s = computed(() => {
  const n = Number(props.size);
  return isNaN(n) ? 40 : Math.max(8, Math.round(n));
});
const thickness = computed(() => Math.max(1, Math.round(props.thickness)));
const c = computed(() => s.value / 2);
const r = computed(() => Math.max(1, c.value - thickness.value / 2));
const circumference = computed(() => 2 * Math.PI * r.value);

// dash animation helpers
const dashArray = computed(() => Math.round(circumference.value * 0.75));
const dashRemainder = computed(() => Math.round(circumference.value));
const dashOffset = computed(() => 0);

const sizePx = computed(() => (typeof props.size === 'number' ? `${props.size}px` : `${props.size}`));
// If a color prop is provided, use it; otherwise use the runtime CSS variable
// `--stress-color` which is exported from `global.scss`. Fallback to the
// Material blue `#1976d2` if the CSS variable is not defined at runtime.
const color = computed(() => props.color ?? 'var(--stress-color, #1976d2)');
const active = computed(() => props.active);
const ariaLabel = computed(() => props.ariaLabel);

</script>

<style lang="scss" scoped>
@use "../../common/style/global.scss" as *;
.spinner {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: var(--size);
  height: var(--size);
  color: var(--color);
  line-height: 0;
}

/* rotate the whole svg */
.spinner-svg {
  transform-origin: center;
  animation: spinner-rotate 1.4s linear infinite;
}

/* subtle background track */
.spinner-track {
  stroke: rgba(0, 0, 0, 0.08);
}

/* animated arc */
.spinner-head {
  stroke-linecap: round;
  transform-origin: center;
  /* combine a spinning rotation with dash animation */
  animation: spinner-dash 1.4s ease-in-out infinite;
}

/* rotation keyframes */
@keyframes spinner-rotate {
  100% {
    transform: rotate(360deg);
  }
}

/* dash keyframes: emulate Material indeterminate arc */
@keyframes spinner-dash {
  0% {
    stroke-dasharray: 1px, 200px;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 120px, 200px;
    stroke-dashoffset: -30px;
  }
  100% {
    stroke-dasharray: 1px, 200px;
    stroke-dashoffset: -120px;
  }
}

/* smaller screens / inline usage adjustments (optional) */
</style>
