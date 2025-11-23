<template>
    <div
        class="NodePyStringInputLayout nodes-innertool-border-radius"
        :class="{disabled: disabled}"
        :style="{width: width, height: height}"
        @click.stop
    >
        <input
            ref="inputEl"
            :placeholder="placeholder"
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
            default: 'auto'
        },
        width: {
            type: String,
            default: '100%'
        },
        placeholder: {
            type: String,
            default: '请输入...'
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
    @use '../../../common/global.scss' as *;
    @use '../../../common/node.scss' as *;
    @use './tools.scss' as *;
    .NodePyStringInputLayout {
        @include box-tools-style;
        font-size: $node-description-fontsize;
        input {
            @include tool-item-style;
            width: 100%;
            text-align: center;
            outline: none;
            &::placeholder {
                color: rgba(0,0,0,0.2);
            }
            cursor: text;
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
