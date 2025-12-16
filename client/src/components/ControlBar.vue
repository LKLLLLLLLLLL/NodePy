<script lang="ts" setup>
// import {useModalStore} from "@/stores/modalStore";
// import { useProjectStore } from "@/stores/projectStore";
import { DefaultService } from "@/utils/api";
import { Avatar } from '@element-plus/icons-vue'
import { ref,computed, watch } from "vue";
import { type Project } from "@/utils/api";
import { RouterLink } from 'vue-router';
import {useRoute,useRouter} from 'vue-router';
import { useGraphStore } from "@/stores/graphStore";
import { useModalStore } from "@/stores/modalStore";
import { useProjectStore } from "@/stores/projectStore";
import Logout from "./Logout.vue";
import { useLoginStore } from "@/stores/loginStore";
import UserInfoMenu from "./FloatingMenu/UserInfoMenu.vue";
import SvgIcon from '@jamescoyle/vue-icon';
import {
  mdiCompassOutline,
  mdiCompass,
  mdiHomeOutline,
  mdiHome,
  mdiFolderOutline,
  mdiFolder,
  mdiProjectorScreenOutline,
  mdiProjectorScreen,
} from '@mdi/js';
import notify from "./Notification/notify";

const explore_path_outline = mdiCompassOutline;
const explore_path_filled = mdiCompass;
const home_path_outline = mdiHomeOutline;
const home_path_filled = mdiHome;
const project_path_outline = mdiProjectorScreenOutline;
const project_path_filled = mdiProjectorScreen;
const file_path_outline = mdiFolderOutline;
const file_path_filled = mdiFolder;

const graphStore = useGraphStore()
const modalStore = useModalStore()
const loginStore = useLoginStore()
const projectStore = useProjectStore()
const route = useRoute()
const router = useRouter()

const showProjectName = computed(()=>{
  if(route.params.projectId)return true
  else return false
})

// 导航项
const navItems = [
  { name: 'Home', path: '/home', label: '首页', iconOutline: home_path_outline, iconFilled: home_path_filled },
  { name: 'Example', path: '/example', label: '探索', iconOutline: explore_path_outline, iconFilled: explore_path_filled },
  { name: 'Project', path: '/project', label: '工作台', iconOutline: project_path_outline, iconFilled: project_path_filled },
  { name: 'File', path: '/file', label: '文件库', iconOutline: file_path_outline, iconFilled: file_path_filled },
]

// 判断当前页面是否激活
const isActive = (path: string) => {
  return route.path === path
}

// 判断项目是否为只读模式
const isReadOnly = computed(() => {
    return graphStore.project.editable === false
})

</script>

<template>
  <div
    class="control-bar set_background_color"
    :class="{ 'readonly-mode': isReadOnly }"
  >
    <!-- 控制栏内容 -->
    <div class="control-content">
        <div class="logo-container">
          <img src="../../public/logo-trans.png" alt="Logo" class="logo"/>
        </div>
        <nav class="nav-bar" v-if="!showProjectName">
          <RouterLink
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="nav-link"
              :class="{ active: isActive(item.path) }"
            >
              <span class="nav-inner">
                <SvgIcon
                  v-if="item.iconOutline"
                  type="mdi"
                  :path="isActive(item.path) ? item.iconFilled : item.iconOutline"
                  class="nav-icon"
                />
                <span class="nav-label">{{ item.label }}</span>
              </span>
            </RouterLink>
        </nav>

        <div v-else class="project-name">
          <h2>{{ graphStore.project.project_name }}</h2>
          <!-- 只读提示 -->
          <div v-if="isReadOnly" class="readonly-indicator">
            只读
          </div>
        </div>

        <div class="user-avatar">
          <UserInfoMenu />
        </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '../common/global.scss' as *;
.control-bar {
  display: flex;
  flex-direction: row;
  height: 100%;
  width: 100%;
  color: black;
  box-shadow: 0 0px 15px rgba(128, 128, 128, 0.1);
  // border-bottom: 1px solid #e0e0e0;

  .control-content {
    display: flex;
    align-items: center;
    // justify-content: space-between;
    width: 100%;
    height: 100%;
    padding: 0 20px;
    font-size: 14px;
    cursor: context-menu;

    .logo-container {
      flex-shrink: 0;
      height: 90%;
      margin-left: 15px;
      position: absolute;
      user-select: none;

      .logo {
        height: 100%;
        width: auto;
      }
    }

    .nav-bar {
      display: flex;
      align-items: center;
      // gap: 6px;
      flex: 1;
      justify-content: center;
      .nav-link {
        color: #000000;
        text-decoration: none;
        font-size: 18px;
        font-weight: bold;
        padding: 9px 15px;
        margin: 0 6px;
        transition: all 0.18s ease;
        min-width: 120px;
        text-align: center;
        border-radius: 20px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: rgba(40, 40, 40, 0.76);

        &:hover {
          background-color: rgba(0, 0, 0, 0.06);
        }

        .nav-inner {
          display: inline-flex;
          align-items: center;
          gap: 8px;
        }

        .nav-icon {
          width: 22px;
          height: 22px;
          display: inline-block;
          fill: currentColor;
          // margin-right: 1px;
        }

        .nav-label {
          line-height: 1;
        }

        &.active {
          border-radius: 19px;
          color: $stress-color;
          background-color: white;
            box-shadow: 0px 3px 5px rgba(128, 128, 128, 0.10);
          // transform: translateY(-1px);
        }
      }
    }

    .project-name {
      position: absolute;
      left: 50%;
      transform: translateX(-50%);
      font-size: 14px;
      font-weight: 500;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .readonly-indicator {
      display: flex;
      // background-color: #108EFE;
      color: #9d9b9b;
      align-items: flex-end;
      justify-content: flex-start;
      height: 30px;
      width: 40px;
      margin-left: 7px;
      border-radius: 4px;
      font-size: 14px;
      font-weight: bold;
      // font-style: italic;
    }

    .add-to-my-project{
      margin-left: 10px;
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
      position: absolute;
      right: 0px;
    }
  }
}

</style>

<style lang="scss" scoped>
@use '../common/global.scss';
  .box {
    flex: 1;
  }
</style>
