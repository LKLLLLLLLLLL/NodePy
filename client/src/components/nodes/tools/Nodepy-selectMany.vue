<template>
    <div
        class="NodePySelectManyLayout"
        ref="root"
        @click.stop
        :class="{open}"
    >
        <div class="value" :class="{close: !open}" @click.stop="toggle" :style="{height: itemHeight, width: itemWidth}">
            <span class="selectedItem" :class="{'_no_specified_col' : selectedItem === '_no_specified_col'}">{{ selectedItem === '_no_specified_col' ? '不指定列名' : selectedItem }}</span>
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
                :class="[{selected: selectedIdx === idx && options[selectedIdx]}, {'_no_specified_col' : item === '_no_specified_col'}]"
            >   <!-- options[selectedIdx] means empty value cannot be accepted-->
                <span>{{ item === '_no_specified_col' ? '不指定列名' : item}}</span>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref, computed, watchEffect, onBeforeUnmount, watch} from 'vue'
    import type { PropType } from 'vue'
    // @ts-ignore
    import SvgIcon from '@jamescoyle/vue-icon'
    import { mdiMenuDown } from '@mdi/js'

    const down_path = mdiMenuDown

    const props = defineProps({
        options: {
            type: Array as PropType<string[]>,
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
        height: `calc(${props.itemHeight} - 2px)`  //-2 for the gap between items
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
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            .selectedItem {
                flex: 1;
                padding: 0 17px;
                text-align: center;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                &._no_specified_col {
                    color: rgba(0, 0, 0, 0.2);
                    font-style: italic;
                    font-size: 12px;
                }
            }
            .arrow {
                position: absolute;
                right: 1px;
                display: flex;
                align-items: center;
                color: rgba(0,0,0,0.4);
                svg {
                    width: 18px;
                }
            }
            .arrow.open {
                transform: rotate(180deg);
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
                display: flex;
                align-items: center;
                justify-content: center;
                &._no_specified_col {
                    color: rgba(0, 0, 0, 0.2);
                    font-style: italic;
                    font-size: 11px;
                }
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
