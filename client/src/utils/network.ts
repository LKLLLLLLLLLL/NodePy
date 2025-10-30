import * as service from '@/utils/api/services/DefaultService'
import { monitorTask } from './task'
import type { Project } from './api'


export const syncProject = (p: Project, graphStore: any) => {
    return new Promise<Project>(async (resolve, reject) => {
        try {
            p.updated_at = Date.now()
            graphStore.is_syncing = true
            const taskResponse = await service.DefaultService.syncProjectApiProjectSyncPost(p)
            graphStore.is_syncing = false
            if(taskResponse) {
                const {task_id} = taskResponse
                if(task_id) {
                    try {
                        const messages = await monitorTask(p, task_id)
                        console.log('WS:', messages)
                        resolve(p)
                    }catch(err) {
                        graphStore.syncing_err_msg = err instanceof Error ? err.message : String(err)
                        reject(err)
                    }
                }else {
                    graphStore.syncing_err_msg = 'No task_id returned'
                    reject('No task_id returned')
                }
            }else {
                resolve(p)
            }
        }catch(err) {
            graphStore.syncing_err_msg = err instanceof Error ? err.message : String(err)
            reject(err)
        }finally {
            graphStore.is_syncing = false
        }
    })
}