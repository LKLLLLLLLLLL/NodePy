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
  const {addNodes, nodes, getSelectedNodes, getSelectedEdges, addEdges} = vueFLowInstance
  const project = ref<vueFlowProject>({
    project_id: -1,
    project_name: "",
    user_id: -1,
    workflow: {
      nodes: [],
      edges: []
    },
    updated_at: 0,
    editable: true
  })
  const is_syncing = ref(false)
  const syncing_err_msg = ref('')
  const maxNodeId = ref<Record<string, number>>({}) // record max id in history for each node type
  const copiedNodes = ref<Array<{type: string, position: {x: number, y: number}, param: any, id: string}>>([])
  const copiedEdges = ref<Array<{source: string, target: string, sourceHandle?: string | null, targetHandle?: string | null, type: string}>>([])
  const copiedNodesBounds = ref<{minX: number, minY: number, maxX: number, maxY: number} | null>(null)
  const idMap = ref<Record<string, string>>({}) //  record old node id to new id


  const nextId = (type:string):string => {
    let currentMax = 0
    nodes.value.forEach(n => {
      if(n.type === type) {
      const idNum = Number(n.id.split('_')[1])
        if(idNum > currentMax) {
          currentMax = idNum
        }
      }
    })
    const next = currentMax + 1
    maxNodeId.value[type] = next
    return `${type}_${next}`
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
      case 'RandomNode':
        const addedRandomNode: Nodetypes.RandomNode = {
          id,
          position,
          type: 'RandomNode',
          data: {
            param: {
              col_name: '',
              col_type: 'int'
            }
          }
        }
        addNodes(addedRandomNode)
        break
      case 'RangeNode':
        const addedRangeNode: Nodetypes.RangeNode = {
          id,
          position,
          type: 'RangeNode',
          data: {
            param: {
              col_name: '',
              col_type: 'int'
            }
          }
        }
        addNodes(addedRangeNode)
        break
      case 'DateTimeNode':
        const addedDateTimeNode: Nodetypes.DateTimeNode = {
          id,
          position,
          type: 'DateTimeNode',
          data: {
            param: {
              value: '',
              isNow: false
            }
          }
        }
        addNodes(addedDateTimeNode)
        break
      case 'KlineNode':
        const addedKlineNode: Nodetypes.KlineNode = {
          id,
          position,
          type: 'KlineNode',
          data: {
            param: {
              data_type: 'stock',
              symbol: '',
              interval: '1m'
            }
          }
        }
        addNodes(addedKlineNode)
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
      case 'NumberUnaryOpNode':
        const addedNumberUnaryOpNode: Nodetypes.NumberUnaryOpNode = {
          id,
          position,
          type: 'NumberUnaryOpNode',
          data: {
            param: {
              op: 'NEG'
            }
          }
        }
        addNodes(addedNumberUnaryOpNode)
        break
      case 'PrimitiveCompareNode':
        const addedPrimitiveCompareNode: Nodetypes.PrimitiveCompareNode = {
          id,
          position,
          type: 'PrimitiveCompareNode',
          data: {
            param: {
              op: 'EQ'
            }
          }
        }
        addNodes(addedPrimitiveCompareNode)
        break
      case 'BoolBinOpNode':
        const addedBoolBinOpNode: Nodetypes.BoolBinOpNode = {
          id,
          position,
          type: 'BoolBinOpNode',
          data: {
            param: {
              op: 'AND'
            }
          }
        }
        addNodes(addedBoolBinOpNode)
        break
      case 'BoolUnaryOpNode':
        const addedBoolUnaryOpNode: Nodetypes.BoolUnaryOpNode = {
          id,
          position,
          type: 'BoolUnaryOpNode',
          data: {
            param: {
              op: 'NOT'
            }
          }
        }
        addNodes(addedBoolUnaryOpNode)
        break
      case 'ColWithNumberBinOpNode':
        const addedColWithNumberBinOpNode: Nodetypes.ColWithNumberBinOpNode = {
          id,
          position,
          type: 'ColWithNumberBinOpNode',
          data: {
            param: {
              op: 'ADD',
              col: ''
            }
          }
        }
        addNodes(addedColWithNumberBinOpNode)
        break
      case 'ColWithBoolBinOpNode':
        const addedColWithBoolBinOpNode: Nodetypes.ColWithBoolBinOpNode = {
          id,
          position,
          type: 'ColWithBoolBinOpNode',
          data: {
            param: {
              op: 'AND',
              col: ''
            }
          }
        }
        addNodes(addedColWithBoolBinOpNode)
        break
      case 'NumberColUnaryOpNode':
        const addedNumberColUnaryOpNode: Nodetypes.NumberColUnaryOpNode = {
          id,
          position,
          type: 'NumberColUnaryOpNode',
          data: {
            param: {
              op: 'ABS',
              col: ''
            }
          }
        }
        addNodes(addedNumberColUnaryOpNode)
        break
      case 'BoolColUnaryOpNode':
        const addedBoolColUnaryOpNode: Nodetypes.BoolColUnaryOpNode = {
          id,
          position,
          type: 'BoolColUnaryOpNode',
          data: {
            param: {
              op: 'NOT',
              col: ''
            }
          }
        }
        addNodes(addedBoolColUnaryOpNode)
        break
      case 'NumberColWithColBinOpNode':
        const addedNumberColWithColBinOpNode: Nodetypes.NumberColWithColBinOpNode = {
          id,
          position,
          type: 'NumberColWithColBinOpNode',
          data: {
            param: {
              op: 'ADD',
              col1: '',
              col2: ''
            }
          }
        }
        addNodes(addedNumberColWithColBinOpNode)
        break
      case 'BoolColWithColBinOpNode':
        const addedBoolColWithColBinOpNode: Nodetypes.BoolColWithColBinOpNode = {
          id,
          position,
          type: 'BoolColWithColBinOpNode',
          data: {
            param: {
              op: 'AND',
              col1: '',
              col2: ''
            }
          }
        }
        addNodes(addedBoolColWithColBinOpNode)
        break
      case 'ColCompareNode':
        const addedColCompareNode: Nodetypes.ColCompareNode = {
          id,
          position,
          type: 'ColCompareNode',
          data: {
            param: {
              op: 'EQ',
              col1: '',
              col2: ''
            }
          }
        }
        addNodes(addedColCompareNode)
        break
      case 'ToStringNode':
        const addedToStringNode: Nodetypes.ToStringNode = {
          id,
          position,
          type: 'ToStringNode',
          data: {
            param: {}
          }
        }
        addNodes(addedToStringNode)
        break
      case 'ToIntNode':
        const addedToIntNode: Nodetypes.ToIntNode = {
          id,
          position,
          type: 'ToIntNode',
          data: {
            param: {
              method: 'FLOOR'
            }
          }
        }
        addNodes(addedToIntNode)
        break
      case 'ToFloatNode':
        const addedToFloatNode: Nodetypes.ToFloatNode = {
          id,
          position,
          type: 'ToFloatNode',
          data: {
            param: {}
          }
        }
        addNodes(addedToFloatNode)
        break
      case 'ToBoolNode':
        const addedToBoolNode: Nodetypes.ToBoolNode = {
          id,
          position,
          type: 'ToBoolNode',
          data: {
            param: {}
          }
        }
        addNodes(addedToBoolNode)
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
      case 'TableFromFileNode':
        const addedTableFromFileNode: Nodetypes.TableFromFileNode = {
          id,
          position,
          type: 'TableFromFileNode',
          data: {
            param: {}
          }
        }
        addNodes(addedTableFromFileNode)
        break
      case 'TableToFileNode':
        const addedTableToFileNode: Nodetypes.TableToFileNode = {
          id,
          position,
          type: 'TableToFileNode',
          data: {
            param: {
              format: 'csv'
            }
          }
        }
        addNodes(addedTableToFileNode)
        break
      case 'TextFromFileNode':
        const addedTextFromFileNode: Nodetypes.TextFromFileNode = {
          id,
          position,
          type: 'TextFromFileNode',
          data: {
            param: {}
          }
        }
        addNodes(addedTextFromFileNode)
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
      case 'AdvancePlotNode':
        const addedAdvancePlotNode: Nodetypes.AdvancePlotNode = {
          id,
          position,
          type: 'AdvancePlotNode',
          data: {
            param: {
              x_col: '',
              y_col: '',
              plot_type: 'bar'
            }
          }
        }
        addNodes(addedAdvancePlotNode)
        break
      case 'WordcloudNode':
        const addedWordcloudNode: Nodetypes.WordcloudNode = {
          id,
          position,
          type: 'WordcloudNode',
          data: {
            param: {
              word_col: '',
              frequency_col: ''
            }
          }
        }
        addNodes(addedWordcloudNode)
        break
      case 'StripNode':
        const addedStripNode: Nodetypes.StripNode = {
          id,
          position,
          type: 'StripNode',
          data: {
            param: {}
          }
        }
        addNodes(addedStripNode)
        break
      case 'SliceNode':
        const addedSliceNode: Nodetypes.SliceNode = {
          id,
          position,
          type: 'SliceNode',
          data: {
            param: {}
          }
        }
        addNodes(addedSliceNode)
        break
      case 'ReplaceNode':
        const addedReplaceNode: Nodetypes.ReplaceNode = {
          id,
          position,
          type: 'ReplaceNode',
          data: {
            param: {
              old: '',
              new: ''
            }
          }
        }
        addNodes(addedReplaceNode)
        break
      case 'LowerOrUpperNode':
        const addedLowerOrUpperNode: Nodetypes.LowerOrUpperNode = {
          id,
          position,
          type: 'LowerOrUpperNode',
          data: {
            param: {
              to_case: 'lower'
            }
          }
        }
        addNodes(addedLowerOrUpperNode)
        break
      case 'ConcatNode':
        const addedConcatNode: Nodetypes.ConcatNode = {
          id,
          position,
          type: 'ConcatNode',
          data: {
            param: {}
          }
        }
        addNodes(addedConcatNode)
        break
      case 'BatchStripNode':
        const addedBatchStripNode: Nodetypes.BatchStripNode = {
          id,
          position,
          type: 'BatchStripNode',
          data: {
            param: {
              col: ''
            }
          }
        }
        addNodes(addedBatchStripNode)
        break
      case 'BatchConcatNode':
        const addedBatchConcatNode: Nodetypes.BatchConcatNode = {
          id,
          position,
          type: 'BatchConcatNode',
          data: {
            param: {
              col1: '',
              col2: '',
            }
          }
        }
        addNodes(addedBatchConcatNode)
        break
      case 'RegexMatchNode':
        const addedRegexMatchNode: Nodetypes.RegexMatchNode = {
          id,
          position,
          type: 'RegexMatchNode',
          data: {
            param: {
              pattern: ''
            }
          }
        }
        addNodes(addedRegexMatchNode)
        break
      case 'BatchRegexMatchNode':
        const addedBatchRegexMatchNode: Nodetypes.BatchRegexMatchNode = {
          id,
          position,
          type: 'BatchRegexMatchNode',
          data: {
            param: {
              pattern: '',
              col: ''
            }
          }
        }
        addNodes(addedBatchRegexMatchNode)
        break
      case 'RegexExtractNode':
        const addedRegexExtractNode: Nodetypes.RegexExtractNode = {
          id,
          position,
          type: 'RegexExtractNode',
          data: {
            param: {
              pattern: ''
            }
          }
        }
        addNodes(addedRegexExtractNode)
        break
      case 'InsertConstColNode':
        const addedInsertConstColNode: Nodetypes.InsertConstColNode = {
          id,
          position,
          type: 'InsertConstColNode',
          data: {
            param: {
              col_name: '',
              col_type: 'int'
            }
          }
        }
        addNodes(addedInsertConstColNode)
        break
      case 'InsertRangeColNode':
        const addedInsertRangeColNode: Nodetypes.InsertRangeColNode = {
          id,
          position,
          type: 'InsertRangeColNode',
          data: {
            param: {
              col_name: '',
              col_type: 'int'
            }
          }
        }
        addNodes(addedInsertRangeColNode)
        break
      case 'InsertRandomColNode':
        const addedInsertRandomColNode: Nodetypes.InsertRandomColNode = {
          id,
          position,
          type: 'InsertRandomColNode',
          data: {
            param: {
              col_name: '',
              col_type: 'int'
            }
          }
        }
        addNodes(addedInsertRandomColNode)
        break
      case 'FilterNode':
        const addedFilterNode: Nodetypes.FilterNode = {
          id,
          position,
          type: 'FilterNode',
          data: {
            param: {
              cond_col: ''
            }
          }
        }
        addNodes(addedFilterNode)
        break
      case 'DropDuplicatesNode':
        const addedDropDuplicatesNode: Nodetypes.DropDuplicatesNode = {
          id,
          position,
          type: 'DropDuplicatesNode',
          data: {
            param: {
              subset_cols: []
            }
          }
        }
        addNodes(addedDropDuplicatesNode)
        break
      case 'DropNaNValueNode':
        const addedDropNaNValueNode: Nodetypes.DropNaNValueNode = {
          id,
          position,
          type: 'DropNaNValueNode',
          data: {
            param: {
              subset_cols: []
            }
          }
        }
        addNodes(addedDropNaNValueNode)
        break
      case 'FillNaNValueNode':
        const addedFillNaNValueNode: Nodetypes.FillNaNValueNode = {
          id,
          position,
          type: 'FillNaNValueNode',
          data: {
            param: {
              subset_cols: [],
              method: 'const'
            }
          }
        }
        addNodes(addedFillNaNValueNode)
        break
      case 'SortNode':
        const addedSortNode: Nodetypes.SortNode = {
          id,
          position,
          type: 'SortNode',
          data: {
            param: {
              sort_col: '',
              ascending: true
            }
          }
        }
        addNodes(addedSortNode)
        break
      case 'GroupNode':
        const addedGroupNode: Nodetypes.GroupNode = {
          id,
          position,
          type: 'GroupNode',
          data: {
            param: {
              group_cols: [],
              agg_cols: [],
              agg_func: 'COUNT'
            }
          }
        }
        addNodes(addedGroupNode)
        break
      case 'MergeNode':
        const addedMergeNode: Nodetypes.MergeNode = {
          id,
          position,
          type: 'MergeNode',
          data: {
            param: {}
          }
        }
        addNodes(addedMergeNode)
        break
      case 'TableSliceNode':
        const addedTableSliceNode: Nodetypes.TableSliceNode = {
          id,
          position,
          type: 'TableSliceNode',
          data: {
            param: {}
          }
        }
        addNodes(addedTableSliceNode)
        break
      case 'SelectColNode':
        const addedSelectColNode: Nodetypes.SelectColNode = {
          id,
          position,
          type: 'SelectColNode',
          data: {
            param: {
              selected_cols: []
            }
          }
        }
        addNodes(addedSelectColNode)
        break
      case 'JoinNode':
        const addedJoinNode: Nodetypes.JoinNode = {
          id,
          position,
          type: 'JoinNode',
          data: {
            param: {
              left_on: '',
              right_on: '',
              how: 'INNER'
            }
          }
        }
        addNodes(addedJoinNode)
        break
      case 'RenameColNode':
        const addedRenameColNode: Nodetypes.RenameColNode = {
          id,
          position,
          type: 'RenameColNode',
          data: {
            param: {
              rename_map: {}
            }
          }
        }
        addNodes(addedRenameColNode)
        break
      case 'ShiftNode':
        const addedShiftNode: Nodetypes.ShiftNode = {
          id,
          position,
          type: 'ShiftNode',
          data: {
            param: {
              col: '',
              periods: 0
            }
          }
        }
        addNodes(addedShiftNode)
        break
      case 'DatetimeComputeNode':
        const addedDatetimeComputeNode: Nodetypes.DatetimeComputeNode = {
          id,
          position,
          type: 'DatetimeComputeNode',
          data: {
            param: {
              op: 'ADD',
              unit: 'DAYS'
            }
          }
        }
        addNodes(addedDatetimeComputeNode)
        break
      case 'DatetimeDiffNode':
        const addedDatetimeDiffNode: Nodetypes.DatetimeDiffNode = {
          id,
          position,
          type: 'DatetimeDiffNode',
          data: {
            param: {
              unit: 'DAYS'
            }
          }
        }
        addNodes(addedDatetimeDiffNode)
        break
      case 'ToDatetimeNode':
        const addedToDatetimeNode: Nodetypes.ToDatetimeNode = {
          id,
          position,
          type: 'ToDatetimeNode',
          data: {
            param: {
              unit: 'DAYS'
            }
          }
        }
        addNodes(addedToDatetimeNode)
        break
    
      default:
        console.log(type)
    }
  }

  const addCopiedNode = (type: string, position: {x: number, y: number}, param: any) => {
    const addedNode: Nodetypes.BaseNode = {
      id: nextId(type),
      position,
      type,
      data: {
        param: param
      }
    }
    addNodes(addedNode)
    return addedNode
  }

  const copySelectedNodes = () => {
    const selectedNodes = getSelectedNodes.value
    copiedNodes.value = []
    copiedEdges.value = []
    idMap.value = {}  // clear previous data
    if(selectedNodes.length > 0 && project.value.editable) {
      copiedNodes.value = selectedNodes.map(n => ({
        id: n.id,
        type: n.type,
        position: {...n.position},
        param: JSON.parse(JSON.stringify(n.data.param)) // deep copy
      }))
      let minX = selectedNodes[0]!.position.x
      let minY = selectedNodes[0]!.position.y
      let maxX = selectedNodes[0]!.position.x
      let maxY = selectedNodes[0]!.position.y
      selectedNodes.forEach(n => {
        minX = Math.min(minX, n.position.x)
        minY = Math.min(minY, n.position.y)
        maxX = Math.max(maxX, n.position.x)
        maxY = Math.max(maxY, n.position.y)
      })
      copiedNodesBounds.value = { minX, minY, maxX, maxY }
      const selectedNodeIds = selectedNodes.map(n => n.id)
      const selectedEdges = getSelectedEdges.value.filter(e => selectedNodeIds.includes(e.source) && selectedNodeIds.includes(e.target))
      copiedEdges.value = selectedEdges.map(e => ({
        source: e.source,
        target: e.target,
        sourceHandle: e.sourceHandle,
        targetHandle: e.targetHandle,
        type: e.type
      }))
      console.log('copy nodes:', copiedNodes.value)
      console.log('copy edges:', copiedEdges.value)
    }
  }

  const pasteNodes = (position: {x: number, y: number}) => {
    if(copiedNodes.value.length > 0 && copiedNodesBounds.value && project.value.editable) {
      const {minX, minY} = copiedNodesBounds.value
      copiedNodes.value.forEach((nodeInfo) => {
        const relativeX = nodeInfo.position.x - minX
        const relativeY = nodeInfo.position.y - minY
        const newNode = addCopiedNode(
          nodeInfo.type,
          {
            x: position.x + relativeX,
            y: position.y + relativeY,
          },
          JSON.parse(JSON.stringify(nodeInfo.param)) // deep copy to avoid param binding
        )
        if(newNode) {
          idMap.value[nodeInfo.id] = newNode.id
        }
      })
      copiedEdges.value.forEach(e => {
        const newSourceId = idMap.value[e.source]
        const newTargetId = idMap.value[e.target]
        if(newSourceId && newTargetId) {
          const newEdge = {
            source: newSourceId,
            target: newTargetId,
            sourceHandle: e.sourceHandle,
            targetHandle: e.targetHandle,
            type: 'NodePyEdge'
          }
          addEdges(newEdge)
        }
      })
      console.log('paste nodes and their edges:', copiedNodes.value, copiedEdges.value)
    }
  }

  return {nodes, url_id, currentNode, addNode, project, is_syncing, syncing_err_msg, copySelectedNodes, pasteNodes}
})