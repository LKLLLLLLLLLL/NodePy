import { ref } from "vue"
import { defineStore } from "pinia"

export const useGraphStore = defineStore('graph', () => {
    const vueFlowInstance = ref<any>({})
    return { vueFlowInstance }
})