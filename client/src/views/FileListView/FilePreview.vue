<script lang="ts" setup>
    import { ref,computed } from 'vue';
    import { useFileStore } from '@/stores/fileStore';
    import { FileItem } from '@/utils/api';
    import ShowCSV from './ShowCSV.vue';
    import ShowIMG from './ShowIMG.vue';
    import ShowPDF from './ShwoPDF.vue';

    const fileStore = useFileStore();

    const currentFile = computed(()=>fileStore.getCurrentFile());
    const currentFileType = computed(()=>{
        switch(currentFile.value.format){
            case(FileItem.format.CSV):
                return 'CSV';
            case(FileItem.format.PDF):
                return 'PDF';
            case(FileItem.format.JPG||FileItem.format.PNG):
                return 'IMG';
        }
    })

</script>
<template>
    <div class="filepreview-container">
        <div class="csv-container" v-if="currentFileType=='CSV'">
            <ShowCSV :file="currentFile"></ShowCSV>
        </div>
        <div class="image-container" v-else-if="currentFileType=='IMG'">
            <ShowIMG :file="currentFile"></ShowIMG>
        </div>
        <div class="pdf-container" v-else>
            <ShowPDF :file="currentFile"></ShowPDF>
        </div>
    </div>
</template>
<style lang="scss" scoped>

</style>