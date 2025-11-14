import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useRouter } from 'vue-router'
export type Page = 'File'|'ProjectList'|'Home'|'Login'|'Example'|'Visitor';
export const usePageStore = defineStore('page', () => {
    const router = useRouter()
    const currentPage = ref<Page>('Home');

    function setCurrentPage(page:Page){
        currentPage.value = page;
    }

    function jumpToPage(){
        switch(currentPage.value){
            case('File'):
                router.push({
                    name: 'file'
                })
                break;
            case('Example'):
                router.push({
                    name: 'example'
                })
                break;
            case('Home'):
                router.push({
                    name: 'home'
                })
                break;
            case('ProjectList'):
                router.push({
                    name: 'project'
                })
                break;
            case('Visitor'):
                router.push({
                    name: 'visitor'
                })
                break;
            default:
                router.push({
                    name: 'home'
                })
                break;
        }
    }
    return{
        currentPage,
        jumpToPage,
        setCurrentPage
    }
});