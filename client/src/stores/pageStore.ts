import { defineStore } from 'pinia';
import { ref } from 'vue';
export type Page = 'File'|'Program'|'Home'|'Login'
export const usePageStore = defineStore('page', () => {
    const currentPage = ref<Page>('Program');
    function setCurrentPage(page:Page){
        currentPage.value = page;
    }
    return{
        currentPage,
        setCurrentPage
    }
});