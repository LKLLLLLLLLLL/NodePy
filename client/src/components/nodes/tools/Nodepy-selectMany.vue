<template>
    <div
        class="NodePySelectManyLayout"
        ref="root"
        @click.stop
        :class="{open}"
    >
        <div class="value" :class="{close: !open}" @click.stop="toggle" :style="{height: itemHeight, width: itemWidth}">
            {{ selectedItem }}
            <span class="arrow" :class="{open}">
              <SvgIcon type="mdi" :path="down_path"  />
            </span>
        </div>

        <div v-if="open" class="options" @click.stop>
            <div
                v-for="(item, idx) in options"
                class="item"
                @click.stop="select(idx)"
                :style="itemStyle"
                :class="{selected: selectedIdx === idx && options[selectedIdx]}"
            >   <!-- options[selectedIdx] means empty value cannot be accepted-->
                {{ item }}
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref, computed, watchEffect, onBeforeUnmount, watch} from 'vue'
    // @ts-ignore
    import SvgIcon from '@jamescoyle/vue-icon'
    import { mdiMenuDown } from '@mdi/js'

    const down_path = mdiMenuDown;

    const props = defineProps({
        options: {
            type: Array,
            required: true
        },
        itemWidth: {
            type: String,
            default: '100%'
        },
        itemHeight: {
            type: String,
            default: '25px'
        },
        defaultSelected: {
            type: Number,
            default: 0
        }
    })
    const emit = defineEmits(['selectChange', 'clearSelect'])
    const root = ref<HTMLElement>()
    const itemStyle = ref({
        width: props.itemWidth,
        height: `calc(${props.itemHeight} - 2px)`  //-4 for the gap between items
    })
    const selectedIdx = ref(props.defaultSelected)
    const open = ref(false)
    const selectedItem = computed(() => selectedIdx.value >= 0 ? props.options[selectedIdx.value] : '')


    const select = (idx: number) => {
        open.value = false
        if(!props.options[idx])return
        selectedIdx.value = idx
        emit('selectChange', idx)
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

    watch(() => JSON.stringify(props.options), async (newValue, oldValue) => {
        await new Promise(resolve => {
            emit('clearSelect', resolve)    //  if options have changed, the selection should be cleared
        })
        selectedIdx.value = props.defaultSelected
    }, {immediate: false})

    onBeforeUnmount(() => document.removeEventListener('click', clickOutside, true))

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    @use './tools.scss' as *;
    .NodePySelectManyLayout.open {
        border-radius: 6px 6px 0 0;
    }
    .NodePySelectManyLayout {
        @include box-tools-style;
        position: relative;
        font-size: $node-description-fontsize;
        .value {
            @include tool-item-style;
            border-radius: 6px 6px 0 0;
            .arrow {
                position: absolute;
                right: 5px;
                top: 50%;
                transform: translateY(-50%);     /* 垂直居中显示 */
                display: flex;
                align-items: center;
                color: rgba(0,0,0,0.4);
                svg {
                    width: 18px;
                }
            }
            .arrow.open {
                transform: translateY(-50%) rotate(180deg);
            }
        }
        .value.close {
            border-radius: 6px;
        }
        .value:hover {
            @include tool-item-style-hover;
        }
        .options {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            z-index: 10;
            background: #eee;
            border-radius: 0 0 6px 6px;
            display: flex;
            flex-direction: column;
            gap: 2px;
            padding: 2px 2px;
            cursor: pointer;
            .item {
                @include tool-item-style;
                padding: 1px 5px;
                border-radius: 6px;
                font-size: 13px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .item:hover {
                background: #ddd;
            }
            .item.selected {
                background: $stress-color;
                color: white;
            }
            .item:hover.selected {
                background: $hover-stress-color;
                color: white;
            }
        }
    }
</style>
