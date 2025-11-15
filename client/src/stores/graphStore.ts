import { useVueFlow } from "@vue-flow/core"
import { defineStore } from 'pinia'
import type * as Nodetypes from '../types/nodeTypes'
import type { vueFlowProject } from "@/types/vueFlowProject"
import {ref} from 'vue'


export const useGraphStore = defineStore('graph', () => {
  const currentNode = ref<Nodetypes.BaseNode>()
  const default_url_id: number = 12306
  const url_id = ref<number>(default_url_id)

  const vueFLowInstance = useVueFlow('main')
  const {addNodes, nodes} = vueFLowInstance
  const project = ref<vueFlowProject>({
    project_id: -1,
    project_name: "",
    user_id: -1,
    workflow: {
      nodes: [],
      edges: []
    },
    updated_at: 0
  })
  const is_syncing = ref(false)
  const syncing_err_msg = ref('')


  const nextId = (type:string):string => {
    const sameTypeNodes = nodes.value.filter(n => n.type === type)
    const count = sameTypeNodes.length + 1
    return `${type}_${count}`
  }

  const addNode = (type: string, position: {x: number, y: number}) => {
    const id = nextId(type)
    switch(type){
      case 'ConstNode':
        const addedConstNode: Nodetypes.ConstNode = {
          id,
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
          id,
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
          id,
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
      case 'BoolNode':
        const addedBoolNode: Nodetypes.BoolNode = {
          id,
          position,
          type: 'BoolNode',
          data: {
            param: {
              value: true
            }
          }
        }
        addNodes(addedBoolNode)
        break
      case 'NumberBinOpNode':
        const addedNumBinComputeNode: Nodetypes.NumberBinOpNode = {
          id,
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
      case 'TableFromCSVNode':
        const addedTableFromCSVNode: Nodetypes.TableFromCSVNode = {
          id,
          position,
          type: 'TableFromCSVNode',
          data: {
            param: {}
          }
        }
        addNodes(addedTableFromCSVNode)
        break
      case 'UploadNode':
        const addedUploadNode: Nodetypes.UploadNode = {
          id,
          position,
          type: 'UploadNode',
          data: {
            param: {
              file: null as any
            }
          }
        }
        addNodes(addedUploadNode)
        break
      case 'PlotNode':
        const addedPlotNode: Nodetypes.PlotNode = {
          id,
          position,
          type: 'PlotNode',
          data: {
            param: {
              x_col: '',
              y_col: '',
              plot_type: 'line',
            }
          }
        }
        addNodes(addedPlotNode)
        break
    
      default:
        console.log(type)
    }
  }


  return {nodes, url_id, currentNode, addNode, project, is_syncing, syncing_err_msg}
})