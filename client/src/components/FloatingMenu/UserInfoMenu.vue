<template>
  <FloatingMenu placement="bottom" :offset="12">
    <!-- 触发元素：头像 -->
    <template #trigger>
      <div class="user-avatar-trigger">
        <el-avatar
          v-if="!avatarUrl"
          :icon="Avatar"
          size="small"
        />
        <img
          v-else
          :src="avatarUrl"
          :alt="userInfo.username"
          class="avatar-img"
          :title="`${userInfo.username}`"
        />
      </div>
    </template>

    <!-- 菜单内容：用户信息 -->
    <div class="user-info-menu">
      <!-- 用户头部 -->
      <div class="user-header">
        <el-avatar
          v-if="!avatarUrl"
          :icon="Avatar"
          size="large"
        />
        <img
          v-else
          :src="avatarUrl"
          :alt="userInfo.username"
          class="user-avatar"
        />
        <div class="user-details">
          <div class="username">{{ userInfo.username }}</div>
          <div class="email">{{ userInfo.email }}</div>
        </div>
      </div>

      <!-- 用户统计 -->
      <div class="user-stats">
        <div class="stat-item">
          <span class="stat-label">项目:</span>
          <span class="stat-value">{{ userInfo.projectCount }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">节点:</span>
          <span class="stat-value">{{ userInfo.nodeCount }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">存储:</span>
          <span class="stat-value">{{ userInfo.storageUsed }}</span>
        </div>
      </div>

      <!-- 用户等级 -->
      <div class="user-tier">
        <span class="tier-label">等级:</span>
        <span class="tier-value" :class="`tier-${userInfo.tier}`">{{
          userInfo.tier
        }}</span>
      </div>

      <!-- 分割线 -->
      <div class="divider"></div>

      <!-- 菜单选项 -->
      <div class="menu-actions">
        <button class="action-btn" @click="handleProfile">
          <span class="icon">👤</span> 个人资料
        </button>
        <button class="action-btn" @click="handleSettings">
          <span class="icon">⚙️</span> 设置
        </button>
        <button class="action-btn" @click="handleHelp">
          <span class="icon">❓</span> 帮助
        </button>
        <button class="action-btn logout" @click="handleLogout">
          <span class="icon" @click="">🚪</span> 登出
        </button>
      </div>
    </div>
  </FloatingMenu>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import FloatingMenu from './FloatingMenu.vue'
import { useLoginStore } from '@/stores/loginStore'
import notify from '@/components/Notification/notify'
import { Avatar } from '@element-plus/icons-vue'


// 类型定义
interface UserInfo {
  username: string
  email: string
  projectCount: number
  nodeCount: number
  storageUsed: string
  tier: 'free' | 'pro' | 'enterprise'
}

// 状态
const loginStore = useLoginStore()

// 示例用户信息（后续可通过 API 获取）
const userInfo = ref<UserInfo>({
  username: '张三',
  email: 'zhangsan@example.com',
  projectCount: 5,
  nodeCount: 48,
  storageUsed: '2.4 GB / 10 GB',
  tier: 'pro',
})

// 头像 URL（当没有用户头像时为空）
const avatarUrl = computed(() => {
  // 返回空字符串表示使用 el-avatar 的默认显示
  return ''
})

// 方法
const handleProfile = () => {
  notify({
    message: '跳转到个人资料页面',
    type: 'info',
  })
  // router.push('/profile')
}

const handleSettings = () => {
  notify({
    message: '跳转到设置页面',
    type: 'info',
  })
  // router.push('/settings')
}

const handleHelp = () => {
  notify({
    message: '打开帮助文档',
    type: 'info',
  })
  // window.open('/help')
}

const handleLogout = async () => {
  notify({
    message: '正在登出...',
    type: 'info',
  })
  await loginStore.logout()
}
</script>

<style scoped lang="scss">
.user-avatar-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.2s ease;

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
}

.user-info-menu {
  width: 280px;
  padding: 16px;

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
    grid-template-columns: 1fr 1fr 1fr;
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
        font-size: 12px;
        color: #999;
      }

      .stat-value {
        font-size: 16px;
        font-weight: 600;
        color: #333;
      }
    }
  }

  .user-tier {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-bottom: 16px;
    padding: 8px 12px;
    background-color: #f0f4ff;
    border-radius: 6px;

    .tier-label {
      font-size: 12px;
      color: #666;
    }

    .tier-value {
      font-size: 14px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 4px;

      &.tier-free {
        background-color: #e0e0e0;
        color: #333;
      }

      &.tier-pro {
        background-color: #4a90e2;
        color: white;
      }

      &.tier-enterprise {
        background-color: #f5a623;
        color: white;
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
