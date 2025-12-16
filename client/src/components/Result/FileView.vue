<script lang="ts" setup>
import { useFileStore } from '@/stores/fileStore'
import { onMounted, onUnmounted, ref, computed, watch } from 'vue'
//@ts-ignore
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiDownload } from '@mdi/js';
import Loading from '@/components/Loading.vue'
import { type File, type TableView } from '@/utils/api'
import type { ResultType } from '@/stores/resultStore'
import * as Mammoth from 'mammoth'
import * as XLSX from 'xlsx'

// 导入新组件
import ShowPDF from './ShowFiles/ShowPDF.vue'
import ShowIMG from './ShowFiles/ShowIMG.vue'
import ShowCSV from './ShowFiles/ShowCSV.vue'
import ShowTXT from './ShowFiles/ShowTXT.vue'
import ShowWord from './ShowFiles/ShowWord.vue'
import ShowExcel from './ShowFiles/ShowExcel.vue'
import ShowJSON from './ShowFiles/ShowJSON.vue'

// 修改 props 定义，允许 null
const props = defineProps<{
    value: ResultType
}>()

const fileStore = useFileStore()
const loading = ref(false)
const error = ref<string>('')
let objectUrl: string | null = null

// PDF 分页相关状态
const currentPage = ref<number>(1)
const pageCount = ref<number>(0)

// TXT 分页相关状态
const txtLines = ref<string[]>([])
const txtCurrentPage = ref<number>(1)
const txtLinesPerPage = 50
const txtTotalPages = computed(() => Math.ceil(txtLines.value.length / txtLinesPerPage))

// Word 内容
const wordContent = ref<string>('')

// Excel 内容
const excelSheets = ref<any[]>([])

// JSON 内容
const jsonData = ref<any>(null)

// 性能优化：虚拟滚动相关
const maxRenderLines = 1000 // 最大渲染行数

// 类型守卫：检查是否是 File 类型
const isFile = computed(() => {
    return (
        props.value !== null &&
        typeof props.value === 'object' &&
        'key' in props.value &&
        'filename' in props.value &&
        'format' in props.value
    )
})

// 判断是否是有效的文件对象
const isValidFile = computed(() => {
    if (!isFile.value) return false
    const file = props.value as File
    return (
        file.key && // key 不能为空
        file.key !== 'loading' // 排除 loading 占位符
    )
})

// 获取文件 key
const fileKey = computed(() => {
    if (isValidFile.value) {
        return (props.value as File).key
    }
    return null
})

// 获取文件名
const fileName = computed(() => {
    if (isValidFile.value) {
        return (props.value as File).filename
    }
    return 'file'
})

// 获取文件格式
const fileFormat = computed(() => {
    if (isValidFile.value) {
        // 将 'word' 格式转换为 'docx' 以便统一处理
        const format = (props.value as File).format.toLowerCase()
        if (format === 'word') {
            return 'docx'  // 默认映射到 docx
        }
        return format
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

// 判断是否是 TXT 文件
const isTxt = computed(() => {
        return fileFormat.value === 'txt'
})

// 判断是否是 Word 文件
const isWord = computed(() => {
    const format = fileFormat.value
    return format === 'docx' || format === 'doc'
})

// 判断是否是 Excel 文件
const isXlsx = computed(() => {
    const format = fileFormat.value
    return format === 'xlsx' || format === 'xls'
})

// 判断是否是 JSON 文件
const isJson = computed(() => {
    return fileFormat.value === 'json'
})

// MIME 类型映射
function getMimeType(format: string): string {
    const mimeMap: Record<string, string> = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'csv': 'text/csv',
        'pdf': 'application/pdf',
        'txt': 'text/plain',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'doc': 'application/msword',
        'word': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // 添加对 word 格式的支持
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xls': 'application/vnd.ms-excel',
        'json': 'application/json'
    }
    return mimeMap[format.toLowerCase()] || 'application/octet-stream'
}

// 用于显示的图片或 PDF URL
const displaySrc = ref<string>('')

// CSV 数据
const csvData = ref<string>('')

// TXT 当前页内容
const txtCurrentPageContent = computed(() => {
    const start = (txtCurrentPage.value - 1) * txtLinesPerPage
    const end = start + txtLinesPerPage
    return txtLines.value.slice(start, end)
})

// TXT 分页 - 上一页
const txtPrevPage = () => {
    if (txtCurrentPage.value > 1) {
        txtCurrentPage.value--
    }
}

// TXT 分页 - 下一页
const txtNextPage = () => {
    if (txtCurrentPage.value < txtTotalPages.value) {
        txtCurrentPage.value++
    }
}

// TXT 分页 - 跳转到指定页
const txtGoToPage = (page: number) => {
    if (page >= 1 && page <= txtTotalPages.value) {
        txtCurrentPage.value = page
    }
}

// 加载文件的函数
const loadFile = async () => {
    // 重置状态
    loading.value = true
    error.value = ''
    if (objectUrl) {
        URL.revokeObjectURL(objectUrl)
        objectUrl = null
    }
    displaySrc.value = ''
    csvData.value = ''
    txtLines.value = []
    txtCurrentPage.value = 1
    wordContent.value = ''
    excelSheets.value = []
    jsonData.value = null

    // 重置PDF分页状态
    currentPage.value = 1
    pageCount.value = 0

    // 检查是否是有效的文件对象
    if (!isValidFile.value) {
        loading.value = false
        return
    }

    try {
        error.value = ''

        // 从 fileStore 获取文件内容
        const content = await fileStore.getCacheContent(fileKey.value!)

        if (!content) {
            error.value = '文件内容为空或加载失败'
            loading.value = false
            return
        }

        let blob: Blob

        if (content instanceof Blob) {
            blob = content
        } else if (content instanceof ArrayBuffer) {
            const mimeType = getMimeType(fileFormat.value)
            blob = new Blob([content], { type: mimeType })
        } else {
            const mimeType = getMimeType(fileFormat.value)
            blob = new Blob([String(content)], { type: mimeType })
        }

        if (!blob || blob.size === 0) {
            error.value = 'Blob 为空或大小为 0'
            loading.value = false
            return
        }

        // 根据文件类型处理
        if (isCsv.value) {
            // 处理 CSV 文件
            try {
                csvData.value = await blob.text()
            } catch (err) {
                error.value = `CSV 文件读取失败: ${err instanceof Error ? err.message : String(err)}`
            }
        } else if (isTxt.value) {
            // 处理 TXT 文件
            try {
                const text = await blob.text()
                txtLines.value = text.split('\n')
                txtCurrentPage.value = 1
            } catch (err) {
                error.value = `TXT 文件读取失败: ${err instanceof Error ? err.message : String(err)}`
            }
        // 在处理 Word 文件的部分，更新 options 配置
        } else if (isWord.value) {
        // 处理 Word 文件，增加样式保留
        try {
            const arrayBuffer = await blob.arrayBuffer()

            // 配置 Mammoth 以保留更多原始样式
            const options = {
                styleMap: [
                    // 标题样式映射
                    "p[style-name='Title'] => h1:fresh",
                    "p[style-name='Heading 1'] => h1:fresh",
                    "p[style-name='Heading 2'] => h2:fresh",
                    "p[style-name='Heading 3'] => h3:fresh",
                    "p[style-name='Heading 4'] => h4:fresh",
                    "p[style-name='Heading 5'] => h5:fresh",
                    "p[style-name='Heading 6'] => h6:fresh",

                    // 强调样式映射
                    "r[style-name='Strong'] => strong",
                    "r[style-name='Emphasis'] => em",
                    "r[style-name='Underline'] => u",
                    "r[style-name='Strikethrough'] => s",

                    // 列表样式映射
                    "p[style-name='List Paragraph'] => li:fresh",
                    "p[style-name='Caption'] => figcaption:fresh",

                    // 表格样式映射
                    "table => table",
                    "tr => tr",
                    "td => td",
                    "th => th",

                    // 更多样式映射
                    "p[style-name='Normal'] => p:fresh",
                    "r[style-name='Font Color'] => span",
                    "r[style-name='Background Color'] => span",
                    "p[style-name='Quote'] => blockquote:fresh",
                    "p[style-name='Code'] => pre:fresh",

                    // 上下标映射
                    "r[style-name='Superscript'] => sup",
                    "r[style-name='Subscript'] => sub",

                    // 更多文本样式映射
                    "r[style-name='Highlight'] => span",
                    "r[style-name='Bold'] => strong",
                    "r[style-name='Italic'] => em",

                    // 增加更多样式支持
                    "r[style-name='Double Underline'] => span.ql-double-underline",
                    "r[style-name='Wave Underline'] => span.ql-wave-underline",
                    "r[style-name='Dotted Underline'] => span.ql-dotted-underline",
                    "r[style-name='Dashed Underline'] => span.ql-dashed-underline"
                ],
                // 保留更多的原始格式信息
                includeDefaultStyleMap: true,
                // 增加对图片的处理
                convertImage: Mammoth.images.imgElement(function(image) {
                    return image.read("base64").then(function(imageBuffer) {
                        return {
                            src: "data:" + image.contentType + ";base64," + imageBuffer
                        };
                    });
                })
            }

            const result = await Mammoth.convertToHtml({ arrayBuffer }, options)
            wordContent.value = result.value
            } catch (err) {
                error.value = `Word 文件解析失败: ${err instanceof Error ? err.message : String(err)}`
            }
        } else if (isXlsx.value) {
            // 处理 Excel 文件
            try {
                const arrayBuffer = await blob.arrayBuffer()
                const workbook = XLSX.read(arrayBuffer, { type: 'array' })

                // 提取所有工作表数据
                const sheets: any[] = []
                workbook.SheetNames.forEach(sheetName => {
                    const worksheet = workbook.Sheets[sheetName]
                    // 确保 worksheet 存在后再处理
                    if (worksheet) {
                        // 修复 XLSX.utils.sheet_to_json 类型问题
                        const data: any[] = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: "" })
                        sheets.push({
                            name: sheetName,
                            data: data
                        })
                    }
                })
                excelSheets.value = sheets
            } catch (err) {
                error.value = `Excel 文件解析失败: ${err instanceof Error ? err.message : String(err)}`
            }
        } else if (isJson.value) {
            // 处理 JSON 文件
            try {
                const text = await blob.text()
                jsonData.value = JSON.parse(text)
            } catch (err) {
                error.value = `JSON 文件解析失败: ${err instanceof Error ? err.message : String(err)}`
            }
        } else {
            // 图片和 PDF 创建 Object URL
            objectUrl = URL.createObjectURL(blob)
            displaySrc.value = objectUrl
        }

    } catch (err) {
        error.value = `加载文件失败: ${err instanceof Error ? err.message : String(err)}`
    } finally {
        loading.value = false
    }
}

// 监听 props.value 变化
watch(() => props.value, loadFile, { immediate: true })

onUnmounted(() => {
    // 清理 Object URL
    if (objectUrl) {
        URL.revokeObjectURL(objectUrl)
        objectUrl = null
    }
})

// 图片加载错误处理
const handleImgError = () => {
    error.value = '图片加载失败'
    console.error('FileView: img error')
}

// 图片加载成功处理
const handleImgLoad = () => {
    console.log('FileView: 图片加载成功')
}

// 是否可以下载（文件预览时显示下载）
const canDownload = computed(() => {
    // isFile 表示 props.value 具有文件结构
    if (!isFile.value) return false
    // 如果文件有效且有 key，则可下载
    if (isValidFile.value) return true
    // 或者当已有可展示的内容时（如 displaySrc/csv/txt/word/excel/json），也允许下载
    if (displaySrc.value) return true
    if (csvData.value) return true
    if (txtLines.value.length > 0) return true
    if (wordContent.value) return true
    if (excelSheets.value.length > 0) return true
    if (jsonData.value) return true
    return false
})

// 下载当前文件（优先使用 key，如果没有则调用 downloadCurrentFile）
const handleDownloadFile = async () => {
    try {
        if (isValidFile.value && fileKey.value) {
            await fileStore.downloadFile(fileKey.value, fileName.value)
        } else {
            // 回退到 downloadCurrentFile，fileStore 内部会处理当前文件名
            await fileStore.downloadCurrentFile()
        }
    } catch (err) {
        console.error('File download failed', err)
    }
}
</script>

<template>
    <div class="file-view-container">
        <div class="file-toolbar">
            <div class="file-title">{{ fileName }}</div>
            <div class="file-actions">
                <button v-if="isValidFile" class="button download" @click="handleDownloadFile">
                    <svg-icon type="mdi" :path="mdiDownload" :size="18"></svg-icon>
                </button>
            </div>
        </div>
        <!-- 加载中 -->
        <div v-if="loading" class="file-loading">
            <Loading></Loading>
        </div>

        <!-- 错误提示 -->
        <div v-else-if="error" class="file-error">
            {{ error }}
        </div>

        <!-- 图片显示 -->
        <ShowIMG
            v-else-if="isImage && displaySrc"
            :src="displaySrc"
            :alt="fileName"
            :on-error="handleImgError"
            :on-load="handleImgLoad"
        />

        <!-- PDF 显示 -->
        <ShowPDF
            v-else-if="isPdf && displaySrc"
            :src="displaySrc"
        />

        <!-- CSV 显示 -->
        <ShowCSV
            v-else-if="isCsv && csvData"
            :data="csvData"
        />

        <!-- TXT 显示 -->
        <ShowTXT
            v-else-if="isTxt && txtLines.length > 0"
            :data="txtLines.join('\n')"
        />

        <!-- Word 显示 -->
        <ShowWord
            v-else-if="isWord && wordContent"
            :content="wordContent"
        />

        <!-- Excel 显示 -->
        <ShowExcel
            v-else-if="isXlsx && excelSheets.length > 0"
            :sheets="excelSheets"
        />

        <!-- JSON 显示 -->
        <ShowJSON
            v-else-if="isJson && jsonData"
            :data="jsonData"
        />
    </div>
</template>

<style scoped lang="scss">
@use '@/common/global.scss' as *;

.file-view-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    background: $background-color;
    border-radius: 10px;
    // padding: 16px;
    box-sizing: border-box;
}

.file-toolbar{
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding: 8px 12px;
    padding-top: 0px;
    padding-left: 4px;
    padding-right: 4px;
    gap: 8px;
}

.file-title{
    font-weight:600;
}

.button.download{
    display: flex;
    justify-content: center;
    align-items: center;
}

.file-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 12px;
    color: #909399;
    font-size: 14px;
}

.file-error {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: $error-message-color;
    font-size: 14px;
    padding: 16px;
    text-align: center;
    background: $stress-background-color;
    border-radius: 10px;
    margin: 16px;
    @include controller-style;
}
</style>
