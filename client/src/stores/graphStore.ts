import { useVueFlow } from "@vue-flow/core"
import type * as Nodetypes from '../types/nodeTypes'

const initTime = Date.now()
const vueFLowInstance = useVueFlow('main')
const {addNodes} = vueFLowInstance
export const {getNodes} = vueFLowInstance

export const addNode = (type: string) => {
  switch(type){
    case 'ConstNode':
      const addedConstNode: Nodetypes.ConstNode = {
        id: (Date.now() - initTime).toString(),
        position: { x: 100, y: 100 + Math.floor(Math.random() * 101 - 50)},
        type: 'ConstNode',
        data: {
          value: 0,
          data_type: 'int'
        }
      }
      addNodes(addedConstNode)
      break
    case 'StringNode':
      const addedStringNode: Nodetypes.StringNode = {
        id: (Date.now() - initTime).toString(),
        position: { x: 100, y: 100 + Math.floor(Math.random() * 101 - 50)},
        type: 'StringNode',
        data: {
          value: ""
        }
      }
      addNodes(addedStringNode)
      break
    case 'TableNode':
      const addedTableNode: Nodetypes.TableNode = {
        id: (Date.now() - initTime).toString(),
        position: { x: 100, y: 100 + Math.floor(Math.random() * 101 - 50)},
        type: 'TableNode',
        data: {
          rows: [{hello: "world"}],
          columns: ['hello']
        }
      }
      addNodes(addedTableNode)
      break

    case 'NumBinComputeNode':
      const addedNumBinComputeNode: Nodetypes.NumBinComputeNode = {
        id: (Date.now() - initTime).toString(),
        position: { x: 100, y: 100 + Math.floor(Math.random() * 101 - 50)},
        type: 'NumBinComputeNode',
        data: {
          input: {},
          op: 'ADD'
        }
      }
      addNodes(addedNumBinComputeNode)
      break
    
    default:
      console.log(type)
  }
}
