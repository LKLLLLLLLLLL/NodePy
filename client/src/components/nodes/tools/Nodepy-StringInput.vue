<template>
    <div 
        class="NodePyStringInputLayout nodes-innertool-border-radius" 
        :class="{disabled: disabled}"
        :style="{width: width, height: height}"
        @click.stop
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
        },
        height: {
            type: String,
            default: '100%'
        },
        width: {
            type: String,
            default: '100%'
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
    @use '../../../common/global.scss';
    @use '../../../common/node.scss';
    .NodePyStringInputLayout {
        border: 1.5px solid #ccc;
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