type MustExist<T> = T extends null | undefined ? never : T
export function handleNetworkError<T>(err: MustExist<T>): string {
    let errMsg = '无法连接到服务器，请检查网络或联系管理员。'
    
    // 检查错误对象是否有 status 属性（HTTP 状态码）
    if (err && typeof err === 'object' && 'status' in err) {
        const status = (err as any).status  // 类型断言为 any 以访问 status
        switch (status) {
            case 400:
                errMsg = '请求参数错误，请检查输入。'
                break
            case 401:
                errMsg = '未授权，请重新登录。'
                break
            case 403:
                errMsg = '权限不足。'
                break
            case 404:
                errMsg = '资源未找到。'
                break
            case 500:
                errMsg = '服务器内部错误，请联系管理员。'
                break
            case 502:
                errMsg = '网关错误，请检查网络。'
                break
            case 503:
                errMsg = '服务器未启动或服务不可用，请检查服务器状态。'  // 针对代理返回的 503
                break
            default:
                errMsg = `未知错误 (状态码: ${status})，请联系管理员。`
        }
    } else {
        // 如果没有 status，可能是网络错误或其他非 HTTP 错误
        errMsg = '网络连接失败，请检查网络或服务器状态。'
    }
    return errMsg
}