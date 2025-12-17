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
        <div class="not-logged-in-text">请先登录</div>
        <button class="login-btn" @click="handleLogin">立即登录</button>
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
        <div v-if="userStore.currentUserInfo?.projects_count !== undefined" class="stat-item">
          <span class="stat-label">项目数量</span>
          <span class="stat-value">{{ userStore.currentUserInfo.projects_count }}</span>
        </div>

        <div v-if="userStore.currentUserInfo?.file_space_used !== undefined && userStore.currentUserInfo?.file_space_total !== undefined" class="stat-item">
          <span class="stat-label">存储空间</span>
          <span class="stat-value">{{ formatStorage(userStore.currentUserInfo.file_space_used) }} / {{ formatStorage(userStore.currentUserInfo.file_space_total) }}</span>
        </div>
      </div>

      <!-- 分割线 -->
      <div v-if="loginStore.isAuthenticated" class="divider"></div>

      <!-- 菜单选项 -->
      <div v-if="loginStore.isAuthenticated" class="menu-actions">
        <button class="logout-btn" @click="handleLogout">退出登录</button>
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

const logoutWidth = 350;
const logoutHeight = 270;

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
    isModal: true,
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

// 计算存储空间使用百分比
const getStoragePercentage = () => {
  const userInfo = userStore.currentUserInfo
  if (!userInfo) return 0

  const used = userInfo.file_space_used
  const total = userInfo.file_space_total

  if (used === undefined || total === undefined || total === 0) return 0

  return Math.min(Math.round((used / total) * 100), 100)
}

// 格式化加入日期
const formatJoinDate = (dateString: string) => {
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  return `${year}年${month}月`
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
  transition: background-color 0.12s ease;

  &:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }

  .avatar-img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .initials-avatar {
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: white;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    background: $stress-color;

    &.small {
      width: 36px;
      height: 36px;
      font-size: 15px;
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
  width: 300px;
  padding: 20px;
  @include controller-style;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(31, 45, 61, 0.12);

  .not-logged-in {
    text-align: center;
    padding: 20px 0;

    .not-logged-in-text {
      font-size: 15px;
      color: rgba(0, 0, 0, 0.65);
      margin-bottom: 20px;
      font-weight: 500;
    }

    .login-btn {
      background-color: $stress-color;
      width: 100%;
      color: white;
      border: none;
      padding: 10px 24px;
      border-radius: 10px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      transition: transform 0.12s ease, box-shadow 0.12s ease;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);

      &:hover {
        // transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      }
    }
  }

  .user-header {
    display: flex;
    gap: 14px;
    margin-bottom: 12px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);

    .user-avatar {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      object-fit: cover;
      flex-shrink: 0;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .initials-avatar {
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      color: white;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
      gap: 5px;
      min-width: 0;
      flex: 1;

      .username {
        font-weight: 600;
        font-size: 16px;
        color: rgba(0, 0, 0, 0.87);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .email {
        font-size: 12px;
        color: rgba(0, 0, 0, 0.55);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
  }

  .user-stats {
    display: flex;
    flex-direction: column;
    // gap: 12px;s
    margin-bottom: 16px;

    .stat-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 0;

      .stat-label {
        font-size: 14px;
        color: rgba(0, 0, 0, 0.6);
        font-weight: 500;
      }

      .stat-value {
        font-size: 14px;
        font-weight: 600;
        color: rgba(0, 0, 0, 0.87);
      }
    }
  }

  .divider {
    height: 1px;
    background-color: rgba(0, 0, 0, 0.06);
    margin: 16px 0;
  }

  .menu-actions {
    .logout-btn {
      width: 100%;
      background-color: #ff4d4f;
      color: white;
      border: none;
      padding: 10px;
      border-radius: 10px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      transition: transform 0.12s ease, box-shadow 0.12s ease, background-color 0.12s ease;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);

      &:hover {
        background-color: #ff7875;
        // transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      }
    }
  }
}
</style>
