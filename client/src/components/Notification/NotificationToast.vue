<template>
  <div class="toast" :class="msg.type" @mouseenter="hover=true" @mouseleave="hover=false">
    <div class="content">{{ msg.message }}</div>
    <button class="close" @click="close">×</button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Keep types lightweight here to avoid tight coupling; the shared notify module provides the runtime state.
const props = defineProps<{ msg: any; remove: (id: number) => void }>()
const hover = ref(false)

function close() {
  props.remove(props.msg.id)
}

// Pause auto-dismiss when hovered (notification service handles timeout, but component can inform future enhancements)
onMounted(() => {})
</script>

<style scoped lang="scss">
@use '@/common/global.scss' as *;

.toast{
  @include controller-style;
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:5px 14px;
  /* controller-style already sets border-radius, background and box-shadow */
  color:#fff;
  margin-top:10px;
  font-size:14px;
}
.toast .content{flex:1;padding-right:8px;text-align: center;}
.toast .close{background:transparent;border:none;color:inherit;font-size:18px;cursor:pointer}
.toast.success{background:#67C23A;color:#fff}
.toast.error{background:#F56C6C;color:#fff}
.toast.info{background:#ffffff;color:#222;border:1px solid rgba(0,0,0,0.06)}
.toast.warning{background:#E6A23C;color:#fff}
</style>
