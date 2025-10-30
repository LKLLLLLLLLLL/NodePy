import * as service from '@/utils/api/services/DefaultService'
import { monitorTask } from './task'
import type { Project } from './api'

interface SyncResponse{
    project: Project
    taskMsg?: any[]
}

export const syncProject = (p: Project) => {
    return new Promise<SyncResponse>(async (resolve, reject) => {
        try {
            p.updated_at = Date.now()
            const taskResponse = await service.DefaultService.syncProjectApiProjectSyncPost(p)
            if(taskResponse) {
                const {task_id} = taskResponse
                if(task_id) {
                    try {
                        const messages = await monitorTask(p, task_id)
                        resolve({
                            project: p,
                            taskMsg: messages
                        })
                    }catch(err) {
                        reject(err)
                    }
                }else {
                    reject('No task_id returned')
                }
            }else {
                resolve({project: p})
            }
        }catch(err) {
            reject(err)
        }
    })
}