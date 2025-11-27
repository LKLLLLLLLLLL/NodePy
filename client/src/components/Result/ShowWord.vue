<script lang="ts" setup>
defineProps<{
  content: string
}>()
</script>

<template>
  <div class="word-view" v-html="content"></div>
</template>

<style scoped>
.word-view {
  flex: 1;
  overflow: auto;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  margin: 12px;
  font-family: 'Microsoft YaHei', 'SimSun', serif;
  line-height: 1.5;
}

/* 通用样式重置，让 Word 样式优先 */
.word-view :deep(*) {
  box-sizing: border-box;
}

/* 保留原始段落样式 */
.word-view :deep(p) {
  margin: 0 0 1em 0;
  line-height: 1.5;
}

/* 保留原始标题样式 */
.word-view :deep(h1),
.word-view :deep(h2),
.word-view :deep(h3),
.word-view :deep(h4),
.word-view :deep(h5),
.word-view :deep(h6) {
  margin: 1em 0 0.5em 0;
  font-weight: bold;
  line-height: 1.3;
}

.word-view :deep(h1) {
  font-size: 2em;
}

.word-view :deep(h2) {
  font-size: 1.5em;
}

.word-view :deep(h3) {
  font-size: 1.17em;
}

.word-view :deep(h4) {
  font-size: 1em;
}

.word-view :deep(h5) {
  font-size: 0.83em;
}

.word-view :deep(h6) {
  font-size: 0.67em;
}

/* 列表样式 */
.word-view :deep(ul),
.word-view :deep(ol) {
  margin: 1em 0;
  padding-left: 2em;
}

.word-view :deep(li) {
  margin: 0.25em 0;
}

.word-view :deep(ul li) {
  list-style-type: disc;
}

.word-view :deep(ol li) {
  list-style-type: decimal;
}

/* 表格样式 */
.word-view :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.word-view :deep(th),
.word-view :deep(td) {
  border: 1px solid #000;
  padding: 3px 4px;
  text-align: left;
  vertical-align: top;
}

.word-view :deep(th) {
  background-color: #f2f2f2;
  font-weight: bold;
}

/* 图像样式 */
.word-view :deep(img) {
  max-width: 100%;
  height: auto;
}

/* 文本样式 */
.word-view :deep(strong),
.word-view :deep(b) {
  font-weight: bold;
}

.word-view :deep(em),
.word-view :deep(i) {
  font-style: italic;
}

.word-view :deep(u) {
  text-decoration: underline;
}

.word-view :deep(s),
.word-view :deep(strike) {
  text-decoration: line-through;
}

.word-view :deep(sub) {
  vertical-align: sub;
  font-size: smaller;
}

.word-view :deep(sup) {
  vertical-align: super;
  font-size: smaller;
}

/* 链接样式 */
.word-view :deep(a) {
  color: #0000ff;
  text-decoration: underline;
}

/* 分割线 */
.word-view :deep(hr) {
  border: none;
  border-top: 1px solid #000;
  margin: 1em 0;
}

/* 代码块 */
.word-view :deep(pre) {
  font-family: 'Courier New', Courier, monospace;
  background-color: #f5f5f5;
  padding: 10px;
  overflow-x: auto;
  margin: 1em 0;
  border: 1px solid #ccc;
}

/* 引用 */
.word-view :deep(blockquote) {
  margin: 1em 0;
  padding: 0 1em;
  border-left: 4px solid #ccc;
  color: #666;
}

/* 文本对齐 */
.word-view :deep(.ql-align-center) {
  text-align: center;
}

.word-view :deep(.ql-align-right) {
  text-align: right;
}

.word-view :deep(.ql-align-justify) {
  text-align: justify;
}
</style>