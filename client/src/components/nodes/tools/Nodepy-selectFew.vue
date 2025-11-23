<template>
    <div 
    class="NodePySelectFewLayout 
    nodes-innertool-border-radius" 
    @click.stop
    :style="{width, height}"
    >
        <div
            class="item"
            :class="{selected: selectedIdx.includes(index)}"
            @click.stop="onClick(index)"
            v-for="(item, index) in options"
        >
            {{ item }}
        </div>
    </div>
</template>

<script lang="ts" setup>
    import { ref, type PropType } from 'vue'
    const props = defineProps({
        options: {
            type: Array,
            required: true
        },
        width: {
            type: String,
            default: 'auto'
        },
        height: {
            type: String,
            default: 'auto'
        },
        selectMaxNum: {
            type: Number,
            default: 1
        },
        defaultSelected: {
            type: Array as PropType<number[]>,
            required: false
        },
        acceptEmpty: {
            type: Boolean,
            default: false
        }
    })
    const emit = defineEmits(['selectChange'])
    const selectedIdx = ref<number[]>(props.defaultSelected || [])


    const onClick = (index: number) => {
        const idx = selectedIdx.value.indexOf(index)
        if(idx !== -1) {
            if(!props.acceptEmpty && selectedIdx.value.length <= 1) return
            selectedIdx.value.splice(idx, 1)
        }else if(selectedIdx.value.length < props.selectMaxNum) {
            selectedIdx.value.push(index)
        }else {
            selectedIdx.value.shift()
            selectedIdx.value.push(index)
        }
        emit('selectChange', selectedIdx.value)
    }

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    @use './tools.scss' as *;
    .NodePySelectFewLayout {
      @include box-tools-style;
        display: flex;
        overflow: hidden;
        gap:2px;
        font-size: $node-description-fontsize;
        cursor: pointer;
        .item {
            @include tool-item-style;
            flex: 1;
        }
        .item:hover:not(.selected) {
            @include tool-item-style-hover;
        }
        .item:hover.selected {
            background: $hover-stress-color;
            color: white;
        }
        .selected {
            background: $stress-color;
            color: white;
        }
    }

</style>
