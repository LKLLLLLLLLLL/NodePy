type MustExist<T> = T extends null | undefined ? never : T

export function handleNetworkError<T>(err: MustExist<T>, statusMsgMap: Record<number, string> = {
    400: '请求参数错误，请检查输入。',
    401: '未授权，请重新登录。',
    403: '权限不足。',
    404: '资源未找到。',
    423: '项目被锁定，可能是因为并发操作。',
    500: '服务器内部错误，请联系管理员。',
    502: '网关错误，请检查网络。',
    503: '服务器未启动或服务不可用，请检查服务器状态。',
}): string {
    let errMsg = '无法连接到服务器，请检查网络或联系管理员。'
    
    // check if errobj has status code
    if (err && typeof err === 'object' && 'status' in err) {
        const status = err.status as number
        // check if status code is in the map
        errMsg = statusMsgMap[status] || `未知错误 (状态码: ${status})，请联系管理员。`
    }else {
        // if status code is not in the map, it is a default network error
        errMsg = '网络连接失败，请检查网络或服务器状态。'
    }
    return errMsg
}