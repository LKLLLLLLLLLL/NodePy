<template>
    <div
        class="NodePyMultiSelectManyLayout"
        ref="root"
        @click.stop
    >
        <div class="tags-container">
            <div
                v-for="(idx) in selectedIdx"
                :key="idx"
                class="tag"
                :class="{'specialColumn' : isSpecialColumn(options[idx])}"
            >
                <span class="tag-text">{{ columnValue(options[idx]) }}</span>
                <span class="tag-close" @click.stop="remove(idx)">
                    <SvgIcon type="mdi" :path="close_path" size="12" />
                </span>
            </div>

            <div class="add-btn" @click.stop="toggle" :class="{active: open}">
                <SvgIcon type="mdi" :path="plus_path" size="16" />
                <span v-if="selectedIdx.length === 0">添加选项</span>
            </div>
        </div>

        <div v-if="open" class="options" @click.stop>
            <div
                v-for="(item, idx) in options"
                :key="item"
                class="item"
                @click.stop="select(idx)"
                :class="[{selected: selectedIdx.includes(idx) && options[idx]}, {'specialColumn' : isSpecialColumn(item)}]"
            >   <!-- options[idx] means empty value cannot be accepted-->
                <span class="text">{{columnValue(item)}}</span>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
    import type { PropType } from 'vue'
import { computed, onBeforeUnmount, ref, watch, watchEffect } from 'vue'
    // @ts-ignore
    import SvgIcon from '@jamescoyle/vue-icon'
import { mdiClose, mdiMenuDown, mdiPlus } from '@mdi/js'

    const down_path = mdiMenuDown
    const close_path = mdiClose
    const plus_path = mdiPlus

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
            type: Array as PropType<number[]>,
            default: () => []
        },
        clearToggle: {
            type: Boolean,
            default: false
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
    const selectedItem = computed(() => selectedIdx.value.map(idx => props.options[idx]).filter(Boolean))


    const select = (idx: number) => {
        if(!props.options[idx])return
        const id = selectedIdx.value.indexOf(idx)
        if(id !== -1) {
            selectedIdx.value.splice(id, 1)
        }else {
            selectedIdx.value.push(idx)
        }
        emit('selectChange', selectedIdx.value)
    }
    const remove = (idx: number) => {
        const id = selectedIdx.value.indexOf(idx)
        if(id !== -1) {
            selectedIdx.value.splice(id, 1)
            emit('selectChange', selectedIdx.value)
        }
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
    watch([() => JSON.stringify(props.options), () => props.clearToggle], async (newValue, oldValue) => {
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
    $tag-fontsize: 13px;
    .NodePyMultiSelectManyLayout {
        position: relative;
        font-size: $node-description-fontsize;
        width: 100%;
        .tags-container {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            min-height: 25px;
            .tag {
                @include tool-item-style;
                display: flex;
                align-items: center;
                border-radius: 6px;
                padding: 2px 8px;
                font-size: $tag-fontsize;
                max-width: 100%;

                &.specialColumn {
                    font-style: italic;
                    color: rgba(0, 0, 0, 0.5);
                }

                .tag-text {
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    margin-right: 4px;
                }

                .tag-close {
                    display: flex;
                    align-items: center;
                    cursor: pointer;
                    opacity: 0.6;
                    &:hover {
                        opacity: 1;
                    }
                }
            }

            .add-btn {
                @include tool-item-style;
                border-radius: 6px;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 2px 8px;
                cursor: pointer;
                color: #666;
                transition: all 0.2s;
                height: 26px;

                &:hover, &.active {
                    background-color: #ddd;
                    color: $stress-color;
                }

                span {
                    margin-left: 4px;
                    font-size: $tag-fontsize;
                }
            }
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
            flex-direction: row;
            flex-wrap: wrap;
            gap: 4px;
            padding: 6px 6px;
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
                width: auto;
                max-width: 100%;
                padding: 2px 8px;
                border-radius: 6px;
                font-size: $tag-fontsize;
                display: flex;
                align-items: center;
                justify-content: center;
                .text {
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }

                &.specialColumn {
                    color: rgba(0, 0, 0, 0.4);
                    font-style: italic;
                }
            }
            .item:hover {
                @include tool-item-style-hover;
                width: auto;
                max-width: 100%;
                padding: 2px 8px;
                border-radius: 6px;
                font-size: $tag-fontsize;
                display: flex;
                align-items: center;
                justify-content: center;
                .text {
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
            }
            .item.selected {
                background-color: $stress-color;
                color: white;
                // font-weight: 600;
            }
            .item:hover.selected {
                background-color: $hover-stress-color;
            }
        }
    }
</style>
