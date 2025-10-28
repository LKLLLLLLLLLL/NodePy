<script lang="ts" setup>
import {useModalStore} from "@/stores/modalStore";
import { Avatar, User } from '@element-plus/icons-vue'
import { RouterLink } from 'vue-router';
import {useRoute} from 'vue-router';


const route=useRoute()

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
