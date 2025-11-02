<template>
    <div class="NodePySelectFewLayout nodes-innertool-border-radius">
        <div 
            class="item" 
            :class="{selected: selectedIdx.includes(index)}" 
            :style="{width: itemWidth, height: itemHeight}" 
            @click="onClick(index)"
            v-for="(item, index) in options"
        >
            {{ item }}
        </div>
    </div>
</template>

<script lang="ts" setup>
    import {ref, type PropType} from 'vue'
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
            default: '100%'
        },
        selectMaxNum: {
            type: Number,
            default: 1
        },
        defualtSelected: {
            type: Array as PropType<number[]>,
            required: false
        },
        acceptEmpty: {
            type: Boolean,
            default: false
        }
    })
    const emit = defineEmits(['selectChange'])
    const selectedIdx = ref<number[]>(props.defualtSelected || [])


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
        emit('selectChange', selectedIdx)
    }

</script>

<style lang="scss" scoped>
    @use '../../../common/global.scss';
    @use '../../../common/node.scss';
    .NodePySelectFewLayout {
        display: inline-flex;
        border: 1.5px solid #ccc;
        overflow: hidden;
        .item {
            text-align: center;
            padding: 0 5px;
            background: #fff;
        }
        .item:hover:not(.selected) {
            background: #ccc;
        }
        .item:hover.selected {
            background: #999;
        }
        .selected {
            background: #aaa;
        }
    }

</style>