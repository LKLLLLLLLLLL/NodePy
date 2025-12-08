<template>
    <div
        class="NodePySelectManyLayout"
        ref="root"
        @click.stop
        :class="{open}"
    >
        <div class="value" :class="{close: !open}" @click.stop="toggle" :style="{height: itemHeight, width: itemWidth}">
            <span class="selectedItem" :class="{'specialColumn' : isSpecialColumn(selectedItem)}">{{columnValue(selectedItem)}}</span>
            <span class="arrow" :class="{open}">
              <SvgIcon type="mdi" :path="down_path"  />
            </span>
        </div>

        <div v-if="open" class="options" @click.stop>
            <div
                v-for="(item, idx) in localOptions"
                :key="item"
                class="item"
                @click.stop="select(idx)"
                :style="itemStyle"
                :class="[{selected: selectedIdx === idx && localOptions[selectedIdx]}, {'specialColumn' : isSpecialColumn(item)}]"
            >   <!-- localOptions[selectedIdx] means empty value cannot be accepted-->
                <span>{{columnValue(item)}}</span>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import type { PropType } from 'vue'
import { computed, onBeforeUnmount, ref, watch, watchEffect } from 'vue'
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
    const localOptions = ref(props.options)
    const root = ref<HTMLElement>()
    const itemStyle = ref({
        width: props.itemWidth,
        height: `calc(${props.itemHeight} - 2px)`  //-2 for the gap between items
    })
    const selectedIdx = ref(props.defaultSelected)
    const open = ref(false)
    const selectedItem = computed(() => selectedIdx.value >= 0 ? localOptions.value[selectedIdx.value] : '')


    const select = (idx: number) => {
        open.value = false
        if(JSON.stringify(props.options) !== JSON.stringify(localOptions.value)) {
            return
        }   // if props.options !== localOptions.value, which means dirty data, just return and display the local cache and wait for next update
        if(!localOptions.value[idx])return
        selectedIdx.value = idx
        emit('selectChange', idx)
    }

    const toggle = () => {
        open.value = !open.value
    }

    const clickOutside = (e: MouseEvent) => {
        if (!root.value!.contains(e.target as Node)) open.value = false
    }

    const isSpecialColumn = (item: string | undefined | null) => {
        switch(item) {
            case '_no_specified_col':
            case '_index':
                return true
            default:
                return false
        }
    }

    const columnValue = (item: string | undefined | null) => {
        switch(item) {
            case '_no_specified_col':
                return '不指定列名'
            case '_index':
                return '行号'
            default:
                return item
        }
    }


    watchEffect(() => open.value
        ? document.addEventListener('click', clickOutside, true)
        : document.removeEventListener('click', clickOutside, true)
    )

    watch(() => JSON.stringify(props.options), async (newValue, oldValue) => {
        if(JSON.stringify(props.options) === JSON.stringify(['']) || (JSON.stringify(props.options) === JSON.stringify(localOptions.value))) {
            return
        } // if props.options is empty, which means the hint is empty, save the local cache and do not clear
        await new Promise(resolve => {
            emit('clearSelect', resolve)    //  if options have changed, the selection should be cleared
        })
        localOptions.value = props.options
        selectedIdx.value = props.defaultSelected
    }, {immediate: false})

    onBeforeUnmount(() => document.removeEventListener('click', clickOutside, true))

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    @use './tools.scss' as *;

    .NodePySelectManyLayout {
        position: relative;
        font-size: $node-description-fontsize;
        .value {
            @include tool-item-style;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            .selectedItem {
                padding: 0 17px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                &.specialColumn {
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
                    transition: transform 0.2s;
                }
            }
            .arrow.open {
                transform: rotate(180deg);
            }
        }
        .value:hover {
            @include tool-item-style-hover;
        }
        .options {
            position: absolute;
            top: calc(100% + 2px);
            left: 0;
            right: 0;
            z-index: 100;
            background: white;
            border-radius: 6px;
            box-shadow: 2px 2px 20px rgba(128, 128, 128, 0.3);
            display: flex;
            flex-direction: column;
            gap: 2px;
            padding: 2px 2px;
            cursor: pointer;
            max-height: 200px;
            overflow-y: auto;
            &::-webkit-scrollbar {
                width: 4px;
            }
            &::-webkit-scrollbar-thumb {
                background: #ccc;
                border-radius: 2px;
            }
            .item {
                @include tool-item-style;
                padding: 1px 5px;
                border-radius: 6px;
                font-size: 13px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: transparent;
                span {
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                &.specialColumn {
                    color: rgba(0, 0, 0, 0.2);
                    font-style: italic;
                    font-size: 11px;
                }
            }
            .item:hover {
                background: #eee;
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
