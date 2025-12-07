<script lang="ts" setup>
    import { computed, ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
    import Loading from '@/components/Loading.vue'
    import type { ResultType } from '@/stores/resultStore';
    
    const props = defineProps<{
        value: ResultType
    }>()

    // 添加loading和error状态
    const loading = ref(false)
    const error = ref<string>('')
    // 添加显示完整字符串的状态
    const showFullString = ref(false)
    
    // 虚拟滚动相关状态
    const containerRef = ref<HTMLElement | null>(null)
    const visibleLines = ref<string[]>([])
    const allLines = ref<string[]>([])
    const startIndex = ref(0)
    const endIndex = ref(0)
    const lineHeight = ref(20) // 默认行高
    const containerHeight = ref(0)
    const scrollTop = ref(0)
    const visibleCount = ref(0)
    const bufferCount = ref(5) // 减少缓冲区行数
    const totalHeight = ref(0) // 总高度
    
    // 防抖定时器
    let resizeTimer: number | null = null;
    let scrollTimer: number | null = null;

    // 格式化日期时间显示的函数 - 转化为年月日时分秒，不需要其他字符
    const formatDateTime = (dateTimeString: string): string => {
        try {
            const date = new Date(dateTimeString);
            // 检查日期是否有效
            if (isNaN(date.getTime())) {
                return dateTimeString; // 如果无效，返回原始字符串
            }

            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const seconds = String(date.getSeconds()).padStart(2, '0');
            
            return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
        } catch (e) {
            // 如果解析失败，返回原始字符串
            return dateTimeString;
        }
    }

    // 格式化值的显示
    const displayValue = computed(() => {
        if (props.value === null || props.value === undefined) {
            return '无值'
        }
        
        if (typeof props.value === 'boolean') {
            return props.value ? 'True' : 'False'
        }
        
        if (typeof props.value === 'number') {
            // 如果是小数，保留3位小数
            return typeof props.value === 'number' && props.value % 1 !== 0 
                ? props.value.toFixed(3) 
                : String(props.value)
        }
        
        if (typeof props.value === 'string') {
            // 检查是否为 Datetime 类型的 ISO 格式字符串
            // ISO 8601 格式通常包含 T 和时区信息
            if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(props.value)) {
                return formatDateTime(props.value);
            }
            return props.value
        }

        // 对于对象类型，检查是否为 Datetime（在传输中会是字符串）
        // 这里处理可能的对象形式（如果有的话）
        if (typeof props.value === 'object') {
            // @ts-ignore - 这是为了处理可能的对象形式
            if (props.value.type === 'Datetime' && typeof props.value.value === 'string') {
                // @ts-ignore
                return formatDateTime(props.value.value);
            }
        }
        
        // 其他类型转为字符串
        return String(props.value)
    })

    // 获取值的类型标签
    const valueType = computed(() => {
        if (props.value === null || props.value === undefined) {
            return 'null'
        }
        if (typeof props.value === 'boolean') {
            return 'bool'
        }
        if (typeof props.value === 'number') {
            return Number.isInteger(props.value) ? 'int' : 'float'
        }
        // 检查是否为 Datetime 类型的字符串
        if (typeof props.value === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(props.value)) {
            return 'datetime'
        }
        // 检查是否为 Datetime 对象
        if (typeof props.value === 'object') {
            // @ts-ignore
            if (props.value.type === 'Datetime') {
                return 'datetime'
            }
        }
        return typeof props.value
    })
    
    // 检查是否为布尔值
    const isBoolean = computed(() => {
        return typeof props.value === 'boolean';
    });
    
    // 检查是否为超长字符串
    const isLongString = computed(() => {
        if (typeof props.value === 'string') {
            return props.value.length > 1000; // 超过1000字符认为是超长字符串
        }
        return false;
    });
    
    // 截断超长字符串用于显示
    const truncatedDisplayValue = computed(() => {
        const value = displayValue.value;
        if (typeof value === 'string' && value.length > 1000) {
            return value.substring(0, 1000) + '...'; // 截断并添加省略号
        }
        return value;
    });
    
    // 完整字符串用于显示
    const fullDisplayValue = computed(() => {
        return displayValue.value;
    });
    
    // 切换显示完整字符串
    const toggleFullString = () => {
        showFullString.value = !showFullString.value;
        if (showFullString.value) {
            nextTick(() => {
                initVirtualScroll();
            });
        }
    };
    
    // 初始化虚拟滚动
    const initVirtualScroll = async () => {
        if (!containerRef.value || !isLongString.value || !showFullString.value) return;
        
        try {
            // 将完整字符串按行分割
            allLines.value = fullDisplayValue.value.split('\n');
            totalHeight.value = allLines.value.length * lineHeight.value;
            
            // 等待DOM更新后再获取容器高度
            await nextTick();
            
            if (!containerRef.value) return;
            
            // 计算容器高度和可见行数
            containerHeight.value = containerRef.value.clientHeight;
            visibleCount.value = Math.ceil(containerHeight.value / lineHeight.value) || 1;
            
            // 设置初始可见范围
            startIndex.value = 0;
            endIndex.value = Math.min(visibleCount.value + bufferCount.value, allLines.value.length);
            
            // 更新可见行
            updateVisibleLines();
            
            // 清理之前的事件监听器
            containerRef.value.removeEventListener('scroll', handleScroll);
            
            // 添加滚动事件监听器，使用passive选项提高性能
            containerRef.value.addEventListener('scroll', handleScroll, { passive: true });
        } catch (err) {
            console.error('初始化虚拟滚动失败:', err);
        }
    };
    
    // 更新可见行
    const updateVisibleLines = () => {
        if (allLines.value.length === 0) return;
        visibleLines.value = allLines.value.slice(startIndex.value, endIndex.value);
    };
    
    // 处理滚动事件 - 使用节流优化性能
    const handleScroll = (e: Event) => {
        if (!isLongString.value || !showFullString.value || !containerRef.value) return;
        
        // 使用节流而不是防抖，确保滚动的流畅性
        if (scrollTimer) return;
        
        scrollTimer = requestAnimationFrame(() => {
            try {
                const target = e.target as HTMLElement;
                scrollTop.value = target.scrollTop;
                
                // 计算新的开始索引
                const newStartIndex = Math.max(0, Math.floor(scrollTop.value / lineHeight.value));
                const newEndIndex = Math.min(
                    newStartIndex + visibleCount.value + bufferCount.value,
                    allLines.value.length
                );
                
                // 只有当索引发生变化时才更新
                if (newStartIndex !== startIndex.value || newEndIndex !== endIndex.value) {
                    startIndex.value = Math.max(0, newStartIndex - bufferCount.value);
                    endIndex.value = newEndIndex;
                    updateVisibleLines();
                }
            } catch (err) {
                console.error('处理滚动事件失败:', err);
            } finally {
                scrollTimer = null;
            }
        });
    };
    
    // 处理窗口大小变化 - 使用更低频率的更新
    const handleWindowResize = () => {
        if (!containerRef.value || !isLongString.value || !showFullString.value) return;
        
        // 清除之前的resize定时器
        if (resizeTimer) {
            clearTimeout(resizeTimer);
        }
        
        // 使用更大的防抖延迟来减少resize事件的影响
        resizeTimer = window.setTimeout(() => {
            try {
                // 只有当容器确实发生变化时才更新
                const newContainerHeight = containerRef.value!.clientHeight;
                if (newContainerHeight !== containerHeight.value) {
                    containerHeight.value = newContainerHeight;
                    const newVisibleCount = Math.ceil(containerHeight.value / lineHeight.value) || 1;
                    
                    // 如果可见行数发生变化，更新显示
                    if (newVisibleCount !== visibleCount.value) {
                        visibleCount.value = newVisibleCount;
                        endIndex.value = Math.min(startIndex.value + visibleCount.value + bufferCount.value, allLines.value.length);
                        updateVisibleLines();
                    }
                }
            } catch (err) {
                console.error('处理窗口大小变化失败:', err);
            }
        }, 0); // 增加到200ms防抖延迟
    };
    
    // 监听showFullString变化，确保在切换时正确初始化
    watch(showFullString, (newVal) => {
        if (newVal) {
            // 使用微任务确保DOM完全渲染后再初始化
            queueMicrotask(() => {
                initVirtualScroll();
            });
        }
    });
    
    // 监听value变化，确保在数据更新时重新初始化
    watch(() => props.value, () => {
        if (showFullString.value) {
            // 使用微任务确保DOM完全渲染后再初始化
            queueMicrotask(() => {
                initVirtualScroll();
            });
        }
    });
    
    // 组件挂载时添加事件监听器
    onMounted(() => {
        window.addEventListener('resize', handleWindowResize, { passive: true });
    });
    
    // 组件卸载时清理
    onUnmounted(() => {
        window.removeEventListener('resize', handleWindowResize);
        if (containerRef.value) {
            containerRef.value.removeEventListener('scroll', handleScroll);
        }
        // 清理定时器
        if (resizeTimer) {
            clearTimeout(resizeTimer);
        }
        if (scrollTimer) {
            cancelAnimationFrame(scrollTimer);
        }
    });
</script>
<template>
    <div class='value-view-container'>
        <!-- 加载中 -->
        <div v-if="loading" class="value-loading">
            <Loading></Loading>
            <span>加载中...</span>
        </div>

        <!-- 错误提示 -->
        <div v-else-if="error" class='value-error'>
            {{ error }}
        </div>

        <!-- 正常显示 -->
        <div v-else>
            <div class='value-header'>
                <span class='value-type'>{{ valueType }}</span>
            </div>
            <div class='value-content-wrapper'>
                <div class='value-content' :class="{ 'boolean-true': isBoolean && value === true, 'boolean-false': isBoolean && value === false }">
                    <!-- 对于超长字符串，根据状态决定显示截断版本还是完整版本 -->
                    <span v-if="isLongString && !showFullString">{{ truncatedDisplayValue }}</span>
                    <div v-else-if="isLongString && showFullString" class="full-string-container" ref="containerRef">
                        <!-- 虚拟滚动实现 -->
                        <div class="virtual-scroll-padding" :style="{ height: `${startIndex * lineHeight}px` }"></div>
                        <div class="virtual-scroll-content">
                            <div 
                                v-for="(line, index) in visibleLines" 
                                :key="`${startIndex + index}`" 
                                class="line"
                                :style="{ height: `${lineHeight}px`, lineHeight: `${lineHeight}px` }"
                            >
                                {{ line }}
                            </div>
                        </div>
                        <div class="virtual-scroll-padding" :style="{ height: `${Math.max(0, (allLines.length - endIndex) * lineHeight)}px` }"></div>
                    </div>
                    <span v-else>{{ displayValue }}</span>
                </div>
            </div>
            <!-- 对于超长字符串，添加提示信息和切换按钮 -->
            <div v-if="isLongString" class="long-string-controls">
                <div class="long-string-hint">
                    内容长度: {{ fullDisplayValue.length }} 字符, {{ allLines.length }} 行
                </div>
                <button @click="toggleFullString" class="toggle-full-string-btn">
                    {{ showFullString ? '收起' : '展开完整内容' }}
                </button>
            </div>
        </div>
    </div>
</template>
<style scoped lang="scss">
    .value-view-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
        padding: 16px;
        box-sizing: border-box;
        background: #fafafa;
        border-radius: 4px;
    }

    .value-loading {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
        color: #909399;
        font-size: 14px;
    }

    .value-error {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #f56c6c;
        background: #fef0f0;
        border: 1px solid #fde2e2;
        border-radius: 4px;
        font-size: 14px;
        padding: 16px;
        margin: 16px;
    }

    .value-header {
        margin-bottom: 12px;
        font-size: 12px;
        color: #909399;
    }

    .value-content-wrapper {
        flex: 1;
        overflow: auto;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .value-content {
        font-size: 32px;
        font-weight: 500;
        color: #303133;
        word-break: break-all;
        text-align: center;
        line-height: 1.6;
        padding: 16px;
        max-width: 100%;
        box-sizing: border-box;
    }
    
    .boolean-true {
        color: #67c23a; // 绿色表示 True
        font-weight: bold;
    }
    
    .boolean-false {
        color: #f56c6c; // 红色表示 False
        font-weight: bold;
    }
    
    .full-string-container {
        text-align: left;
        font-size: 14px;
        width: 100%;
        height: 100%;
        overflow-y: auto;
        position: relative;
        background-color: #fff;
        border: 1px solid #ebeef5;
        border-radius: 4px;
        box-sizing: border-box;
        /* 移除硬件加速以避免影响窗口拖动 */
    }
    
    .virtual-scroll-padding {
        width: 100%;
    }
    
    .virtual-scroll-content {
        width: 100%;
    }
    
    .line {
        padding: 2px 10px;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    
    .long-string-controls {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        margin-top: 8px;
    }
    
    .long-string-hint {
        font-size: 12px;
        color: #909399;
        padding: 4px;
        background: #f5f5f5;
        border-radius: 4px;
    }
    
    .toggle-full-string-btn {
        padding: 6px 12px;
        background: #409eff;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        
        &:hover {
            background: #66b1ff;
        }
    }
</style>