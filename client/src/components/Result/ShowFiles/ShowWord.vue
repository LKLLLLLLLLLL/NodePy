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
  border-radius: 10px;
  padding: 12px;
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
  table-layout: auto;
}

.word-view :deep(th),
.word-view :deep(td) {
  border: 1px solid #000;
  padding: 8px 12px;
  text-align: left;
  vertical-align: top;
}

.word-view :deep(th) {
  background-color: #f2f2f2;
  font-weight: bold;
}

.word-view :deep(td) {
  background-color: #fff;
}

/* 表格单元格对齐 */
.word-view :deep(.ql-align-center) {
  text-align: center;
}

.word-view :deep(.ql-align-right) {
  text-align: right;
}

.word-view :deep(.ql-align-justify) {
  text-align: justify;
}

/* 图像样式 */
.word-view :deep(img) {
  max-width: 100%;
  height: auto;
}

/* 文本样式 - 加粗 */
.word-view :deep(strong),
.word-view :deep(b) {
  font-weight: bold;
}

/* 斜体 */
.word-view :deep(em),
.word-view :deep(i) {
  font-style: italic;
}

/* 下划线 */
.word-view :deep(u) {
  text-decoration: underline;
}

/* 删除线 */
.word-view :deep(s),
.word-view :deep(strike),
.word-view :deep(del) {
  text-decoration: line-through;
}

/* 上标 */
.word-view :deep(sup) {
  vertical-align: super;
  font-size: smaller;
  line-height: 1;
}

/* 下标 */
.word-view :deep(sub) {
  vertical-align: sub;
  font-size: smaller;
  line-height: 1;
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
  white-space: pre-wrap;
}

/* 引用 */
.word-view :deep(blockquote) {
  margin: 1em 0;
  padding: 0 1em;
  border-left: 4px solid #ccc;
  color: #666;
}

/* 字体样式 */
.word-view :deep(.ql-font-serif) {
  font-family: Georgia, 'Times New Roman', Times, serif;
}

.word-view :deep(.ql-font-monospace) {
  font-family: 'Courier New', Courier, monospace;
}

/* 字体大小 */
.word-view :deep(.ql-size-small) {
  font-size: 0.75em;
}

.word-view :deep(.ql-size-large) {
  font-size: 1.5em;
}

.word-view :deep(.ql-size-huge) {
  font-size: 2.5em;
}

/* 背景色 */
.word-view :deep(.ql-background-yellow) {
  background-color: #ffff00;
}

.word-view :deep(.ql-background-red) {
  background-color: #ff0000;
}

.word-view :deep(.ql-background-green) {
  background-color: #00ff00;
}

.word-view :deep(.ql-background-blue) {
  background-color: #0000ff;
}

/* 文本颜色 */
.word-view :deep(.ql-color-white) {
  color: #ffffff;
}

.word-view :deep(.ql-color-red) {
  color: #ff0000;
}

.word-view :deep(.ql-color-green) {
  color: #00ff00;
}

.word-view :deep(.ql-color-blue) {
  color: #0000ff;
}

/* 缩进 */
.word-view :deep(.ql-indent-1) {
  padding-left: 3em;
}

.word-view :deep(.ql-indent-2) {
  padding-left: 6em;
}

.word-view :deep(.ql-indent-3) {
  padding-left: 9em;
}

.word-view :deep(.ql-indent-4) {
  padding-left: 12em;
}

.word-view :deep(.ql-indent-5) {
  padding-left: 15em;
}

/* 行间距 */
.word-view :deep(.ql-line-height-normal) {
  line-height: normal;
}

.word-view :deep(.ql-line-height-1-5) {
  line-height: 1.5;
}

.word-view :deep(.ql-line-height-2-0) {
  line-height: 2.0;
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

/* 公式样式 */
.word-view :deep(.ql-formula) {
  background: rgba(0, 0, 0, 0.05);
  font-family: 'Cambria Math', serif;
  font-style: italic;
  padding: 2px 4px;
  border-radius: 3px;
}

/* 双删除线 */
.word-view :deep(.ql-underline) {
  text-decoration: underline;
}

/* 双下划线 */
.word-view :deep(.ql-double-underline) {
  text-decoration: underline;
  text-decoration-style: double;
}

/* 波浪下划线 */
.word-view :deep(.ql-wave-underline) {
  text-decoration: underline;
  text-decoration-style: wavy;
}

/* 点线 */
.word-view :deep(.ql-dotted-underline) {
  text-decoration: underline;
  text-decoration-style: dotted;
}

/* 虚线 */
.word-view :deep(.ql-dashed-underline) {
  text-decoration: underline;
  text-decoration-style: dashed;
}

/* 表格边框样式 */
.word-view :deep(.ql-table-border-none) {
  border: none;
}

.word-view :deep(.ql-table-border-solid) {
  border: 1px solid #000;
}

.word-view :deep(.ql-table-border-dashed) {
  border: 1px dashed #000;
}

.word-view :deep(.ql-table-border-dotted) {
  border: 1px dotted #000;
}

/* 表格单元格边框 */
.word-view :deep(.ql-table-cell-border-none) {
  border: none;
}

.word-view :deep(.ql-table-cell-border-solid) {
  border: 1px solid #000;
}

.word-view :deep(.ql-table-cell-border-dashed) {
  border: 1px dashed #000;
}

.word-view :deep(.ql-table-cell-border-dotted) {
  border: 1px dotted #000;
}

/* 表格背景色 */
.word-view :deep(.ql-table-bg-yellow) {
  background-color: #ffff00;
}

.word-view :deep(.ql-table-bg-red) {
  background-color: #ff0000;
}

.word-view :deep(.ql-table-bg-green) {
  background-color: #00ff00;
}

.word-view :deep(.ql-table-bg-blue) {
  background-color: #0000ff;
}

/* 表格文本对齐 */
.word-view :deep(.ql-table-text-left) {
  text-align: left;
}

.word-view :deep(.ql-table-text-center) {
  text-align: center;
}

.word-view :deep(.ql-table-text-right) {
  text-align: right;
}

/* 添加对更复杂表格的支持 */
.word-view :deep(table[cellpadding]) :deep(td),
.word-view :deep(table[cellpadding]) :deep(th) {
  padding: attr(cellpadding px);
}

.word-view :deep(table[cellspacing]) {
  border-spacing: attr(cellspacing px);
}

/* 添加对表格宽度的支持 */
.word-view :deep(table[width]) {
  width: attr(width);
}

/* 添加对单元格宽度的支持 */
.word-view :deep(td[width]),
.word-view :deep(th[width]) {
  width: attr(width);
}
</style>