import { defineStore } from 'pinia';
import { ref } from 'vue';
export type Page = 'File'|'ProjectList'|'Home'|'Login'|'Example'|'Visitor';
export const usePageStore = defineStore('page', () => {
    const currentPage = ref<Page>('Home');
    function setCurrentPage(page:Page){
        currentPage.value = page;
    }
    return{
        currentPage,
        setCurrentPage
    }
});