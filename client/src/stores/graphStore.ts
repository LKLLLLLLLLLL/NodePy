import { useVueFlow } from "@vue-flow/core"
import { defineStore } from 'pinia'
import type * as Nodetypes from '../types/nodeTypes'
import type { vueFlowProject } from "@/types/vueFlowProject"
import {ref} from 'vue'


export const useGraphStore = defineStore('graph', () => {
  const vueFLowInstance = useVueFlow('main')
  const {addNodes} = vueFLowInstance
  const project = ref<vueFlowProject>({
    project_id: -1,
    project_name: "undefined",
    user_id: -1,
    workflow: {
      nodes: [],
      edges: []
    },
    updated_at: 0
  })
  const is_syncing = ref(false)
  const syncing_err_msg = ref('')


  const addNode = (type: string, position: {x: number, y: number}) => {
    switch(type){
      case 'ConstNode':
        const addedConstNode: Nodetypes.ConstNode = {
          id: Date.now().toString(),
          position,
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
          position,
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
          position,
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

      case 'NumberBinOpNode':
        const addedNumBinComputeNode: Nodetypes.NumberBinOpNode = {
          id: Date.now().toString(),
          position,
          type: 'NumberBinOpNode',
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


  return {addNode, project, is_syncing, syncing_err_msg}
})