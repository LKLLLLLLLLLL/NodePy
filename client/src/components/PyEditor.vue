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
import { ref, computed, onMounted, watch } from 'vue';

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

// 处理输入
const handleInput = () => {
  if (editor.value) {
    const newCode = editor.value.textContent || '';
    code.value = newCode;
    emit('update:modelValue', newCode);
    highlightCode();
  }
};

// 获取当前光标位置的行号
const getCurrentLineNumber = (): number => {
  if (!editor.value) return 0;
  
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) return 0;
  
  const range = selection.getRangeAt(0);
  const preElement = editor.value;
  
  // 创建一个范围，从pre元素开始到光标位置
  const rangeToCursor = document.createRange();
  rangeToCursor.setStart(preElement, 0);
  rangeToCursor.setEnd(range.startContainer, range.startOffset);
  
  // 计算这个范围内的换行符数量
  const textToCursor = rangeToCursor.toString();
  const lineCount = (textToCursor.match(/\n/g) || []).length;
  
  return lineCount;
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

// 处理Backspace键 - 自动删除缩进
const handleBackspace = (event: KeyboardEvent) => {
  if (!editor.value || !editable.value) return false;

  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) return false;

  const range = selection.getRangeAt(0);
  const startOffset = range.startOffset;

  // 只在行首处理
  if (startOffset === 0) {
    const startContainer = range.startContainer;
    
    if (startContainer.nodeType === Node.TEXT_NODE) {
      const currentLineNumber = getCurrentLineNumber();
      const currentLineContent = getLineContent(currentLineNumber);
      const currentIndent = getLineIndent(currentLineNumber);

      // 如果当前行有缩进
      if (currentIndent.length > 0) {
        event.preventDefault();

        // 计算要删除的空格数（最多4个或整行缩进）
        const spacesToRemove = Math.min(4, currentIndent.length);

        // 删除缩进
        const newLineContent = currentLineContent.substring(spacesToRemove);
        const lines = code.value.split('\n');
        lines[currentLineNumber] = newLineContent;
        code.value = lines.join('\n');

        // 更新编辑器内容
        if (editor.value) {
          editor.value.textContent = code.value;

          // 重新设置光标位置
          setTimeout(() => {
            if (!editor.value) return;
            
            const walker = document.createTreeWalker(
              editor.value,
              NodeFilter.SHOW_TEXT,
              null
            );

            let node = walker.nextNode();
            let position = 0;
            const targetPosition = lines.slice(0, currentLineNumber).join('\n').length + 
                                  (currentLineNumber > 0 ? currentLineNumber : 0);

            while (node) {
              const nodeLength = node.textContent?.length || 0;
              if (position + nodeLength >= targetPosition) {
                const offsetInNode = targetPosition - position;
                const newRange = document.createRange();
                newRange.setStart(node, offsetInNode);
                newRange.collapse(true);
                
                selection.removeAllRanges();
                selection.addRange(newRange);
                break;
              }
              position += nodeLength;
              node = walker.nextNode();
            }
          }, 0);
        }

        handleInput();
        syncScroll();
        return true;
      }
    }
  } 
  // 如果光标在文本中间但前面有空格
  else if (range.startContainer.nodeType === Node.TEXT_NODE) {
    const textContent = range.startContainer.textContent || '';
    
    // 检查光标前是否有连续的空格
    let spacesBeforeCursor = 0;
    for (let i = startOffset - 1; i >= 0 && i >= startOffset - 4; i--) {
      if (textContent[i] === ' ') {
        spacesBeforeCursor++;
      } else {
        break;
      }
    }
    
    // 如果光标前有空格，则删除这些空格
    if (spacesBeforeCursor > 0) {
      event.preventDefault();
      
      const newRange = document.createRange();
      newRange.setStart(range.startContainer, startOffset - spacesBeforeCursor);
      newRange.setEnd(range.startContainer, startOffset);
      newRange.deleteContents();
      
      // 更新选区
      range.setStart(range.startContainer, startOffset - spacesBeforeCursor);
      range.collapse(true);
      selection.removeAllRanges();
      selection.addRange(range);
      
      handleInput();
      syncScroll();
      return true;
    }
  }

  return false;
};

// 处理键盘事件
const handleKeydown = (event: KeyboardEvent) => {
  if (!editor.value || !editable.value) return;

  // Backspace键处理
  if (event.key === 'Backspace') {
    if (handleBackspace(event)) {
      event.preventDefault();
      return;
    }
  }

  // Tab键处理
  if (event.key === 'Tab') {
    event.preventDefault();
    
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;
    
    const range = selection.getRangeAt(0);
    
    if (event.shiftKey) {
      // Shift+Tab 减少缩进
      removeIndentation(range);
    } else {
      // Tab 增加缩进
      const tabNode = document.createTextNode('    ');
      range.insertNode(tabNode);
      range.setStartAfter(tabNode);
      range.collapse(true);
      selection.removeAllRanges();
      selection.addRange(range);
    }
    
    handleInput();
    syncScroll();
    return;
  }
  
  // 回车键处理 - 自动缩进
  if (event.key === 'Enter') {
    event.preventDefault();
    
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;
    
    const range = selection.getRangeAt(0);
    
    // 获取当前行号
    const currentLineNumber = getCurrentLineNumber();
    const currentLineContent = getLineContent(currentLineNumber);
    const currentIndent = getLineIndent(currentLineNumber);
    
    // 计算新行的缩进
    let newIndent = currentIndent;
    
    // 检查是否需要增加缩进
    if (shouldIncreaseIndent(currentLineContent)) {
      newIndent += '    '; // 增加4个空格
    }
    
    // 检查下一行是否需要减少缩进
    const nextLineContent = getLineContent(currentLineNumber + 1);
    if (nextLineContent && shouldDecreaseIndent(nextLineContent)) {
      newIndent = newIndent.slice(0, -4); // 减少4个空格
      if (newIndent.length < 0) newIndent = '';
    }
    
    // 插入换行和缩进
    const newLineText = '\n' + newIndent;
    const newLineNode = document.createTextNode(newLineText);
    range.insertNode(newLineNode);
    
    // 移动光标到新行
    range.setStartAfter(newLineNode);
    range.collapse(true);
    selection.removeAllRanges();
    selection.addRange(range);
    
    handleInput();
    syncScroll();
  }
};

// 移除缩进
const removeIndentation = (range: Range) => {
  const selection = window.getSelection();
  if (!selection) return;
  
  const startContainer = range.startContainer;
  const startOffset = range.startOffset;
  
  // 如果是文本节点，检查前面的空格
  if (startContainer.nodeType === Node.TEXT_NODE) {
    const textContent = startContainer.textContent || '';
    let spacesToRemove = 0;
    
    // 查找前面的空格
    for (let i = startOffset - 1; i >= 0 && spacesToRemove < 4; i--) {
      if (textContent[i] === ' ') {
        spacesToRemove++;
      } else {
        break;
      }
    }
    
    if (spacesToRemove > 0) {
      // 删除空格
      const newRange = document.createRange();
      newRange.setStart(startContainer, startOffset - spacesToRemove);
      newRange.setEnd(startContainer, startOffset);
      newRange.deleteContents();
      
      // 更新选区
      range.setStart(startContainer, startOffset - spacesToRemove);
      range.collapse(true);
      selection.removeAllRanges();
      selection.addRange(range);
    }
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
  
  // 设置光标位置
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
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
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