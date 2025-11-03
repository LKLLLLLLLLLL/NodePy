import * as service from '@/utils/api/services/DefaultService'
import { taskManager, TaskCancelledError } from './task'
import type { Project } from './api'


export const syncProject = (p: Project, graphStore: any) => {
    return new Promise<Project>(async (resolve, reject) => {
        try {
            p.updated_at = Date.now()
            graphStore.is_syncing = true
            graphStore.syncing_err_msg= ''
            if (taskManager.hasActiveTask()) {
                console.log('取消之前的同步任务:', taskManager.getCurrentTaskId())
                taskManager.cancel()
            }
            const taskResponse = await service.DefaultService.syncProjectApiProjectSyncPost(p)
            graphStore.is_syncing = false
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
        }catch(err) {
            const errMsg = err && typeof err === 'object' && 'message' in err
              ? String(err.message)
              : '无法连接到服务器，请检查网络或联系管理员。'
            graphStore.syncing_err_msg = errMsg
            graphStore.is_syncing = false
            reject(err)
        }finally {
            graphStore.is_syncing = false
        }
    })
}

export const syncProjectUiState = (p: Project, graphStore: any) => {
    return new Promise<any>(async (resolve, reject) => {
        try {
            p.updated_at = Date.now()
            graphStore.is_syncing = true
            graphStore.syncing_err_msg= ''
            const res = await service.DefaultService.syncProjectUiApiProjectSyncUiPost(p.project_id, p.ui_state)
            graphStore.is_syncing = false
            resolve(res)
        }catch(err) {
            const errMsg = err && typeof err === 'object' && 'message' in err
              ? String(err.message)
              : '无法连接到服务器，请检查网络或联系管理员。'
            graphStore.syncing_err_msg = errMsg
            graphStore.is_syncing = false
            reject(err)
        }finally {
            graphStore.is_syncing = false
        }
    })
}
