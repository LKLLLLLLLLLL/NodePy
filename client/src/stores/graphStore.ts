import { useVueFlow } from "@vue-flow/core"
import { ref } from "vue"
import { defineStore } from 'pinia'
import type * as Nodetypes from '../types/nodeTypes'
import type { Project } from "@/utils/api"


export const useGraphStore = () => {
  const vueFLowInstance = useVueFlow('main')
  const {addNodes} = vueFLowInstance
  const project = ref<Project>()


  const addNode = (type: string) => {
    switch(type){
      case 'ConstNode':
        const addedConstNode: Nodetypes.ConstNode = {
          id: Date.now().toString(),
          position: { x: 100, y: 100 + Math.floor(Math.random() * 101 - 50)},
          type: 'ConstNode',
          data: {
            param: {
              value: 0,
              data_type: 'int'
            }
          }
        }
        addNodes(addedConstNode)
        break
      case 'StringNode':
        const addedStringNode: Nodetypes.StringNode = {
          id: Date.now().toString(),
          position: { x: 100, y: 100 + Math.floor(Math.random() * 101 - 50)},
          type: 'StringNode',
          data: {
            param: {
              value: ""
            }
          }
        }
        addNodes(addedStringNode)
        break
      case 'TableNode':
        const addedTableNode: Nodetypes.TableNode = {
          id: Date.now().toString(),
          position: { x: 100, y: 100 + Math.floor(Math.random() * 101 - 50)},
          type: 'TableNode',
          data: {
            param: {
              rows: [],
              col_names: []
            }
          }
        }
        addNodes(addedTableNode)
        break

      case 'NumBinComputeNode':
        const addedNumBinComputeNode: Nodetypes.NumBinComputeNode = {
          id: Date.now().toString(),
          position: { x: 100, y: 100 + Math.floor(Math.random() * 101 - 50)},
          type: 'NumBinComputeNode',
          data: {
            param: {
              op: 'ADD'
            }
          },
        }
        addNodes(addedNumBinComputeNode)
        break
    
      default:
        console.log(type)
    }
  }


  return {vueFLowInstance, addNode, project}
}