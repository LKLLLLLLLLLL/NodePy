<template>
    <span
        class="NodePyBoolValueLayout"
        role="checkbox"
        :aria-checked="model"
        tabindex="0"
        @click.stop="toggle"
        @keydown.space.prevent="toggle"
        :style="{width: width, height: height}"
    >
        <svg class="box" viewBox="0 0 24 24">
            <rect x="2" y="2" width="20" height="20" rx="3" :stroke="borderColor" fill="white" stroke-width="2"/>
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

        <span class="label"><slot/></span>
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
            default: '#aaa'
        },
        borderColor: {
            type: String,
            default: '#ccc'
        }
    })
    const emit = defineEmits(['updateValue'])

    
    const toggle = () => {
        model.value = !model.value
        emit('updateValue')
    }

</script>

<style lang="scss" scoped>
    .NodePyBoolValueLayout{ 
        display: inline-flex;
        align-items: center;
        cursor: pointer;
        user-select: none;
        gap: 6px;
        .box {
            height: 100%;
            width: 100%;
            .tick{
                transition: opacity .2s ease;
            }
        }
    }
</style>