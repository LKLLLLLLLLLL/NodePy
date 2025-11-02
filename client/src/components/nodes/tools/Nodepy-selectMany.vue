<template>
    <div 
        class="NodePySelectManyLayout" 
        ref="root" 
        :style="{height: height, width: width}"
    >
        <div class="value" :class="{close: !open}" @click="toggle">
            {{ selectedItem }}
            <span class="arrow" :class="{open}">
                <svg width="10" height="12" viewBox="0 0 8 8">
                    <path d="M1 2 L4 6 L7 2" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </span>
        </div>

        <div v-if="open" class="options" :style="optionStyle" @click.stop>
            <div 
                v-for="(item, idx) in options"
                class="item"
                @click="select(idx)"
            >
                {{ item }}
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref, computed, watchEffect, onBeforeUnmount} from 'vue'


    const props = defineProps({
        options: {
            type: Array,
            required: true
        },
        width: {
            type: String,
            default: '100%'
        },
        height: {
            type: String,
            default: '100%'
        },
        defaultSelected: {
            type: Number,
            default: 1
        }
    })
    const emit = defineEmits(['selectChange'])
    const root = ref<HTMLElement>()
    const optionStyle = ref({})
    const selectedIdx = ref(props.defaultSelected)
    const open = ref(false)
    const selectedItem = computed(() => props.options[selectedIdx.value])


    const select = (idx: number) => {
        selectedIdx.value = idx
        emit('selectChange', idx)
        open.value = false
    }

    const toggle = () => {
        open.value = !open.value
    }

    const clickOutside = (e: MouseEvent) => {
        if (!root.value!.contains(e.target as Node)) open.value = false
    }


    watchEffect(() => open.value
        ? document.addEventListener('click', clickOutside, true)
        : document.removeEventListener('click', clickOutside, true)
    )

    onBeforeUnmount(() => document.removeEventListener('click', clickOutside, true))

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss';
    @use '../../../common/node.scss';
    .NodePySelectManyLayout {
        position: relative;
        .value {
            border-radius: 6px 6px 0 0;
            padding: 2px 0 2px 10px;
            background: #ddd;
            .arrow {
                position: absolute;
                right: 5px;
            }
            .arrow.open {
                transform: rotate(180deg); 
            }
        }
        .value.close {
            border-radius: 6px 6px 6px 6px;
        }
        .value:hover {
            background: #ccc;
        }
        .options {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            z-index: 10;
            .item {
                padding: 2px 0 2px 10px;
                background: #ddd;
            }
            .item:hover {
                background: #ccc;
            }
            .item:last-child {
                border-radius: 0 0 6px 6px;
            }
        }
    }
</style>