<template>
  <div class="python-editor-modal">
    <!-- 基本介绍和控制 -->
    <div class="editor-header">
      <h3>Python代码编辑器</h3>
      <div class="controls">
        <label class="switch">
          <input type="checkbox" v-model="editable" />
          <span class="slider"></span>
        </label>
        <span class="editable-label">{{ editable ? '可编辑' : '只读' }}</span>
      </div>
    </div>
    
    <!-- 编辑器主体 -->
    <div class="editor-wrapper">
      <pre 
        ref="editor"
        class="code-editor"
        :contenteditable="editable"
        @input="handleInput"
        @keydown="handleKeydown"
        @paste="handlePaste"
        @scroll="syncScroll"
        @beforeinput="handleBeforeInput"
        spellcheck="false"
      ></pre>
      <pre 
        ref="highlighter"
        class="code-highlighter"
        aria-hidden="true"
      ><code class="language-python" ref="codeElement"></code></pre>
    </div>
    
    <!-- 状态信息 -->
    <div class="editor-footer">
      <span>行数: {{ lineCount }}</span>
      <span>字符数: {{ codeLength }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue';

// 引入Prism.js和Python语法高亮
import Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/themes/prism.css';

const props = defineProps<{
  modelValue?: string;
  readOnly?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
}>();

const editor = ref<HTMLElement | null>(null);
const highlighter = ref<HTMLElement | null>(null);
const codeElement = ref<HTMLElement | null>(null);

// 默认代码
const defaultCode = `#!/usr/bin/env python3

# Python代码编辑器示例
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()`;

// 响应式数据
const code = ref(props.modelValue || defaultCode);
const editable = ref(!props.readOnly);

// 计算属性
const lineCount = computed(() => code.value.split('\n').length);
const codeLength = computed(() => code.value.length);

// 高亮代码
const highlightCode = () => {
  if (!codeElement.value) return;
  
  const highlighted = Prism.highlight(
    code.value, 
    Prism.languages.python, 
    'python'
  );
  codeElement.value.innerHTML = highlighted;
};

// 同步滚动
const syncScroll = () => {
  if (highlighter.value && editor.value) {
    highlighter.value.scrollTop = editor.value.scrollTop;
    highlighter.value.scrollLeft = editor.value.scrollLeft;
  }
};

// 处理输入前的事件，用于阻止默认行为并正确处理撤销
const handleBeforeInput = (event: InputEvent) => {
  // 让浏览器处理撤销/重做操作
  if (event.inputType === 'historyUndo' || event.inputType === 'historyRedo') {
    return;
  }
};

// 处理输入
const handleInput = () => {
  if (editor.value) {
    const newCode = editor.value.textContent || '';
    code.value = newCode;
    emit('update:modelValue', newCode);
    highlightCode();
  }
};

// 获取当前光标位置（改进版）
const getCursorPosition = (): { lineNumber: number; columnNumber: number } => {
  if (!editor.value) return { lineNumber: 0, columnNumber: 0 };
  
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) return { lineNumber: 0, columnNumber: 0 };
  
  const range = selection.getRangeAt(0);
  
  // 获取从编辑器开始到光标位置的文本
  const preRange = document.createRange();
  preRange.setStart(editor.value, 0);
  preRange.setEnd(range.startContainer, range.startOffset);
  
  const textUpToCursor = preRange.toString();
  const lines = textUpToCursor.split('\n');
  const lineNumber = lines.length - 1;
  const columnNumber = lines[lines.length - 1]!.length;
  
  return { lineNumber, columnNumber };
};

// 设置光标位置（改进版）
const setCursorPosition = (lineNumber: number, columnNumber: number) => {
  if (!editor.value) return;
  
  const selection = window.getSelection();
  if (!selection) return;
  
  // 获取所有文本节点
  const textNodes: Text[] = [];
  const walker = document.createTreeWalker(
    editor.value,
    NodeFilter.SHOW_TEXT,
    null
  );
  
  let node = walker.nextNode();
  while (node) {
    if (node.nodeType === Node.TEXT_NODE) {
      textNodes.push(node as Text);
    }
    node = walker.nextNode();
  }
  
  // 计算目标位置
  let totalCharCount = 0;
  
  // 遍历所有文本节点查找目标位置
  for (const node of textNodes) {
    const nodeText = node.textContent || '';
    const nodeLines = nodeText.split('\n');
    
    let lineCharCount = 0;
    for (let i = 0; i < nodeLines.length; i++) {
      const lineText = nodeLines[i];
      const isLastLine = i === nodeLines.length - 1;
      
      // 计算当前行在整体中的行号
      const currentGlobalLine = totalCharCount > 0 ? 
        (nodeText.substring(0, lineCharCount).split('\n').length - 1) + 
        (editor.value.textContent?.substring(0, editor.value.textContent.indexOf(nodeText)).split('\n').length || 0) :
        (editor.value.textContent?.substring(0, editor.value.textContent.indexOf(nodeText)).split('\n').length || 0);
      
      // 如果找到了目标行
      if (currentGlobalLine === lineNumber) {
        // 计算列位置
        const actualColumn = Math.min(columnNumber, lineText!.length);
        
        // 设置光标位置
        const range = document.createRange();
        range.setStart(node, lineCharCount + actualColumn);
        range.collapse(true);
        
        selection.removeAllRanges();
        selection.addRange(range);
        return;
      }
      
      // 更新字符计数
      lineCharCount += lineText!.length + (isLastLine ? 0 : 1); // +1 for \n
    }
    
    totalCharCount += nodeText.length;
  }
  
  // 如果没找到特定位置，将光标放在开头
  if (textNodes.length > 0) {
    const range = document.createRange();
    range.setStart(textNodes[0]!, 0);
    range.collapse(true);
    
    selection.removeAllRanges();
    selection.addRange(range);
  }
};

// 获取指定行的内容
const getLineContent = (lineNumber: number): string => {
  const lines = code.value.split('\n');
  const line = lines[lineNumber];
  return line !== undefined ? line : '';
};

// 计算指定行的缩进
const getLineIndent = (lineNumber: number): string => {
  const lineContent = getLineContent(lineNumber);
  const match = lineContent.match(/^(\s*)/);
  return match && match[1] !== undefined ? match[1] : '';
};

// 检查是否需要增加缩进
const shouldIncreaseIndent = (lineContent: string): boolean => {
  const trimmed = lineContent.trim();
  
  // 检查是否以冒号结尾或其他需要增加缩进的情况
  const increaseKeywords = [
    ':',
    'def',
    'class',
    'if',
    'elif',
    'else',
    'for',
    'while',
    'try',
    'except',
    'finally',
    'with',
  ];
  
  if (trimmed.endsWith(':')) return true;
  
  for (const keyword of increaseKeywords) {
    if (trimmed.startsWith(keyword)) {
      const afterKeyword = trimmed.substring(keyword.length);
      if (afterKeyword === '' || /^\s/.test(afterKeyword)) {
        return true;
      }
    }
  }
  
  return false;
};

// 检查是否需要减少缩进
const shouldDecreaseIndent = (lineContent: string): boolean => {
  const trimmed = lineContent.trim();
  
  const decreaseKeywords = [
    'else',
    'elif',
    'except',
    'finally',
  ];
  
  for (const keyword of decreaseKeywords) {
    if (trimmed.startsWith(keyword)) {
      const afterKeyword = trimmed.substring(keyword.length);
      if (afterKeyword === '' || /^\s/.test(afterKeyword)) {
        return true;
      }
    }
  }
  
  return false;
};

// 处理Tab键
const handleTab = (event: KeyboardEvent) => {
  event.preventDefault();
  
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) return;
  
  const range = selection.getRangeAt(0);
  
  if (event.shiftKey) {
    // Shift+Tab 减少缩进
    removeIndentation();
  } else {
    // Tab 增加缩进
    const tabNode = document.createTextNode('    ');
    range.deleteContents();
    range.insertNode(tabNode);
    range.setStartAfter(tabNode);
    range.collapse(true);
    selection.removeAllRanges();
    selection.addRange(range);
    
    handleInput();
    syncScroll();
  }
};

// 移除缩进（改进版）
const removeIndentation = () => {
  const selection = window.getSelection();
  if (!selection || !editor.value) return;
  
  const range = selection.getRangeAt(0);
  
  // 只有在光标位于行首时才移除缩进
  if (range.startContainer.nodeType === Node.TEXT_NODE) {
    const textContent = range.startContainer.textContent || '';
    const startOffset = range.startOffset;
    
    // 检查是否在行首
    const textBeforeCursor = textContent.substring(0, startOffset);
    const lastNewlineIndex = textBeforeCursor.lastIndexOf('\n');
    const textFromLineStart = lastNewlineIndex >= 0 
      ? textBeforeCursor.substring(lastNewlineIndex + 1)
      : textBeforeCursor;
    
    // 检查行首是否有空格
    const leadingSpaces = textFromLineStart.match(/^\s*/)?.[0] || '';
    if (leadingSpaces.length > 0) {
      // 计算要删除的空格数（最多4个或到行首）
      const spacesToRemove = Math.min(4, leadingSpaces.length);
      
      // 创建新的范围来删除空格
      const deleteRange = document.createRange();
      deleteRange.setStart(range.startContainer, startOffset - spacesToRemove);
      deleteRange.setEnd(range.startContainer, startOffset);
      deleteRange.deleteContents();
      
      // 更新选区
      range.setStart(range.startContainer, startOffset - spacesToRemove);
      range.collapse(true);
      selection.removeAllRanges();
      selection.addRange(range);
      
      handleInput();
      syncScroll();
    }
  }
};

// 处理回车键（改进版）
const handleEnter = (event: KeyboardEvent) => {
  event.preventDefault();
  
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) return;
  
  const range = selection.getRangeAt(0);
  
  // 获取当前光标位置
  const cursorPos = getCursorPosition();
  const currentLineNumber = cursorPos.lineNumber;
  const currentLineContent = getLineContent(currentLineNumber);
  const currentIndent = getLineIndent(currentLineNumber);
  
  // 计算新行的缩进
  let newIndent = currentIndent;
  
  // 检查是否需要增加缩进
  if (shouldIncreaseIndent(currentLineContent)) {
    newIndent += '    '; // 增加4个空格
  }
  
  // 检查下一行是否需要减少缩进（仅在当前行不是最后一行时）
  const lines = code.value.split('\n');
  if (currentLineNumber < lines.length - 1) {
    const nextLineContent = getLineContent(currentLineNumber + 1);
    if (nextLineContent && shouldDecreaseIndent(nextLineContent)) {
      newIndent = newIndent.slice(0, -4); // 减少4个空格
      if (newIndent.length < 0) newIndent = '';
    }
  }
  
  // 插入换行和缩进
  const newLineText = '\n' + newIndent;
  const newLineNode = document.createTextNode(newLineText);
  range.deleteContents();
  range.insertNode(newLineNode);
  
  // 移动光标到新行
  range.setStartAfter(newLineNode);
  range.collapse(true);
  selection.removeAllRanges();
  selection.addRange(range);
  
  handleInput();
  syncScroll();
};

// 处理键盘事件
const handleKeydown = (event: KeyboardEvent) => {
  if (!editor.value || !editable.value) return;

  // Tab键处理
  if (event.key === 'Tab') {
    handleTab(event);
    return;
  }
  
  // 回车键处理 - 自动缩进
  if (event.key === 'Enter') {
    handleEnter(event);
    return;
  }
};

// 处理粘贴事件，清理格式
const handlePaste = (event: ClipboardEvent) => {
  if (!editable.value) {
    event.preventDefault();
    return;
  }
  
  event.preventDefault();
  
  const clipboardData = event.clipboardData;
  if (!clipboardData) return;
  
  const pastedText = clipboardData.getData('text/plain');
  const selection = window.getSelection();
  
  if (!selection || selection.rangeCount === 0) return;
  
  const range = selection.getRangeAt(0);
  range.deleteContents();
  
  // 插入纯文本
  const textNode = document.createTextNode(pastedText);
  range.insertNode(textNode);
  
  // 设置光标位置到插入文本的末尾
  range.setStartAfter(textNode);
  range.collapse(true);
  selection.removeAllRanges();
  selection.addRange(range);
  
  handleInput();
  syncScroll();
};

// 监听外部传入的值变化
watch(() => props.modelValue, (newValue) => {
  if (newValue !== undefined && newValue !== code.value) {
    code.value = newValue;
    if (editor.value) {
      editor.value.textContent = newValue;
    }
    highlightCode();
  }
});

// 监听代码变化
watch(code, () => {
  highlightCode();
}, { immediate: true });

// 监听可编辑状态变化
watch(editable, () => {
  if (editor.value) {
    editor.value.contentEditable = editable.value.toString();
  }
});

// 初始化
onMounted(() => {
  if (editor.value) {
    editor.value.textContent = code.value;
    editor.value.contentEditable = editable.value.toString();
    
    // 设置焦点
    if (editable.value) {
      editor.value.focus();
    }
    
    highlightCode();
  }
});
</script>

<style scoped>
.python-editor-modal {
  display: flex;
  flex-direction: column;
  height: 100%;
  /* 使用等宽字体族，确保英文字符对齐 */
  font-family: 'Consolas', 'Courier New', monospace, 'Microsoft YaHei', 'SimHei';
  font-size: 14px;
  background-color: #ffffff;
  border-radius: 8px;
  overflow: hidden;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e1e4e8;
}

.editor-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #24292e;
}

.controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 34px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #007bff;
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.editable-label {
  font-size: 12px;
  color: #586069;
}

.editor-wrapper {
  position: relative;
  flex: 1;
  min-height: 0;
}

.code-editor, .code-highlighter {
  margin: 0;
  padding: 16px;
  border: none;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  white-space: pre;
  overflow: auto;
  tab-size: 4;
  -moz-tab-size: 4;
  font-family: inherit;
  font-size: inherit;
  line-height: 1.5;
  /* 确保字体渲染一致，避免中英文字符宽度差异 */
  font-variant-ligatures: none;
  -webkit-font-variant-ligatures: none;
  text-rendering: optimizeSpeed;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* 强制使用等宽字体，确保字符对齐 */
  font-feature-settings: "tnum";
}

.code-editor {
  position: absolute;
  top: 0;
  left: 0;
  color: transparent;
  background: transparent;
  caret-color: #24292e;
  z-index: 2;
  outline: none;
  resize: none;
}

.code-highlighter {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
  pointer-events: none;
  overflow: hidden;
  background-color: transparent;
  color: #24292e;
}

.editor-footer {
  padding: 8px 16px;
  background-color: #f8f9fa;
  border-top: 1px solid #e1e4e8;
  font-size: 12px;
  display: flex;
  justify-content: space-between;
  color: #586069;
}

/* 确保Prism高亮样式正确应用 */
:deep(.token.comment) {
  color: #6a737d;
  font-style: italic;
}

:deep(.token.keyword) {
  color: #d73a49;
  font-weight: bold;
}

:deep(.token.string) {
  color: #032f62;
}

:deep(.token.function) {
  color: #6f42c1;
}

:deep(.token.number) {
  color: #005cc5;
}

:deep(.token.operator) {
  color: #d73a49;
}

:deep(.token.punctuation) {
  color: #24292e;
}

:deep(.token.builtin) {
  color: #e36209;
}

:deep(.token.class-name) {
  color: #6f42c1;
}
</style>