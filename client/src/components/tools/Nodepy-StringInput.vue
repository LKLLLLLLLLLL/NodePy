<template>
    <div 
        class="NodePyStringInputLayout nodes-innertool-border-radius" 
        :class="{disabled: disabled}"
    >
        <input 
            ref="inputEl"
            v-model="editText" 
            :disabled="disabled"
            type="text"
            @focus="startEdit"
            @blur="commitEdit"
            @keydown.enter="commitEdit"
            @keydown.esc="cancelEdit"
        />
    </div>
</template>

<script lang="ts" setup>
    import { ref, computed } from 'vue'
    const model = defineModel<string>()
    const emit = defineEmits(['updateValue'])
    const props = defineProps({
        disabled: {
            type: Boolean,
            default: false
        }
    })
    const editText = ref(model.value)
    const disabled = computed(() => props.disabled)
    const isEditing = ref(false)
    const inputEl = ref<HTMLInputElement>()


    const startEdit = () => {
        isEditing.value = true
    }

    const cancelEdit = () => {
        isEditing.value = false
        editText.value = model.value
        inputEl.value?.blur()
    }

    const commitEdit = () => {
        if(isEditing.value) {
            isEditing.value = false
            model.value = editText.value
            inputEl.value?.blur()
            emit('updateValue')
        }
    }
</script>

<style lang="scss" scoped>
    @use '../../common/style/global.scss';
    @use '../../common/style/node.scss';
    .NodePyStringInputLayout {
        width: 100%;
        height: 100%;
        outline: 1px solid #ccc;
        input {
            width: 100%;
            text-align: center;
            outline: none;
        }
    }
    .disabled {
        background: rgba(200, 200, 200, 0.3);
        input {
            cursor: not-allowed;
            opacity: 0.5;
        }
    }
</style>