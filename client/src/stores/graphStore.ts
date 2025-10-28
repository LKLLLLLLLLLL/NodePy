import { useVueFlow } from "@vue-flow/core"
import { defineStore } from 'pinia'
import type * as Nodetypes from '../types/nodeTypes'


export const useGraphStore = defineStore('graph', () => {
  const vueFLowInstance = useVueFlow('main')
  const {addNodes} = vueFLowInstance


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

      case 'NumBinComputeNode':
        const addedNumBinComputeNode: Nodetypes.NumBinComputeNode = {
          id: Date.now().toString(),
          position,
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


  return {addNode}
})