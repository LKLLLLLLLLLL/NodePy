<template>
    <span
        class="NodePyBoolValueLayout"
        :class="{'has-label': $slots.default }"
        role="checkbox"
        :aria-checked="model"
        tabindex="0"
    >
        <span class="label" :style="{lineHeight: height}"><slot/></span>
        <svg 
            class="box nodrag" 
            viewBox="0 0 24 24" 
            :style="{width: width, height: height}" 
            @click.stop="toggle" 
            @keydown.space.prevent="toggle"
        >
            <rect 
                class="rect" 
                x="2" 
                y="2" 
                width="20" 
                height="20" 
                rx="3" 
                :stroke="borderColor" 
                fill="#eee" 
                stroke-width="2"
            />
            <path
                class="tick"
                d="M7 12l3 3 7-7"
                fill="none"
                :stroke="tickColor"
                stroke-width="3"
                stroke-linecap="round"
                stroke-linejoin="round"
                :style="{ opacity: model ? 1 : 0 }"
            />
        </svg>
    </span>
</template>

<script lang="ts" setup>
    const model = defineModel<boolean>()
    const props = defineProps({
        width: {
            type: String,
            default: '100%'
        },
        height: {
            type: String,
            default: '100%'
        },
        tickColor: {
            type: String,
            default: '#999'
        },
        borderColor: {
            type: String,
            default: '#aaa'
        }
    })
    const emit = defineEmits(['updateValue'])

    
    const toggle = () => {
        model.value = !model.value
        emit('updateValue')
    }

</script>

<style lang="scss" scoped>
    .NodePyBoolValueLayout {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        user-select: none;
        background: white;
        .box {
            cursor: pointer;
        }
        .box:hover {
            .rect {
                fill: #ddd;
            }
        }
        &.has-label { 
            gap: 6px;
        }
    }
</style>