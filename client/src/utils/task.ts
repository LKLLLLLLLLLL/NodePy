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

export async function monitorTask(project: Project, task_id: string): Promise<any[]> {
  const messages: any[] = []

  await new Promise<void>((resolve, reject) => {
    const ws = new WebSocket(`ws://localhost:8000/api/project/status/${task_id}`)
    const timeoutId = setTimeout(() => {
      ws.close()
      resolve()
    }, 120000)

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      messages.push(message)
      const patch = message.patch as any[]
      if(patch && patch.length > 0) {
        patch.forEach(p => {
          setDeep(project.workflow, p.key, p.value)
        })
      }
    }

    ws.onclose = (event) => {
      clearTimeout(timeoutId)
      console.log(`WebSocket 关闭: code=${event.code}, reason=${event.reason}, wasClean=${event.wasClean}`)
      resolve()
    }

    ws.onerror = (error) => {
      clearTimeout(timeoutId)
      console.error('WebSocket 错误:', error)
      reject(error)
    }
  })

  return messages
}
