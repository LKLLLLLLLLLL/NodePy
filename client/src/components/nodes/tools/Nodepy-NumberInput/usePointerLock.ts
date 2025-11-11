import { ref, onMounted, onUnmounted } from "vue";

export interface Position {
  x: number
  y: number
}

export function usePointerLock(params: { onMove: (movement: Position) => void, onDragEnd?: () => void }) {
  const isLocked = ref(false)
  const isDragging = ref(false)

  const handleLockChange = () => {
    isLocked.value = document.pointerLockElement !== null
  }

  const handleMove = (e: PointerEvent) => {
    if (!isLocked.value || !isDragging.value) return
    params.onMove({ x: e.movementX, y: e.movementY })
  }

  const handleMouseUp = () => {
    isDragging.value = false
    document.exitPointerLock()
    document.removeEventListener("pointermove", handleMove)
    document.removeEventListener("mouseup", handleMouseUp)
    if(params.onDragEnd) {
      params.onDragEnd()
    }
  }

  onMounted(() => {
    document.addEventListener("pointerlockchange", handleLockChange)
  })

  onUnmounted(() => {
    document.removeEventListener("pointerlockchange", handleLockChange)
  })

  const requestLock = (element: HTMLElement) => {
    isDragging.value = true
    element.requestPointerLock()
    document.addEventListener("mouseup", handleMouseUp)
    document.addEventListener("pointermove", handleMove)
  }

  return {
    isLocked,
    requestLock,
  }
}