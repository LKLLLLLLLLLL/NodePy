import axios from 'axios';
import type { Project } from '@/utils/api'

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
      console.log("WS:", message)
    }

    ws.onclose = () => {
      clearTimeout(timeoutId)
      resolve()
    }

    ws.onerror = (error) => {
      clearTimeout(timeoutId)
      reject(error)
    }
  })

  return messages
}
