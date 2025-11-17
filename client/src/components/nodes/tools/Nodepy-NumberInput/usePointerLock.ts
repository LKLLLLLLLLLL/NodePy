import { ref, onMounted, onUnmounted } from "vue";

export interface Position {
  x: number
  y: number
}

export function usePointerLock(params: { onMove: (movement: Position, acceleration: number) => void, onDragEnd?: () => void }) {
  const isLocked = ref(false)
  const isDragging = ref(false)
  const totalMovement = ref(0)

  const handleLockChange = () => {
    isLocked.value = document.pointerLockElement !== null
  }

  const handleMove = (e: PointerEvent) => {
    if (!isLocked.value || !isDragging.value) return
    totalMovement.value += Math.abs(e.movementX)
    const acceleration = 1 + Math.log1p(totalMovement.value)  //  the farther the user move, the faster the number increases
    params.onMove({ x: e.movementX, y: e.movementY }, acceleration)
  }

  const handleMouseUp = () => {
    isDragging.value = false
    totalMovement.value = 0 // reset total movement
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
    totalMovement.value = 0 // reset total movement
    element.requestPointerLock()
    document.addEventListener("mouseup", handleMouseUp)
    document.addEventListener("pointermove", handleMove)
  }

  return {
    isLocked,
    requestLock,
  }
}