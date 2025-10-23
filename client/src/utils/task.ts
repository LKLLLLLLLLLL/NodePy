import axios from 'axios';
import WebSocket from 'ws';
import type { Project } from '@/utils/api'

export async function monitorTask(project: Project, task_id: string): Promise<any[]> {
  const messages: any[] = []

  await new Promise<void>((resolve, reject) => {
    const ws = new WebSocket(`ws://localhost:8000/api/project/status/${task_id}`)
    const timeoutId = setTimeout(() => {
      ws.close()
      resolve()
    }, 120000)

    ws.on('message', (data) => {
      const message = JSON.parse(data.toString());
      messages.push(message);
      console.log("WS:", message);
    })

    ws.on('close', () => {
      clearTimeout(timeoutId);
      resolve();
    })

    ws.on('error', reject)
  })

  return messages
}
