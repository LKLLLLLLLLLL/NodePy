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
                :class="{ticked: model}"
                x="3"
                y="3"
                width="20" 
                height="20" 
                rx="5" 
                :fill="model ? '#108efe' : '#ddd'"
            />
            <path
                class="tick"
                d="M8 13l3 3 7-7"
                fill="none"
                :stroke="tickColor"
                stroke-width="2"
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
            default: 'white'
        },
    })
    const emit = defineEmits(['updateValue'])

    
    const toggle = () => {
        model.value = !model.value
        emit('updateValue')
    }

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    .NodePyBoolValueLayout {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        user-select: none;
        background: white;
        font-size: $node-description-fontsize;
        .box {
            cursor: pointer;
        }
        .box:hover {
            .rect {
                fill: #ccc;
            }
            .rect.ticked {
                fill: #0d73cd
            }
        }
        &.has-label { 
            gap: 6px;
        }
    }
</style>