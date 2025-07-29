/**
 * axios 基础配置
 */
import type { AxiosRequestConfig } from 'axios';
// 1. 从当前页面的 URL 中获取查询参数
const urlParams = new URLSearchParams(window.location.search);
// 2. 获取 'type' 参数的值
let domain = urlParams.get('type');

// 3. 修正不规范的 URL (http:/... -> http://...)
if (domain && domain.startsWith('http:/') && !domain.startsWith('http://')) {
  domain = domain.replace('http:/', 'http://');
}

export const baseConfig: AxiosRequestConfig = {
  baseURL: domain ?? window.location.origin, // baseUrl
  timeout: 60000 // 超时时间
};
