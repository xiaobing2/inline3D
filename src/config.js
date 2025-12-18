// 全局接口基础地址配置
// 优先读取环境变量 VUE_APP_API_BASE（在 .env 或 .env.local 中配置）
// 未配置时默认使用本地后端
export const API_BASE = process.env.VUE_APP_API_BASE || 'https://47.108.230.185';
