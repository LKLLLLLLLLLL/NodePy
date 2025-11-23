<script lang="ts" setup>
    import { useFileStore } from '@/stores/fileStore'
    import { onMounted, onUnmounted, ref, computed } from 'vue'
    import Loading from '@/components/Loading.vue'
    import { type File } from '@/utils/api'

    const props = defineProps<{
        value: (string | number | boolean | File | any)
    }>()

    const fileStore = useFileStore()
    const loading = ref(true)
    const error = ref<string>('')
    let objectUrl: string | null = null

    // 判断是否是文件对象（类型守卫）
    const isFileObject = computed(() => {
        return (
            typeof props.value === 'object' &&
            props.value !== null &&
            'key' in props.value &&
            'filename' in props.value
        )
    })

    // 获取文件 key
    const fileKey = computed(() => {
        if (isFileObject.value) {
            return (props.value as File).key
        }
        return null
    })

    // 获取文件名
    const fileName = computed(() => {
        if (isFileObject.value) {
            return (props.value as File).filename
        }
        return 'file'
    })

    // 获取文件格式
    const fileFormat = computed(() => {
        if (isFileObject.value) {
            return (props.value as File).format.toLowerCase()
        }
        return 'unknown'
    })

    // 判断是否是图片文件
    const isImage = computed(() => {
        const format = fileFormat.value
        return format === 'png' || format === 'jpg' || format === 'jpeg'
    })

    // 判断是否是 PDF 文件
    const isPdf = computed(() => {
        return fileFormat.value === 'pdf'
    })

    // 判断是否是 CSV 文件
    const isCsv = computed(() => {
        return fileFormat.value === 'csv'
    })

    // MIME 类型映射
    function getMimeType(format: string): string {
        const mimeMap: Record<string, string> = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'csv': 'text/csv',
            'pdf': 'application/pdf'
        }
        return mimeMap[format.toLowerCase()] || 'application/octet-stream'
    }

    // 用于显示的图片或 PDF URL
    const displaySrc = ref<string>('')

    // CSV 数据
    const csvData = ref<string>('')

    onMounted(async () => {
        try {
            loading.value = true
            error.value = ''

            // 检查是否是文件对象
            if (!isFileObject.value || !fileKey.value) {
                error.value = '不是有效的文件对象或文件 key 不存在'
                console.warn('FileView: 接收到的不是文件对象', props.value)
                return
            }

            console.log('FileView: 开始加载文件')
            console.log('FileView: 文件 key:', fileKey.value)
            console.log('FileView: 文件格式:', fileFormat.value)
            console.log('FileView: 文件名:', fileName.value)

            // 从 fileStore 获取文件内容
            const content = await fileStore.getCacheContent(fileKey.value)

            console.log('FileView: 获取到内容')
            console.log('FileView: 内容类型:', typeof content)
            console.log('FileView: 内容是否为 Blob:', content instanceof Blob)

            if (!content) {
                error.value = '文件内容为空或加载失败'
                console.warn('FileView: 内容为空')
                return
            }

            let blob: Blob

            if (content instanceof Blob) {
                blob = content
                console.log('FileView: 内容已是 Blob，大小:', blob.size, '字节')
            } else if (content instanceof ArrayBuffer) {
                const mimeType = getMimeType(fileFormat.value)
                blob = new Blob([content], { type: mimeType })
                console.log('FileView: ArrayBuffer 已转换为 Blob，大小:', blob.size, '字节')
            } else {
                console.warn('FileView: 未知类型:', typeof content)
                const mimeType = getMimeType(fileFormat.value)
                blob = new Blob([String(content)], { type: mimeType })
            }

            if (!blob || blob.size === 0) {
                error.value = 'Blob 为空或大小为 0'
                console.warn('FileView: Blob 为空或大小为 0')
                return
            }

            // 根据文件类型处理
            if (isCsv.value) {
                // 读取 CSV 内容
                const text = await blob.text()
                csvData.value = text
                console.log('FileView: CSV 文件内容已读取')
            } else {
                // 图片和 PDF 创建 Object URL
                objectUrl = URL.createObjectURL(blob)
                displaySrc.value = objectUrl
                console.log('FileView: Object URL 已创建')
            }

            console.log('FileView: 文件加载成功')

        } catch (err) {
            error.value = `加载文件失败: ${err instanceof Error ? err.message : String(err)}`
            console.error('FileView 加载失败:', err)
        } finally {
            loading.value = false
        }
    })

    onUnmounted(() => {
        // 清理 Object URL
        if (objectUrl) {
            URL.revokeObjectURL(objectUrl)
            objectUrl = null
            console.log('FileView: Object URL 已清理')
        }
    })

    // 解析 CSV 数据为表格
    const csvTable = computed(() => {
        if (!csvData.value) {
            return { headers: [], rows: [] }
        }

        const lines = csvData.value.trim().split('\n')
        if (lines.length === 0) {
            return { headers: [], rows: [] }
        }

        const headerLine = lines[0]
        if (!headerLine) {
            return { headers: [], rows: [] }
        }

        const headers = headerLine.split(',').map(h => h.trim())
        const rows = lines.slice(1).map(line => {
            const cells = line.split(',').map(cell => cell.trim())
            const row: Record<string, string> = {}
            headers.forEach((header, index) => {
                row[header] = cells[index] || ''
            })
            return row
        })

        return { headers, rows }
    })
</script>

<template>
    <div class="file-view-container">
        <!-- 加载中 -->
        <div v-if="loading" class="file-loading">
            <Loading></Loading>
            <span>加载中...</span>
        </div>

        <!-- 错误提示 -->
        <div v-else-if="error" class="file-error">
            {{ error }}
        </div>

        <!-- 图片显示 -->
        <div v-else-if="isImage && displaySrc" class="image-view">
            <img
                :src="displaySrc"
                :alt="fileName"
                class="file-img"
                @error="() => { error = '图片加载失败'; console.error('FileView: img error') }"
                @load="console.log('FileView: 图片加载成功')"
            />
        </div>

        <!-- PDF 显示（使用 iframe）-->
        <div v-else-if="isPdf && displaySrc" class="pdf-view">
            <iframe
                :src="displaySrc"
                class="pdf-iframe"
                frameborder="0"
            ></iframe>
        </div>

        <!-- CSV 显示 -->
        <div v-else-if="isCsv && csvData" class="csv-view">
            <div v-if="csvTable.rows.length > 0" class="csv-table-wrapper">
                <table class="csv-table">
                    <thead>
                        <tr>
                            <th class="index-column">序号</th>
                            <th v-for="header in csvTable.headers" :key="header" class="csv-column">
                                {{ header }}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(row, rowIndex) in csvTable.rows" :key="rowIndex" class="csv-row">
                            <td class="index-column">{{ rowIndex + 1 }}</td>
                            <td v-for="header in csvTable.headers" :key="header" class="csv-column">
                                {{ row[header] || '-' }}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div v-else class="csv-empty">
                CSV 文件为空
            </div>
        </div>

        <!-- 无内容 -->
        <div v-else class="file-placeholder">
            无法显示该文件或文件为空
        </div>
    </div>
</template>

<style scoped lang="scss">
    .file-view-container {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        overflow: auto;
        background: #fafafa;
        padding: 12px;
        box-sizing: border-box;
    }

    .file-loading {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #606266;
        font-size: 14px;

        :deep(.el-icon) {
            font-size: 20px;
            animation: rotating 2s linear infinite;
        }
    }

    .file-error {
        color: #f56c6c;
        font-size: 14px;
        padding: 16px;
        background: #fef0f0;
        border-radius: 4px;
        border-left: 4px solid #f56c6c;
    }

    .image-view {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
    }

    .file-img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        border-radius: 6px;
        background: #fff;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    }

    .pdf-view {
        width: 100%;
        height: 100%;
        border-radius: 4px;
        overflow: hidden;
    }

    .pdf-iframe {
        width: 100%;
        height: 100%;
        border: none;
    }

    .csv-view {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        border-radius: 4px;
        overflow: hidden;
    }

    .csv-table-wrapper {
        flex: 1;
        overflow: auto;
        border: 1px solid #ebeef5;
        border-radius: 4px;
    }

    .csv-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        background: #fff;
    }

    .csv-table thead {
        position: sticky;
        top: 0;
        background: #f5f7fa;
        z-index: 1;
    }

    .csv-table th {
        padding: 12px 8px;
        text-align: left;
        border-bottom: 2px solid #ebeef5;
        font-weight: 600;
        color: #303133;
    }

    .csv-table td {
        padding: 10px 8px;
        border-bottom: 1px solid #ebeef5;
        color: #606266;
    }

    .index-column {
        width: 50px;
        min-width: 50px;
        text-align: center;
        background: #fafafa;
        font-weight: 500;
    }

    .csv-column {
        word-break: break-word;
        white-space: normal;
    }

    .csv-table tbody tr:hover td:not(.index-column) {
        background: #f0f9ff;
    }

    .csv-empty {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #909399;
        font-size: 14px;
    }

    .file-placeholder {
        color: #909399;
        font-size: 14px;
    }

    @keyframes rotating {
        0% {
            transform: rotate(0);
        }
        100% {
            transform: rotate(360deg);
        }
    }
</style>
