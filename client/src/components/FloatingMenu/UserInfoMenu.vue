<template>
  <FloatingMenu placement="bottom" :offset="12">
    <!-- 触发元素：头像 -->
    <template #trigger>
      <div class="user-avatar-trigger">
        <!-- 未登录时显示 mdi 图标 -->
        <div v-if="!loginStore.isAuthenticated" class="initials-avatar small">
          <svg-icon type="mdi" :path="mdiAccount" :size="22"></svg-icon>
        </div>
        <!-- 登录但无头像时显示首字符 -->
        <div v-else-if="!avatarUrl" class="initials-avatar small">
          {{ userInitials }}
        </div>
        <!-- 登录且有头像时显示头像 -->
        <img
          v-else
          :src="avatarUrl"
          class="avatar-img"
        />
      </div>
    </template>

    <!-- 菜单内容：用户信息 -->
    <div class="user-info-menu">
      <!-- 未登录提示 -->
      <div v-if="!loginStore.isAuthenticated" class="not-logged-in">
        <div class="not-logged-in-icon">
          <!-- 使用 mdi 图标 -->
          <div class="initials-avatar large">
            <svg-icon type="mdi" :path="mdiAccount" :size="36"></svg-icon>
          </div>
        </div>
        <div class="not-logged-in-text">请先登录</div>
        <el-button @click="handleLogin">立即登录</el-button>
      </div>
      
      <!-- 用户头部 -->
      <div v-else class="user-header">
        <!-- 无头像时显示首字符 -->
        <div v-if="!avatarUrl" class="initials-avatar large">
          {{ userInitials }}
        </div>
        <!-- 有头像时显示头像 -->
        <img
          v-else
          :src="avatarUrl"
          class="user-avatar"
        />
        <div class="user-details">
          <div class="username">{{ userStore.currentUserInfo?.username || '未知用户' }}</div>
          <div class="email">{{ userStore.currentUserInfo?.email || '暂无邮箱' }}</div>
        </div>
      </div>

      <!-- 用户统计 -->
      <div v-if="loginStore.isAuthenticated" class="user-stats">
        <!-- 动态显示所有用户信息字段 -->
        <div 
          v-for="(value, key) in filteredUserInfo" 
          :key="key" 
          class="stat-item"
        >
          <span class="stat-label">{{ formatKey(key) }}:</span>
          <span class="stat-value">{{ formatValue(key, value) }}</span>
        </div>
        
        <!-- 合并显示存储空间信息 -->
        <div v-if="userStore.currentUserInfo?.file_space_used !== undefined && userStore.currentUserInfo?.file_space_total !== undefined" class="stat-item">
          <span class="stat-label">存储空间:</span>
          <span class="stat-value">{{ formatStorageSpace() }}</span>
        </div>
      </div>

      <!-- 分割线 -->
      <div v-if="loginStore.isAuthenticated" class="divider"></div>

      <!-- 菜单选项 -->
      <div v-if="loginStore.isAuthenticated" class="menu-actions">
        <!-- <button class="action-btn">
          <span class="icon">⚙️</span> 设置
        </button> -->
        <button class="action-btn logout" @click="handleLogout">
          <span class="icon"><svg-icon type="mdi" :path="mdiLogout" :size="22"></svg-icon></span> 登出
        </button>
        <!-- <button @click="tableStore.createTableModal()">点我测试表格编辑</button>
        <button @click="editorStore.createEditorModal()">点我测试脚本编辑</button> -->
      </div>
    </div>
  </FloatingMenu>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Avatar } from '@element-plus/icons-vue'
import { useLoginStore } from '@/stores/loginStore'
import { useModalStore } from '@/stores/modalStore'
import { useUserStore } from '@/stores/userStore'
import { useEditorStore } from '@/stores/editorStore'
import notify from '@/components/Notification/notify'
import FloatingMenu from './FloatingMenu.vue'
import EditableTableModal from '../EditableTable/EditableTableModal.vue'
import PyEditor from '../PyEditor/PyEditor.vue'
import Logout from '../Logout.vue'
import { useTableStore } from '@/stores/tableStore'
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiAccount, mdiLogout } from '@mdi/js'

const loginStore = useLoginStore()
const modalStore = useModalStore()
const userStore = useUserStore()
const tableStore = useTableStore()
const editorStore = useEditorStore()

const router = useRouter()

const logoutWidth = 300;
const logoutHeight = 200;

onMounted(async () => {
  if (!loginStore.isAuthenticated) return
  await userStore.refreshUserInfo()
  await userStore.getUserInfo()
})

function handleLogin() {
  router.replace({
    name: 'login' 
  })
}

async function handleLogout() {
  modalStore.createModal({
    component: Logout,
    title: '退出登录',
    isActive: true,
    isResizable: false,
    isDraggable: true,
    position: {
      x: window.innerWidth / 2 - logoutWidth / 2,
      y: window.innerHeight / 2 - logoutHeight / 2
    },
    size: {
      width: logoutWidth,
      height: logoutHeight
    },
    id: 'logout',
  })
  await userStore.refreshUserInfo();
}

// 判断是否有头像功能（未来可能添加）
const hasAvatar = computed(() => {
  // 目前不支持头像功能，返回false
  // 未来可以基于用户信息或其他条件来判断
  return false
})

// 判断是否有头像URL
const avatarUrl = computed(() => {
  // 检查用户信息中是否有头像URL
  return userStore.currentUserInfo?.avatar_url || ''
})

// 获取用户名首字母（支持中文和其他语言）
const userInitials = computed(() => {
  const username = userStore.currentUserInfo?.username || 'G'
  // 获取第一个字符，支持中文和其他语言
  const firstChar = username.charAt(0)
  return firstChar.toUpperCase()
})

// 过滤掉不需要显示的字段（包括存储空间字段，因为我们要合并显示它们）
const filteredUserInfo = computed(() => {
  const userInfo = userStore.currentUserInfo
  if (!userInfo) return {}
  
  // 过滤掉已经在其他地方显示的字段和一些不需要显示的字段
  const excludeKeys = ['username', 'email', 'id', 'file_space_used', 'file_space_total']
  const filtered: Record<string, any> = {}
  
  Object.keys(userInfo).forEach(key => {
    if (!excludeKeys.includes(key)) {
      filtered[key] = userInfo[key]
    }
  })
  
  return filtered
})

// 格式化键名显示
const formatKey = (key: string) => {
  const keyMap: Record<string, string> = {
    'projects_count': '项目数量',
    'file_space_used': '已使用存储',
    'file_space_total': '总存储空间',
    'created_at': '注册时间'
  }
  return keyMap[key] || key
}

// 格式化值显示
const formatValue = (key: string, value: any) => {
  // 格式化存储空间显示
  if (key.includes('space')) {
    return formatStorage(value)
  }
  
  // 格式化时间显示
  if (key === 'created_at' && typeof value === 'string') {
    return new Date(value).toLocaleDateString()
  }
  
  // 默认显示
  return value ?? 'N/A'
}

// 格式化存储空间显示
const formatStorage = (bytes: number | undefined) => {
  if (bytes === undefined || bytes === null) return '0 B'
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  // 如果是整数，不显示小数点
  if (size % 1 === 0) {
    return `${size} ${units[unitIndex]}`
  } else {
    // 保留两位小数
    return `${size.toFixed(2)} ${units[unitIndex]}`
  }
}

// 格式化存储空间显示（合并显示已用空间/总空间和百分比）
const formatStorageSpace = () => {
  const userInfo = userStore.currentUserInfo
  if (!userInfo) return 'N/A'
  
  const used = userInfo.file_space_used
  const total = userInfo.file_space_total
  
  if (used === undefined || total === undefined) return 'N/A'
  
  // 计算百分比
  const percentage = total > 0 ? Math.round((used / total) * 100) : 0
  
  // 格式化存储空间显示
  return `${formatStorage(used)} / ${formatStorage(total)}`
}
</script>

<style scoped lang="scss">
@use '../../common/global.scss' as *;
.user-avatar-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.2s ease;
  // @include controller-style;

  &:hover {
    background-color: rgba(0, 0, 0, 0.05);
    transform: scale(1.05);
  }

  .avatar-img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }

  .initials-avatar {
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: white;
    // border: 2px solid #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    background: $stress-color;
    
    &.small {
      width: 30px;
      height: 30px;
      font-size: 14px;
    }

    &.large {
      width: 56px;
      height: 56px;
      font-size: 20px;
      flex-shrink: 0;
    }
  }
}

.user-info-menu {
  width: 280px;
  padding: 16px;
  @include controller-style;

  .not-logged-in {
    text-align: center;
    padding: 20px 0;

    .initials-avatar {
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      color: white;
      // border: 2px solid #fff;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
      background: $stress-color;
      
      &.large {
        width: 56px;
        height: 56px;
        font-size: 20px;
        flex-shrink: 0;
      }
    }

    .not-logged-in-icon {
      // font-size: 48px;
      margin-bottom: 12px;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .not-logged-in-text {
      font-size: 16px;
      color: #666;
      margin-bottom: 16px;
    }

    .login-btn {
      background-color: #409eff;
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;

      &:hover {
        background-color: #66b1ff;
      }
    }
  }

  .user-header {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;

    .user-avatar {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      object-fit: cover;
      flex-shrink: 0;
    }

    .initials-avatar {
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      color: white;
      // border: 2px solid #fff;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
      background: $stress-color;
      
      &.large {
        width: 56px;
        height: 56px;
        font-size: 20px;
        flex-shrink: 0;
      }
    }

    .user-details {
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 4px;

      .username {
        font-weight: 600;
        font-size: 15px;
        color: #333;
      }

      .email {
        font-size: 13px;
        color: #666;
      }
    }
  }

  .user-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 16px;
    padding: 12px;
    background-color: #f5f7fa;
    border-radius: 6px;

    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;

      .stat-label {
        font-size: 14px;
        color: #999;
      }

      .stat-value {
        font-size: 14px;
        font-weight: 600;
        color: #333;
        text-align: center;
      }
    }
  }

  .divider {
    height: 1px;
    background-color: #e8e8e8;
    margin: 12px 0;
  }

  .menu-actions {
    display: flex;
    flex-direction: column;
    gap: 4px;

    .action-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 12px;
      border: none;
      background-color: transparent;
      color: #333;
      font-size: 14px;
      cursor: pointer;
      border-radius: 4px;
      transition: all 0.2s ease;

      .icon {
        font-size: 16px;
        display: flex;
        justify-content: center;
        align-items: center;
      }

      &:hover {
        background-color: #f0f0f0;
        color: #4a90e2;
      }

      &.logout {
        color: #e74c3c;

        &:hover {
          background-color: #ffe0e0;
          color: #c0392b;
        }
      }
    }
  }
}
</style>