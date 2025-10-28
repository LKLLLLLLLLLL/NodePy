<script lang="ts" setup>

import { useGraphStore } from '@/stores/graphStore'
import { ref } from 'vue'
import { nodeMenuItems } from '@/types/menuTypes'
import { computed } from 'vue'

const graphStore = useGraphStore()
const { addNode } = graphStore
    const showMenu = ref(false)
    const x = ref(0)
    const y = ref(0)

// 计算菜单位置
const menuLocation = computed(() => {
  return x.value > window.innerWidth / 2 ? 'left' : 'right'
})

// 获取叶子节点（扁平化处理三级菜单）
const getLeafItems = (item: any) => {
  const leafItems: any[] = []

  if (item.children) {
    item.children.forEach((child: any) => {
      if (child.children) {
        // 如果有三级菜单，将其扁平化到二级
        leafItems.push(...child.children)
      } else {
        // 直接是叶子节点
        leafItems.push(child)
      }
    })
  }

  return leafItems
}

// 处理右键点击事件
const handleContextmenu = (event: MouseEvent) => {
  event.preventDefault()

  x.value = event.clientX
  y.value = event.clientY
  showMenu.value = false

  // 使用 setTimeout 确保 DOM 更新后再显示菜单
  setTimeout(() => {
    showMenu.value = true
  }, 10)
}

// 处理节点选择
const handleNodeSelect = (nodeType: string) => {
  console.log('添加节点:', nodeType)
  addNode(nodeType)
  showMenu.value = false
}
</script>
<template>
    <!-- 透明激活器，确保菜单在鼠标处弹出 -->
    <div
      v-if="showMenu"
      :style="{
        position: 'fixed',
        left: x + 'px',
        top: y + 'px',
        width: '1px',
        height: '1px',
        zIndex: 9999,
        pointerEvents: 'none'
      }"
      id="menu-activator"
    ></div>

    <!-- 主菜单 -->
    <v-menu
      v-model="showMenu"
      activator="#menu-activator"
      absolute
      :close-on-content-click="false"
      offset="2"
      :location="menuLocation"
    >
      <v-list density="compact" class="main-menu">
        <template v-for="(item, index) in nodeMenuItems" :key="item.value">
          <!-- 有子菜单的项 -->
          <v-list-item
            v-if="item.children"
            :title="item.label"
            @click.stop
            class="menu-item parent-item"
          >
            <template #append>
              <v-icon
                :icon="menuLocation === 'right' ? 'mdi-chevron-right' : 'mdi-chevron-left'"
                size="x-small"
              ></v-icon>
            </template>

            <!-- 二级菜单 -->
            <v-menu
              :open-on-focus="false"
              activator="parent"
              open-on-hover
              :location="menuLocation"
              submenu
              :close-on-content-click="false"
              offset="2"
            >
              <v-list density="compact" class="submenu">
                <v-list-item
                  v-for="(leafItem, leafIndex) in getLeafItems(item)"
                  :key="leafItem.value"
                  :title="leafItem.label"
                  @click="handleNodeSelect(leafItem.value)"
                  class="leaf-item submenu-item"
                />
              </v-list>
            </v-menu>
          </v-list-item>

          <!-- 一级叶子节点 -->
          <v-list-item
            v-else
            :title="item.label"
            @click="handleNodeSelect(item.value)"
            class="leaf-item parent-item"
          />
        </template>
      </v-list>
    </v-menu>
</template>
<style scoped lang="scss">
// 主菜单样式
:deep(.main-menu) {
  min-width: 160px;
  padding: 6px 4px !important;
  border-radius: 12px !important; // 增大圆角

  .v-list-item {
    min-height: 28px !important;
    margin: 2px 4px !important;
    border-radius: 6px !important; // 增大菜单项圆角
    cursor: pointer;

    &:hover {
      background-color: rgba(0, 0, 0, 0.06);
    }
  }
}

// 父级菜单项样式
:deep(.parent-item) {
  margin: 3px 4px !important;
  background-color: rgba(0, 0, 0, 0.02);

  &:hover {
    background-color: rgba(0, 0, 0, 0.08);
  }
}

// 子菜单样式
:deep(.submenu) {
  min-width: 160px;
  padding: 6px 4px !important;
  border-radius: 12px !important; // 增大圆角

  .v-list-item {
    min-height: 28px !important;
    margin: 1px 4px !important;
    border-radius: 6px !important; // 增大菜单项圆角
    cursor: pointer;

    &:hover {
      background-color: rgba(0, 0, 0, 0.06);
    }
  }
}

// 子菜单项样式
:deep(.submenu-item) {
  margin: 1px 4px !important;
}

// 叶子节点样式
:deep(.leaf-item) {
  min-height: 28px !important;
  border-radius: 6px !important; // 增大圆角

  &:hover {
    background-color: rgba(0, 123, 255, 0.12) !important;
  }
}

// 菜单项内容样式
:deep(.v-list-item__content) {
  padding: 4px 0 !important;
}

// 菜单标题样式
:deep(.v-list-item-title) {
  font-size: 13px !important;
  line-height: 1.2 !important;
  padding: 0 4px;
}

// 确保子菜单样式正确 - 增大所有菜单容器的圆角
:deep(.v-menu__content) {
  border-radius: 16px !important; // 显著增大圆角
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important; // 增强阴影以配合更大的圆角
  overflow: hidden; // 确保内容不超出圆角边界

  .v-list {
    background-color: #ffffff;
  }
}
</style>