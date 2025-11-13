import type { ProjNodeError } from "@/utils/api"
import { useVueFlow } from "@vue-flow/core"
import type { Ref } from "vue"

const {getEdges} = useVueFlow('main')

export const handleValidationError = (nodeId: string, err: ProjNodeError | null | undefined, errMsg: Ref<string[]>, ...handleErrObj: any[]) => {
    errMsg.value = []   //  reset errMsg
    getEdges.value.filter(e => e.target === nodeId).forEach(e => { e.class = '' })  //  reset classname
    handleErrObj.forEach((v) => {
        v.value.value = false
    })  //  reset handleErrObj
    if(!err) return
    if(err.type === 'validation') {
        const inputHandles = new Set(err.inputs)
        getEdges.value.forEach(e => {
            if(e.target === nodeId && inputHandles.has(e.targetHandle!)) {
                e.class= 'error-edge'
                console.log('error-edge')
            }
        })
        handleErrObj.forEach((v) => {
            if(inputHandles.has(v.value.handleId)) {
                v.value.value = true
            }
        })
        errMsg.value = err.message as string[]
    }
}

export const handleParamError = (hasParamerr: Ref<boolean>, err: ProjNodeError | null | undefined, errMsg: Ref<string[]>) => {
    errMsg.value = []
    hasParamerr.value = false
    if(!err) return
    if(err.type === 'param') {
        hasParamerr.value = true
        errMsg.value = err.message as string[]
    }
}

export const handleExecError = (err: ProjNodeError | null | undefined, errMsg: Ref<string[]>) => {
    errMsg.value = []
    if(!err) return
    if(err.type === 'execution') {
        errMsg.value = [err.message as string]
    }
}