const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    title: 'PyLogCodeTrace 日志分析工具',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });

  mainWindow.loadFile('log_analyzer.html');

  // 开发模式下打开 DevTools
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// ========== IPC 处理：打开日志文件 ==========
ipcMain.handle('open-log-file', async () => {
  console.log('[main] open-log-file 被调用');
  const result = await dialog.showOpenDialog(mainWindow, {
    title: '选择日志文件',
    properties: ['openFile'],
    filters: [
      { name: 'Log Files', extensions: ['log', 'txt'] }
    ]
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  const filePath = result.filePaths[0];
  console.log('[main] 选择的日志文件:', filePath);
  try {
    const buffer = fs.readFileSync(filePath);
    let content;

    // 先检查 BOM
    if (buffer.length >= 2 && buffer[0] === 0xFF && buffer[1] === 0xFE) {
      // UTF-16 LE BOM
      content = buffer.slice(2).toString('utf16le');
      console.log('[main] 检测到 UTF-16 LE BOM');
    } else if (buffer.length >= 2 && buffer[0] === 0xFE && buffer[1] === 0xFF) {
      // UTF-16 BE BOM
      // 交换字节后按 utf16le 解码
      const swapped = Buffer.alloc(buffer.length - 2);
      for (let i = 2; i < buffer.length; i += 2) {
        swapped[i - 2] = buffer[i + 1];
        swapped[i - 1] = buffer[i];
      }
      content = swapped.toString('utf16le');
      console.log('[main] 检测到 UTF-16 BE BOM');
    } else if (buffer.length >= 3 && buffer[0] === 0xEF && buffer[1] === 0xBB && buffer[2] === 0xBF) {
      content = buffer.toString('utf8');
      console.log('[main] 检测到 UTF-8 BOM');
    } else {
      // 没有 BOM，启发式检测：检查前 20 个偶数位置字节是否为零
      // UTF-16 LE 的 ASCII 内容表现为 char\x00char\x00
      let zeroCount = 0;
      const checkLen = Math.min(40, buffer.length - 1);
      for (let i = 1; i < checkLen; i += 2) {
        if (buffer[i] === 0) zeroCount++;
      }
      const threshold = checkLen / 4; // 超过 25% 的偶数位为零则认为是 UTF-16 LE
      if (zeroCount > threshold) {
        content = buffer.toString('utf16le');
        console.log(`[main] 启发式检测: UTF-16 LE (偶数位零的比例: ${zeroCount}/${checkLen})`);
      } else {
        content = buffer.toString('utf8');
        console.log(`[main] 启发式检测: UTF-8 (偶数位零的比例: ${zeroCount}/${checkLen})`);
      }
    }

    console.log('[main] 读取成功, 大小:', content.length, '字符');
    return { filePath, content, fileName: path.basename(filePath) };
  } catch (err) {
    console.error('[main] 读取日志文件失败:', err);
    throw new Error(`读取文件失败: ${err.message}`);
  }
});

// ========== IPC 处理：选择映射目录 ==========
ipcMain.handle('select-mapping-directory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: '选择源码目录',
    properties: ['openDirectory']
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  const dirPath = result.filePaths[0];

  // 递归扫描所有 .py 文件
  const pyFiles = [];
  const MAX_FILES = 1000;
  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

  function scanDir(dir, baseDir) {
    if (pyFiles.length >= MAX_FILES) return;

    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }

    for (const entry of entries) {
      if (pyFiles.length >= MAX_FILES) break;

      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        // 跳过隐藏目录和 node_modules
        if (entry.name.startsWith('.') || entry.name === 'node_modules') continue;
        scanDir(fullPath, baseDir);
      } else if (entry.isFile() && entry.name.endsWith('.py')) {
        try {
          const stats = fs.statSync(fullPath);
          if (stats.size <= MAX_FILE_SIZE) {
            const relativePath = path.relative(baseDir, fullPath);
            pyFiles.push({
              absolutePath: fullPath,
              relativePath: relativePath,
              fileName: entry.name,
              size: stats.size
            });
          }
        } catch {
          // 跳过无法访问的文件
        }
      }
    }
  }

  scanDir(dirPath, dirPath);

  return { dirPath, files: pyFiles, totalScanned: pyFiles.length };
});

// ========== IPC 处理：读取文件内容 ==========
ipcMain.handle('read-file-content', async (event, filePath) => {
  console.log('[main] read-file-content 收到路径:', filePath);
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    console.log('[main] 读取成功, 长度:', content.length);
    return content;
  } catch (err) {
    console.error('[main] 读取文件失败:', err.message);
    throw new Error(`读取文件失败: ${err.message}`);
  }
});

// ========== IPC 处理：选择单个源文件 ==========
ipcMain.handle('select-source-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: '选择源文件',
    properties: ['openFile'],
    filters: [
      { name: 'Python Files', extensions: ['py'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  const filePath = result.filePaths[0];
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    return { filePath, content, fileName: path.basename(filePath) };
  } catch (err) {
    throw new Error(`读取文件失败: ${err.message}`);
  }
});
