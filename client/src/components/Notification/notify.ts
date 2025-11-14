import { reactive } from 'vue'

export type NotificationType = 'success' | 'error' | 'info' | 'warning'
export type NotificationMessage = {
  id: number
  type: NotificationType
  message: string
  duration?: number // ms, 0 means persistent
}

const state = reactive({ messages: [] as NotificationMessage[], nextId: 1 })

export const notificationState = state

// global defaults that can be set by the container via props
const defaults = {
  duration: 3000, // ms
  // top offset is visual only and handled by the container's style
}

export function setNotifyDefaults(opts: { duration?: number }) {
  if (typeof opts.duration === 'number') defaults.duration = opts.duration
}

export function notify(opts: { message: string; type?: NotificationType; duration?: number }) {
  const id = state.nextId++
  const msg: NotificationMessage = {
    id,
    type: opts.type || 'info',
    message: opts.message,
    duration: typeof opts.duration === 'number' ? opts.duration : defaults.duration,
  }
  state.messages.push(msg)

  if (msg.duration && msg.duration > 0) {
    setTimeout(() => {
      remove(id)
    }, msg.duration)
  }
  return id
}

export function remove(id: number) {
  const idx = state.messages.findIndex(m => m.id === id)
  if (idx >= 0) state.messages.splice(idx, 1)
}

// Compatibility helper so callers can use { message, type } like ElMessage
export default notify
