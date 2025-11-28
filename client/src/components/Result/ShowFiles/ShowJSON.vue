<script lang="ts" setup>
import VueJsonPretty from 'vue-json-pretty'
import 'vue-json-pretty/lib/styles.css'

defineProps<{
  data: any
}>()
</script>

<template>
  <div class="json-view">
    <VueJsonPretty 
      :data="data" 
      :deep="3"
      :showLength="true"
      :showLine="true"
      :highlightMouseoverNode="true"
    />
  </div>
</template>

<style scoped>
.json-view {
  flex: 1;
  overflow: auto;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  margin: 12px;
}
</style>