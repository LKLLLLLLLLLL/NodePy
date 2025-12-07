import type { Project } from '@/utils/api'
import { useGraphStore } from '@/stores/graphStore'
import { writeBackRunningTime } from './projectConvert'


// apply patch
function setDeep<O extends Record<string, any>>(
  obj: O,
  path: any[],
  value: any
): void {
  let cur: any = obj

  for (let i = 0; i < path.length - 1; i++) {
    const key = path[i]
    cur = cur[key]
  }

  cur[path[path.length - 1]] = value
}


export class TaskCancelledError extends Error {
    constructor(message: string = '任务被取消') {
        super(message)
        this.name = 'TaskCancelledError'
    }
}


//  timer message
type TimerMsg = {action: 'start' | 'stop' | 'error'; nodeId: string}
const timerListeners = new Set<(msg: TimerMsg) => void>()
const runningNodes = new Set<string>()
export const onTimerMsg = (callback: (msg: TimerMsg) => void) => {
  timerListeners.add(callback)
  return () => timerListeners.delete(callback)
}
const broadcastTimer = (msg: TimerMsg) => {
  if(msg.action === 'start') runningNodes.add(msg.nodeId)
  if(msg.action === 'error' || msg.action === 'stop') runningNodes.delete(msg.nodeId)
  timerListeners.forEach(callback => callback(msg))
}
const stopAllRunningTimers = () => {
  ;[...runningNodes].forEach(nodeId => {
    broadcastTimer({
      action: 'error',
      nodeId
    })
  })
}


class TaskManager {
  private currentTaskId: string | null = null
  private currentWebSocket: WebSocket | null = null
  private cancelCurrentTask: (() => Promise<void>) | null = null
  private timeoutId: number | null = null
  private isOpen: Promise<void> | null = null
  private isClosed: Promise<void> | null = null

  monitorTask(project: Project, task_id: string): Promise<any[]> {
    return this.createCancellableTask(project, task_id)
  }

  private createCancellableTask(project: Project, task_id: string): Promise<any[]> {
    return new Promise((resolve, reject) => {
      const messages: any[] = []
      
      this.cancelCurrentTask = async () => {
        if (this.currentWebSocket) {
          try {
            await this.isOpen
            this.currentWebSocket.send('')
            reject(new TaskCancelledError('任务被新请求取消'))
            await this.isClosed
          }catch(err) {
            console.log('WebSocket 可能已经关闭:', err)
          }
        }
      }

      this.currentTaskId = task_id
      const ws = new WebSocket(`ws://localhost:8000/api/project/status/${task_id}`)
      this.currentWebSocket = ws
      this.timeoutId = window.setTimeout(() => {
        ws.close()
        this.cleanup()
        resolve(messages)
      }, 600000)


      ws.onmessage = (event) => {
        const message = JSON.parse(event.data)
        messages.push(message)

        const patch = message.patch as any[]
        if (patch && patch.length > 0) {
          patch.forEach(p => {
            setDeep(project.workflow, p.key, p.value)
            const graphStore:any = useGraphStore()
            writeBackRunningTime(project, graphStore.project)
          })
        }

        if(message.timer === 'start' || message.timer === 'stop') {
          broadcastTimer({
            action: message.timer,
            nodeId: message.node_id
          })
        }

      }

      ws.onerror = (error) => {
        console.error('WebSocket 错误:', error)
        this.cleanup()
        reject(error)
      }

      this.isOpen =  new Promise<void> ((res, rej) => {
        ws.onopen = () => {
          res()
          console.log(`WebSocket 连接已建立, 任务ID: ${task_id}`)
        }
      })

      this.isClosed = new Promise<void> ((res, rej) => {
        ws.onclose = (event) => {
          this.cleanup()
          stopAllRunningTimers()
          resolve(messages)
          res()
          console.log(`WebSocket 关闭: code=${event.code}, reason=${event.reason}, wasClean=${event.wasClean}, taskid=${task_id}`)
        }
      })


    })
  }

  private cleanup(): void {
    this.currentTaskId = null
    this.currentWebSocket = null
    this.cancelCurrentTask = null
    if (this.timeoutId) {
      clearTimeout(this.timeoutId)
      this.timeoutId = null
    }
  }

  async cancel(): Promise<void> {
    if (this.cancelCurrentTask) {
      await this.cancelCurrentTask()
    }
  }

  hasActiveTask(): boolean {
    return this.currentTaskId !== null
  }

  getCurrentTaskId(): string | null {
    return this.currentTaskId
  }
}

export const taskManager = new TaskManager()