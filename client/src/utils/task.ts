import type { Project } from '@/utils/api'


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

class TaskManager {
  private currentTaskId: string | null = null
  private currentWebSocket: WebSocket | null = null
  private cancelCurrentTask: (() => void) | null = null
  private timeoutId: number | null = null

  monitorTask(project: Project, task_id: string): Promise<any[]> {
    return this.createCancellableTask(project, task_id)
  }

  private createCancellableTask(project: Project, task_id: string): Promise<any[]> {
    return new Promise((resolve, reject) => {
      const messages: any[] = []
      
      this.cancelCurrentTask = () => {
        if (this.currentWebSocket) {
          try {
            this.currentWebSocket.send('')
          }catch(err) {
            console.error('WebSocket 可能已经关闭:', err)
          }
          this.currentWebSocket.close()
          this.currentWebSocket = null
        }
        if (this.timeoutId) {
          clearTimeout(this.timeoutId)
          this.timeoutId = null
        }
        this.currentTaskId = null
        reject(new TaskCancelledError('任务被新请求取消'))
      }

      this.currentTaskId = task_id
      const ws = new WebSocket(`ws://localhost:8000/api/project/status/${task_id}`)
      this.currentWebSocket = ws

      this.timeoutId = window.setTimeout(() => {
        ws.close()
        this.cleanup()
        resolve(messages)
      }, 120000)

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data)
        messages.push(message)
        const patch = message.patch as any[]
        if (patch && patch.length > 0) {
          patch.forEach(p => {
            setDeep(project.workflow, p.key, p.value)
          })
        }
      }

      ws.onclose = (event) => {
        if (this.timeoutId) {
          clearTimeout(this.timeoutId)
          this.timeoutId = null
        }
        console.log(`WebSocket 关闭: code=${event.code}, reason=${event.reason}, wasClean=${event.wasClean}`)
        this.cleanup()
        resolve(messages)
      }

      ws.onerror = (error) => {
        if (this.timeoutId) {
          clearTimeout(this.timeoutId)
          this.timeoutId = null
        }
        console.error('WebSocket 错误:', error)
        this.cleanup()
        reject(error)
      }

      ws.onopen = () => {
        console.log(`WebSocket 连接已建立, 任务ID: ${task_id}`)
      }
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

  cancel(): void {
    if (this.cancelCurrentTask) {
      this.cancelCurrentTask()
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