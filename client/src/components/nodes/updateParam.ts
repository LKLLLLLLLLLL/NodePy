export const updateSimpleStringNumberBoolValue = (param: Record<string, any>, k: string, v: string|number|boolean|null) => {
    param[k] = v
}

export const updateSimpleSelectFew = (param: Record<string, any>, k: string, options: string[], idx: number[]) => {
    param[k] = options[idx[0]!]
}

export const updateSimpleSelectMany = (param: Record<string, any>, k: string, options: string[], idx: number) => {
    param[k] = options[idx]
}

export const updateSimpleMultiSelectMany = (param: Record<string, any>, k: string, options: string[], idx: number[]) => {
    param[k] = idx.map(i => options[i])
}
