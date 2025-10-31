import { ref, onMounted, onUnmounted, type Ref } from "vue";

export interface Position {
  x: number
  y: number
}

export function usePointerLock(params: { onMove: (movement: Position) => void, onDragEnd?: () => void }) {
  const isLocked: Ref<boolean> = ref(false)
  const hasDragged = ref(false)

  const handleLockChange = () => {
    isLocked.value = document.pointerLockElement !== null
    if (isLocked.value) {
      hasDragged.value = false
    }
  }

  const handleMove = (e: PointerEvent) => {
    if (!isLocked.value) return
    if (e.movementX !== 0 || e.movementY !== 0) {
      hasDragged.value = true
    }
    params.onMove({ x: e.movementX, y: e.movementY })
  }

  const handlePointerUp = () => {
    document.exitPointerLock()
    document.removeEventListener("pointermove", handleMove)
    if(params.onDragEnd) {
      params.onDragEnd()
    }
  }

  onMounted(() => {
    document.addEventListener("pointerlockchange", handleLockChange)
    document.addEventListener("pointerup", handlePointerUp)
  })

  onUnmounted(() => {
    document.removeEventListener("pointerlockchange", handleLockChange)
    document.removeEventListener("pointerup", handlePointerUp)
  })

  const requestLock = (element: HTMLElement) => {
    element.requestPointerLock()
    document.addEventListener("pointermove", handleMove)
  }

  return {
    isLocked,
    hasDragged,
    requestLock,
  }
}