<script lang = "ts" setup>
    import { ref } from 'vue';
    import { useModalStore } from '@/stores/modalStore';
    import Result from './results/Result.vue'
    import SearchNode from './menuModals/SearchNode.vue'
    import ManageNode from './menuModals/ManageNode.vue';
    import SelectNode from './menuModals/SelectNode.vue';

    const modalStore = useModalStore();

    //result modal params
    let widthResult = 1000;
    let heightResult = 1200;
    let xResult = 400;
    let yResult = 300;

    //search modal params
    let widthSearch = 400;
    let heightSearch = 600;
    let xSearch = 400;
    let ySearch = 300;

    //select modal params
    let widthSelect = 400;
    let heightSelect = 600;
    let xSelect = 500;
    let ySelect = 350;

    //manage modal params
    let widthManage = 600;
    let heightManage = 800;
    let xManage = 600;
    let yManage = 400;

    function openResult(){
        modalStore.createModal({
            id: 'result-modal',
            title: 'Result',
            content: 'This is the result modal',
            isActive: true,
            isResizable: false,
            isDraggable: true,
            size: { width: widthResult, height: heightResult },
            position: { x: xResult, y: yResult },
            minSize: { width: 200, height: 150 },
            maxSize: { width: 1000, height: 800 },
            component: Result
        })
    }

    function openSearch(){
        modalStore.createModal({
            id: 'search-modal',
            title: 'Search',
            content: 'This is the search modal',
            isActive: true,
            isResizable: false,
            isDraggable: true,
            size: { width: widthSearch, height: heightSearch },
            position: { x: xSearch, y: ySearch },
            minSize: { width: 200, height: 150 },
            maxSize: { width: 1000, height: 800 },
            component: SearchNode
        })
    }

    function openSelect(){
        modalStore.createModal({
            id: 'select-modal',
            title: 'Select',
            content: 'This is the select modal',
            isActive: true,
            isResizable: false,
            isDraggable: true,
            size: { width: widthSelect, height: heightSelect },
            position: { x: xSelect, y: ySelect },
            minSize: { width: 200, height: 150 },
            maxSize: { width: 1000, height: 800 },
            component: SelectNode
        })
    }

    function openManage(){
        modalStore.createModal({
            id: 'manage-modal',
            title: 'Manage',
            content: 'This is the manage modal',
            isActive: true,
            isResizable: false,
            isDraggable: true,
            size: { width: widthManage, height: heightManage },
            position: { x: xManage, y: yManage },
            minSize: { width: 200, height: 150 },
            maxSize: { width: 1000, height: 800 },
            component: ManageNode
        })
    }

    import type { DropdownInstance } from 'element-plus'

    const dropdownRef = ref<DropdownInstance>()
    const position = ref({
        top: 0,
        left: 0,
        bottom: 0,
        right: 0,
    } as DOMRect)

    const triggerRef = ref({
        getBoundingClientRect: () => position.value,
    })

    const handleClick = () => {
        dropdownRef.value?.handleClose()
    }

    const handleContextmenu = (event: MouseEvent) => {
        const { clientX, clientY } = event
        position.value = DOMRect.fromRect({
            x: clientX,
            y: clientY,
    })
    event.preventDefault()
    dropdownRef.value?.handleOpen()
    }

</script>
<template>
    <div class = "control-bar" 
        @click="handleClick"
        @contextmenu="handleContextmenu"
    >
        <el-button
            @click="openResult" 
            :style="{height: '100%'}"
            type="primary"
        >
            唤起结果弹窗
        </el-button>
        <el-dropdown
            ref="dropdownRef"
            :virtual-ref="triggerRef"
            :show-arrow="false"
            :popper-options="{
                modifiers: [{ name: 'offset', options: { offset: [0, 0] } }],
            }"
            virtual-triggering
            trigger="contextmenu"
            placement="bottom-start"
        >
            <template #dropdown>
                <el-dropdown-menu>
                    <el-dropdown-item @click="openSearch">搜索节点</el-dropdown-item>
                    <el-dropdown-item @click="openManage">管理节点</el-dropdown-item>
                    <el-dropdown-item @click="openSelect">选择节点</el-dropdown-item>
                </el-dropdown-menu>
            </template>
        </el-dropdown>
    </div>
</template>
<style lang = "scss" scoped>
    .control-bar{
        display: flex;
        flex-direction: row;
        height: 100%;
        width: 100%;
        color: black;
        background-color: #655555;
    }
</style>