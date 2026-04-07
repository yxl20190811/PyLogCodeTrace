const { contextBridge, ipcRenderer } = require('electron');

// 向渲染进程暴露安全的 API
contextBridge.exposeInMainWorld('electronAPI', {
  // 打开日志文件
  openLogFile: () => ipcRenderer.invoke('open-log-file'),

  // 选择映射目录
  selectMappingDirectory: () => ipcRenderer.invoke('select-mapping-directory'),

  // 读取文件内容
  readFileContent: (filePath) => ipcRenderer.invoke('read-file-content', filePath),

  // 选择单个源文件
  selectSourceFile: () => ipcRenderer.invoke('select-source-file')
});
