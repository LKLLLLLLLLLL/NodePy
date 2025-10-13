import { ref } from "vue";
import { defineStore } from "pinia";

export const useLayoutStore = defineStore('layout', () => {
    const showNodeSelector = ref(false);
    const showProperty = ref(false);
    const showResult = ref(false);
    const showGraph = ref(false);

    return {
        showNodeSelector,
        showProperty,
        showResult,
        showGraph
    };
});