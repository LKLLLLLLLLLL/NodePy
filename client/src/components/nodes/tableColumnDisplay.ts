export const displayColumnName = (colName: string | null | undefined) => {
    switch(colName) {
        case '_no_specified_col':
            return '不指定列名'
        case '_index':
            return '行号'
        default:
            return colName      
    }
}

export const isSpecialColumn = (colName: string | null | undefined) => {
    switch(colName) {
        case '_no_specified_col':
        case '_index':
            return true
        default:
            return false
    }
}