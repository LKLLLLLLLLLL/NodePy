<script lang="ts" setup>
defineProps<{
  src: string
  alt: string
  onError: () => void
  onLoad: () => void
}>()
</script>

<template>
  <div class="image-view">
    <img
      :src="src"
      :alt="alt"
      class="file-img"
      @error="onError"
      @load="onLoad"
    />
  </div>
</template>

<style scoped>
.image-view {
  flex: 1;
  overflow: auto;
  background: white;
  /* border: 1px solid #e4e7ed; */
  border-radius: 10px;
  /* padding: 12px; */
  display: flex;
  justify-content: center;
  align-items: center;
}

.file-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
</style>
