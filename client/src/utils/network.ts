import { taskManager, TaskCancelledError } from './task'
import type { Project, TaskResponse } from './api'
import { Mutex } from 'async-mutex'
import { autoCaptureMinimap } from '@/utils/GraphCapture/minimapCapture'
import { useVueFlow } from '@vue-flow/core'
import { getProject, writeBackVueFLowProject } from './projectConvert'
import AuthenticatedServiceFactory from './AuthenticatedServiceFactory'
import { useResultStore } from '@/stores/resultStore'


const mutex = new Mutex()
const {vueFlowRef} = useVueFlow('main')
const authService = AuthenticatedServiceFactory.getService()
const resultStore = useResultStore()


const syncProject = (p: Project, graphStore: any) => {
    return new Promise<Project>(async (resolve, reject) => {
        let taskResponse: TaskResponse | undefined


        const release = await mutex.acquire()
        p.updated_at = Date.now()
        graphStore.project.updated_at = p.updated_at    //  update_at should writeback immediately
        graphStore.is_syncing = true
        graphStore.syncing_err_msg= ''


        try {
            const thumbBase64 = await autoCaptureMinimap(vueFlowRef.value)
            if (thumbBase64) {
                const pureBase64 = thumbBase64.startsWith('data:image')
                    ? thumbBase64.split(',')[1]
                    : thumbBase64

                p.thumb = pureBase64
                graphStore.project.thumb = p.thumb  //  thumb should writeback immediately
            }
        }catch(err) {
            const errMsg = err && typeof err === 'object' && 'message' in err
            ? String(err.message)
            : '无法连接到服务器，请检查网络或联系管理员。'
            graphStore.syncing_err_msg = errMsg
            reject(err)
        }

        try {
            if (taskManager.hasActiveTask()) {
                await taskManager.cancel()
            }
            taskResponse = await authService.syncProjectApiProjectSyncPost(p)
        }catch(err) {
            const errMsg = err && typeof err === 'object' && 'message' in err
            ? String(err.message)
            : '无法连接到服务器，请检查网络或联系管理员。'
            graphStore.syncing_err_msg = errMsg
            reject(err)
        }finally {
            graphStore.is_syncing = false
            release()
        }

        if(taskResponse) {
            const {task_id} = taskResponse
            if(task_id) {
                try {
                    const messages = await taskManager.monitorTask(p, task_id)
                    console.log('WS:', messages)
                    resolve(p)
                }catch(err) {
                    if(err instanceof TaskCancelledError) {
                        reject(err)
                    }else {
                        const errMsg = err && typeof err === 'object' && 'message' in err
                        ? String(err.message)
                        : '无法连接到服务器，请检查网络或联系管理员。'
                        graphStore.syncing_err_msg = errMsg
                        reject(err)
                    }
                }
            }else {
                graphStore.syncing_err_msg = 'No task_id returned'
                reject('No task_id returned')
            }
        }else {
            resolve(p)
        }

    })
}

const syncProjectUiState = (p: Project, graphStore: any) => {
    return new Promise<any>(async (resolve, reject) => {

        const release = await mutex.acquire()
        graphStore.project.updated_at = Date.now()    //  update_at should writeback immediately
        graphStore.is_syncing = true
        graphStore.syncing_err_msg= ''

        try {
            const res = await authService.syncProjectUiApiProjectSyncUiPost(p.project_id, p.ui_state)
            resolve(res)
        }catch(err) {
            const errMsg = err && typeof err === 'object' && 'message' in err
              ? String(err.message)
              : '无法连接到服务器，请检查网络或联系管理员。'
            graphStore.syncing_err_msg = errMsg
            reject(err)
        }finally {
            graphStore.is_syncing = false
            release()
        }
    })
}

export const sync = async(graphStore: any) => {

    try {
        resultStore.cacheGarbageRecycle()
        const p = getProject(graphStore.project)
        const res = await syncProject(p, graphStore)
        console.log('syncProject response:', res, res === p)
        writeBackVueFLowProject(res, graphStore.project)
    }catch(err) {
        if(err instanceof TaskCancelledError) {
            console.log(err)
        }else {
            console.error('@', err)
        }
    }

}

export const syncUiState = async(graphStore: any) => {

    try {
        const p = getProject(graphStore.project)
        const res = await syncProjectUiState(p, graphStore)
        console.log('syncProjectUiState response:', res)
    }catch(err) {
        console.error('@@',err)
    }

}

export const getProjectFromServer = async (ProjectId: number) => {
    return authService.getProjectApiProjectProjectIdGet(ProjectId)
}