<template>
  <transition-group
    name="toast"
    tag="div"
    class="notification-root"
    :style="{ top: typeof props.topOffset === 'number' ? props.topOffset + 'px' : (props.topOffset || '20px') }"
  >
    <NotificationToast
      v-for="msg in state.messages"
      :key="msg.id"
      :msg="msg"
      :remove="remove"
      class="toast-item"
    />
  </transition-group>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { notificationState as state, remove, setNotifyDefaults } from '@/components/Notification/notify'
import NotificationToast from './NotificationToast.vue'

const props = defineProps<{
  topOffset?: string | number
  defaultDuration?: number
}>()

// set defaults from props when container mounts
onMounted(() => {
  if (props.defaultDuration !== undefined) {
    setNotifyDefaults({ duration: props.defaultDuration })
  }
})

</script>

<style scoped lang="scss">
@use '../../common/global.scss' as *;
.notification-root{
  position:fixed;
  left:50%;
  transform:translateX(-50%);
  /* top is set inline by the component instance via :style binding when used */
  top:20px;
  z-index:2000;
  display:flex;
  flex-direction:column;
  align-items:center;
  pointer-events:none; /* allow clicks through gaps */
}

.toast-item{
  pointer-events:auto; /* make toasts clickable */
}

/* enter: start above and move down into place; leave: move up and fade */
.toast-enter-from{
  transform: translateY(-18px) scale(0.995);
  opacity: 0;
}
.toast-enter-active{
  transition: all 300ms cubic-bezier(.2,.9,.2,1);
}
.toast-enter-to{
  transform: translateY(0) scale(1);
  opacity: 1;
}
.toast-leave-from{
  transform: translateY(0);
  opacity: 1;
}
.toast-leave-active{
  transition: all 250ms ease-in;
}
.toast-leave-to{
  transform: translateY(-18px) scale(0.99);
  opacity: 0;
}

/* small responsive tweak */
@media (max-width:420px){
  .notification-root{right:8px;left:8px;transform:none}
  .notification-root .toast{width:100%;max-width:none}
}
</style>
