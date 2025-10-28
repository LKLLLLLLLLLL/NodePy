<script lang="ts" setup>
import { ref, computed } from 'vue'
import { nodeMenuItems } from '@/types/menuTypes'
import { useGraphStore } from '@/stores/graphStore'
import {useModalStore} from "@/stores/modalStore";
import { useProjectStore } from '@/stores/projectStore';
import { usePageStore, type Page} from '@/stores/pageStore';
import { Avatar, User } from '@element-plus/icons-vue'
import { RouterLink } from 'vue-router';
import { ElMessage } from 'element-plus';
import {useRoute} from 'vue-router';
import Result from './results/Result.vue';

const route=useRoute()
const modalStore = useModalStore()

function handleClickResult(){
    const marginRight = 20; // 距离右侧的间距
    const modalWidth = 600; // 弹窗宽度
    const modalHeight = 800; // 弹窗高度

    // 计算位置：窗口宽度 - 弹窗宽度 - 右侧间距
    const xPosition = window.innerWidth - modalWidth - marginRight;
    const yPosition = (window.innerHeight - modalHeight)/2;

    modalStore.createModal({
        id: 'result',
        title: '结果查看',
        isActive: true,
        isDraggable: true,
        isResizable: false,
        position:{
            x: xPosition,
            y: yPosition
        },
        size: {
            width: modalWidth,
            height: modalHeight
        },
        component: Result
    })
}

// 导航项
const navItems = [
  { name: 'Home', path: '/home', label: '首页' },
  { name: 'File', path: '/file', label: '文件' },
  { name: 'Project', path: '/project', label: '项目' },
  { name: 'Example', path: '/example', label: '示例' },
]

// 判断当前页面是否激活
const isActive = (path: string) => {
  return route.path === path
}

function handleAvatarClick(){
    // 处理头像点击事件，比如显示用户菜单
    console.log('Avatar clicked');
}

</script>

<template>
  <div
    class="control-bar set_background_color"
  >
    <!-- 控制栏内容 -->
    <div class="control-content">
        <div class="logo-container">
          <img src="../../public/logo-trans.png" alt="Logo" class="logo"/>
        </div>
        <nav class="nav-bar">
          <RouterLink
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-link"
            :class="{ active: isActive(item.path) }"
          >
            {{ item.label }}
          </RouterLink>
        </nav>
        <div class="actions">
          <el-button @click="handleClickResult" size="small">结果</el-button>

        </div>
        <div class="user-avatar">
          <el-avatar :icon="Avatar" size="small" @click="handleAvatarClick"></el-avatar>
        </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.control-bar {
  display: flex;
  flex-direction: row;
  height: 100%;
  width: 100%;
  color: black;
  position: relative;
  box-shadow: 0 0px 15px rgba(128, 128, 128, 0.1);

  .control-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    height: 100%;
    padding: 0 20px;
    font-size: 14px;
    cursor: context-menu;

    .logo-container {
      flex-shrink: 0;
      height: 90%;
      margin-left: 15px;

      .logo {
        height: 100%;
        width: auto;
      }
    }

    .nav-bar {
      display: flex;
      align-items: center;
      gap: 32px;
      flex: 1;
      justify-content: center;

      .nav-link {
        color: #000000;
        text-decoration: none;
        font-size: 18px;
        font-weight: 400;
        padding: 8px 16px;
        margin: 0 0.4%;
        border-bottom: 2px solid transparent;
        transition: all 0.3s ease;

        &:hover {
          color: #108EFE;
        }

        &.active {
          color: #000000;
          border-bottom-color: #108EFE;
        }
      }
    }

    .actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }

    .user-avatar {
      flex-shrink: 0;
      margin-left: 20px;
      margin-right: 15px;
      cursor: pointer;
    }
  }
}

</style>

<style lang="scss" scoped>
@use '../common/style/global.scss';
  .box {
    flex: 1;
  }
</style>
