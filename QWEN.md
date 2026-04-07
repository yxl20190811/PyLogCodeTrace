# PyLogCodeTrace（代码追踪器）

## 项目概述

**PyLogCodeTrace** 是一个 **Python 运行时调用链可视化工具**，用于自动生成和展示代码执行过程中的函数调用关系。它通过增强日志记录捕获完整的调用栈信息，并提供 Web 可视化工具将扁平的日志转换为清晰的树状调用图。

核心价值：**让代码自己揭示执行流程，无需反复调试和交叉引用源码！**

## 项目架构

项目采用**三模块架构**，工作流如下：

```
function_calls.py          loguru_main.py           log_analyzer.html
(业务函数模块)        ───▶   (日志增强配置)    ───▶   (Web 可视化工具)
• 20个互相调用的函数        • 调用栈捕获              • 日志文件解析
• 调用深度控制              • 线程ID记录              • 调用树构建
• 日志记录(entry/exit)      • 程序入口                • 树形可视化
                                                          • 源码查看器
───────────────────────────────────────────────────────────────────────
     业务层 (Business)          日志增强层              可视化层 (Visualization)
```

### 模块职责

| 模块 | 职责 | 技术栈 | 代码行数 |
|------|------|--------|----------|
| **function_calls.py** | 业务函数定义、互相调用逻辑、深度控制 | Python 3.12+ | ~480 |
| **loguru_main.py** | 日志格式配置、调用栈捕获、程序入口 | Python + loguru | ~55 |
| **log_analyzer.html** | 日志解析、调用树构建、可视化展示 | HTML5 + CSS3 + JS | ~1123 |
| **main.js** | Electron 主进程、文件对话框、IPC 通信 | Electron + Node.js | ~180 |
| **preload.js** | 安全的 IPC 桥接（contextBridge） | Electron | ~15 |

## 快速开始

### 1. 安装依赖

```bash
pip install loguru
npm install  # 如需使用 Electron 桌面版
```

### 2. 运行程序生成日志

```bash
python loguru_main.py
```

输出增强格式的日志到控制台，包含：
- 线程 ID
- 完整调用栈路径
- 函数进入/退出消息
- 调用深度信息

### 3. 使用可视化工具分析

**Web 版**（推荐）：
1. 在浏览器中打开 `log_analyzer.html`
2. 点击 **"📂 打开日志文件"** 按钮
3. 选择 `.log` 文件（如 `1.log`）
4. 在左侧面板选择线程 ID
5. 在右侧面板查看**树状调用链**

**Electron 桌面版**：
```bash
npm start         # 生产模式
npm run dev       # 开发模式（打开 DevTools）
```

### 4. 映射源码目录（可选）

点击 **"📁 映射目录"** 按钮，选择包含 `.py` 文件的目录。之后点击调用树中的文件名，即可在底部查看器中打开对应源码，并自动高亮调用发生的行。

## 日志格式详解

### 输出格式

每条日志占用**两行**：

```
tid:{线程ID}|{调用栈路径}
tid:{线程ID}|{日志消息}
```

### 调用栈路径格式

```
函数名@文件路径@行号#函数名@文件路径@行号#...
```

| 字段 | 示例 | 说明 |
|------|------|------|
| **函数名** | `func_o` | 被调用的函数 |
| **文件路径** | `C:\hh\svn\yy\学习\PyLogCodeTrace\function_calls.py` | 完整绝对路径 |
| **行号** | `316` | 调用发生的行号 |
| **#** | 分隔符 | 调用链从外到内 |

### 调用栈示例

```
tid:2136|<module>@loguru_main.py@51#main@function_calls.py@453#func_o@function_calls.py@316#func_t@function_calls.py@416#
tid:2136|▶ 进入函数: func_t | 当前深度: 2
```

**调用链解析**（从外到内）：
```
<module>(loguru_main.py:51)
  └─ main(function_calls.py:453)
       └─ func_o(function_calls.py:316)
            └─ func_t(function_calls.py:416) ← 当前执行点
```

### 日志消息类型

| 类型 | 示例 | 说明 |
|------|------|------|
| 分隔线 | `================================================================================` | 程序开始/结束标记 |
| 程序状态 | `程序开始执行 - 使用loguru日志库` | 关键事件 |
| 随机选择函数 | `随机选择起始函数: func_o` | 入口函数选择 |
| 函数进入 | `▶ 进入函数: func_o | 当前深度: 1` | 函数调用入口 |
| 函数退出 | `◀ 退出函数: func_d | 当前深度: 20` | 函数返回 |
| 达到最大深度 | `  达到最大深度,返回` | 触发深度限制 |

## 核心实现原理

### 1. 调用栈捕获（loguru_main.py）

使用 Python 的 `sys._getframe()` 捕获调用栈：

```python
def get_call_depth1(record):
    """获取当前调用深度（快速版）"""
    stack = ""
    frame = sys._getframe(4)  # 跳过 get_call_depth 和调用者帧
    while frame:
        filename = frame.f_code.co_filename
        stack = frame.f_code.co_name + "@" + filename + "@" + str(frame.f_lineno) + "#" + stack
        frame = frame.f_back
    record["extra"]["depth"] = stack
    return True
```

**关键点**：
- `sys._getframe(4)` 跳过 loguru 内部帧，从业务代码开始捕获
- 通过 `frame.f_back` 遍历整个调用链
- 将调用栈注入到 loguru 的 `extra` 字段

### 2. 日志格式配置（loguru_main.py）

```python
fmt = (
    "<cyan>tid:{thread.id}</cyan>|<yellow>{extra[depth]:<2}</yellow>\n"
    "<cyan>tid:{thread.id}</cyan>|<level>{message}</level>"
)

logger.remove()
logger.add(
    sink=sys.stdout,
    level="DEBUG",
    format=fmt,
    colorize=True,
    filter=get_call_depth1
)
```

### 3. 业务函数调用逻辑（function_calls.py）

每个业务函数遵循统一模式：

```python
def func_x():
    log_entry("func_x")          # 记录进入日志

    if should_return():          # 检查深度限制
        logger.debug("  达到最大深度,返回")
        log_exit("func_x")
        return

    choice = random.choice(['a', 'b', 'c'])  # 随机选择下一个函数
    if choice == 'a':
        func_a()
    # ... 其他分支

    log_exit("func_x")           # 记录退出日志
```

**特点**：
- 最大深度限制：**20**（通过 `MAX_DEPTH` 常量控制）
- 调用关系随机生成（可通过 `random.seed(42)` 复现）
- 全局调用深度计数器（`call_depth`）

### 4. 调用树构建算法（log_analyzer.html）

前端通过**路径匹配算法**将扁平日志转换为树结构：

```javascript
function buildCallTree(lines, threadIdRegex) {
    const root = { name: 'root', children: [], messages: [], depth: -1 };
    let lastStackTrace = [];
    let pathNodes = [];  // 路径栈，跟踪当前节点的所有祖先

    lines.forEach(line => {
        const stackTrace = parseStackTrace(content);

        // 与上一次调用栈比较，找到第一个差异点
        let diffIndex = 0;
        for (let i = 0; i < Math.min(stackTrace.length, lastStackTrace.length); i++) {
            if (current_frame === previous_frame) {
                diffIndex = i + 1;
            } else {
                break;
            }
        }

        // 从差异点开始创建新节点
        for (let i = diffIndex; i < stackTrace.length; i++) {
            const newNode = { name: stackTrace[i].name, children: [], messages: [] };
            parentNode.children.push(newNode);
            pathNodes.push(newNode);
            parentNode = newNode;
        }
    });

    return root;
}
```

**算法特点**：
- 自动识别调用链的分支和返回
- 维护路径栈确保正确的父节点分配
- 支持深层嵌套（已测试达到 20 层）

## 项目结构

```
PyLogCodeTrace/
├── function_calls.py          # 业务函数模块（20 个互相调用的函数）
├── loguru_main.py             # 日志格式配置 + 程序入口
├── log_analyzer.html          # Web 日志可视化工具（纯前端）
├── 1.log                      # 示例日志文件
├── main.js                    # Electron 主进程
├── preload.js                 # Electron preload 脚本
├── package.json               # Electron 项目配置
├── README.md                  # 英文 README
├── README_en.md               # 英文文档
├── USER_MANUAL.md             # 用户手册（英文）
├── QWEN.md                    # 项目上下文文档
├── node_modules/              # npm 依赖目录
└── .git/                      # Git 版本控制目录
```

## 函数调用关系图

每个函数在未达到最大深度时，会从 3 个候选函数中随机选择一个调用：

| 函数 | 可能调用的函数 |
|------|----------------|
| func_a | func_b, func_c, func_d |
| func_b | func_a, func_e, func_f |
| func_c | func_d, func_g, func_h |
| func_d | func_a, func_e, func_i |
| func_e | func_b, func_f, func_j |
| func_f | func_c, func_g, func_k |
| func_g | func_a, func_d, func_l |
| func_h | func_b, func_e, func_m |
| func_i | func_c, func_f, func_n |
| func_j | func_d, func_g, func_o |
| func_k | func_a, func_h, func_p |
| func_l | func_b, func_i, func_q |
| func_m | func_c, func_j, func_r |
| func_n | func_d, func_k, func_s |
| func_o | func_e, func_l, func_t |
| func_p | func_f, func_m, func_a |
| func_q | func_g, func_n, func_b |
| func_r | func_h, func_o, func_c |
| func_s | func_i, func_p, func_d |
| func_t | func_j, func_q, func_e |

## Web 工具功能

### 核心特性

| 功能 | 说明 |
|------|------|
| **日志文件解析** | 自动解析 `tid:{ID}|{content}` 格式日志 |
| **线程 ID 分组** | 左侧面板按线程 ID 分组显示日志 |
| **树状调用链** | 右侧面板以树形结构展示完整调用链 |
| **节点折叠/展开** | 点击箭头折叠/展开子节点 |
| **语法高亮** | 函数名（黄色）、文件名（黄色可点击）、行号（红色） |
| **实时统计** | 底部状态栏显示节点数量 |
| **源码查看器** | 点击文件名打开对应源码，自动高亮调用行 |
| **目录映射** | 映射源码目录后自动加载 `.py` 文件 |

### 界面布局

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 PyLogCodeTrace    [📂 打开日志文件]  [📁 映射目录]          │
├──────────────┬──────────────────────────────────────────────────┤
│  线程列表     │  日志内容                                       │
│              │                                                 │
│  ○ tid:2136  │  ▶ main() (function_calls.py:436)               │
│              │     ├─ ▶ func_o() (function_calls.py:316)        │
│              │     │   ├─ ▶ func_t() (function_calls.py:416)    │
│              │     │   │   └─ ...                               │
│              │     │   └─ ...                                   │
│              │     └─ ...                                       │
│              │                                                 │
├──────────────┴──────────────────────────────────────────────────┤
│  总计 1 个线程                        总计 245 个节点            │
├─────────────────────────────────────────────────────────────────┤
│  源码查看器                                                     │
│  function_calls.py (第 316 行)                           [×]    │
│  314 │ def func_o():                                           │
│  315 │     """函数O - 可能调用func_e或func_l或func_t"""         │
│  316 │▶    log_entry("func_o")  ← 高亮显示                      │
│  317 │                                                          │
│  318 │     if should_return():                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 可拖动分割线

- 左右面板之间的分割线支持**鼠标拖动**调整宽度
- 最小宽度：120px
- 最大宽度：容器宽度 - 200px

## 依赖

### Python 模块

| 依赖 | 版本 | 说明 |
|------|------|------|
| **Python** | 3.12+ | 运行环境 |
| **loguru** | 任意 | 第三方日志库 |

安装：
```bash
pip install loguru
```

### Web 工具

| 要求 | 说明 |
|------|------|
| **浏览器** | 现代浏览器（Chrome、Firefox、Edge 等） |
| **外部依赖** | 无（纯前端） |
| **服务器** | 不需要（直接打开 HTML 文件） |

### Electron 桌面版

| 依赖 | 版本 | 说明 |
|------|------|------|
| **Node.js** | 16+ | 运行环境 |
| **Electron** | ^28.0.0 | 桌面应用框架 |

安装和运行：
```bash
npm install
npm start         # 生产模式
npm run dev       # 开发模式（打开 DevTools）
```

## 开发约定

### Python 代码
- 统一使用 `logger.debug()` 记录日志
- 函数命名简单（`func_a` ~ `func_t`），便于测试
- 调用关系随机生成，模拟复杂调用场景
- 通过 `random.seed(42)` 可复现调用链

### 日志格式
- 每条日志占用**两行**（调用栈路径 + 日志消息）
- 调用栈路径使用 `#` 分隔，格式：`函数名@文件路径@行号`
- 函数进入/退出日志成对出现

### Web 工具
- 纯前端实现，无需构建工具
- 原生 JavaScript（无框架依赖）
- 支持 LRU 缓存（最大 50 个文件）
- 文件映射限制：最多 1000 个 `.py` 文件，每个文件最大 5MB

### Electron 应用
- 使用 `contextBridge` + `contextIsolation` 确保安全
- 通过 IPC 处理文件操作（`ipcMain.handle` / `ipcRenderer.invoke`）
- 支持 UTF-8 和 UTF-16 编码自动检测

## 配置与自定义

### 调整最大调用深度

在 `function_calls.py` 中修改：

```python
MAX_DEPTH = 20  # 改为你需要的深度
```

### 复现调用链

取消注释 `random.seed(42)`：

```python
# 在 function_calls.py 末尾
if __name__ == "__main__":
    random.seed(42)  # 取消注释以复现结果
    main()
```

### 自定义日志格式

修改 `loguru_main.py` 中的 `fmt` 变量：

```python
fmt = (
    "<cyan>tid:{thread.id}</cyan>|<yellow>{extra[depth]:<2}</yellow>\n"
    "<cyan>tid:{thread.id}</cyan>|<level>{message}</level>"
)
```

### 调整调用栈捕获起点

修改 `sys._getframe(4)` 的参数：

```python
frame = sys._getframe(4)  # 增大或减小参数以调整捕获起点
```

## 如何将本工具应用到你的项目

### 场景：学习一个系统的调用关系

#### 步骤 1：准备业务代码

确保你的业务代码使用 `loguru` 记录日志，或在关键函数添加入口/退出日志：

```python
from loguru import logger

def your_function():
    logger.debug(f"▶ 进入函数: your_function")
    # ... 业务逻辑
    logger.debug(f"◀ 退出函数: your_function")
```

#### 步骤 2：集成日志增强模块

将 `loguru_main.py` 复制到你的项目，修改导入路径：

```python
# 改为你的业务模块
from your_module import main as your_main
```

#### 步骤 3：运行并生成日志

```bash
python loguru_main.py > output.log
```

#### 步骤 4：使用可视化工具分析

1. 打开 `log_analyzer.html`
2. 加载 `output.log`
3. 查看调用树

#### 步骤 5：映射源码目录

点击 **"📁 映射目录"**，选择你的源码目录。之后点击调用树中的文件名即可查看对应代码。

## 注意事项

1. **日志中的调用栈路径非常长**，建议使用 `log_analyzer.html` 工具分析，而非手动阅读
2. **每次运行会随机选择 3 个起始函数**，如需复现结果，取消注释 `random.seed(42)`
3. **Web 工具支持树状展开和折叠**，适合分析深层调用链
4. **浏览器安全限制**：无法直接读取本地文件，需使用"映射目录"或手动选择源文件
5. **调用深度计数器是全局的**：多线程场景下可能需要调整
6. **项目使用 Git 进行版本控制**（非 SVN）

## 学习技巧

### 如何使用本工具学习新系统

1. **运行目标系统**：使用本工具的日志增强功能运行目标系统
2. **查看调用树**：使用可视化工具查看实际运行时调用关系
3. **交叉参考源码**：点击调用树中的文件名，跳转到对应代码行
4. **理解业务流程**：通过调用树理解程序执行流程，无需逐行阅读代码

### 对比

| 传统方式 | 使用本工具 |
|----------|------------|
| 逐行阅读代码 | 查看实际运行时调用链 |
| 手动调试追踪 | 自动记录完整调用关系 |
| 脑补调用树 | 可视化树形展示 |
| 容易遗漏调用路径 | 完整记录所有路径 |
| 需反复调试验证 | 一次运行，清晰展示 |

## 文件编码说明

Electron 版本的日志读取功能支持多种编码自动检测：
- **UTF-8**（带或不带 BOM）
- **UTF-16 LE**（带 BOM 或启发式检测）
- **UTF-16 BE**（带 BOM）

检测逻辑：
1. 先检查 BOM 标记（UTF-8 BOM: EF BB BF，UTF-16 LE BOM: FF FE，UTF-16 BE BOM: FE FF）
2. 无 BOM 时，通过启发式算法检测：检查前 20 个偶数位置字节是否为零（UTF-16 LE 的 ASCII 内容表现为 `char\x00char\x00`）

## Electron IPC API

### 主进程（main.js）暴露的 IPC 处理器

| IPC Handler | 参数 | 返回值 | 说明 |
|-------------|------|--------|------|
| `open-log-file` | 无 | `{ filePath, content, fileName }` 或 `null` | 打开日志文件对话框 |
| `select-mapping-directory` | 无 | `{ dirPath, files: [...], totalScanned }` 或 `null` | 选择源码目录 |
| `read-file-content` | `filePath` (string) | `content` (string) | 读取指定文件内容 |
| `select-source-file` | 无 | `{ filePath, content, fileName }` 或 `null` | 选择单个源文件 |

### Preload 脚本（preload.js）暴露的安全 API

渲染进程通过 `window.electronAPI` 访问：

```javascript
// 打开日志文件
const result = await window.electronAPI.openLogFile();

// 选择映射目录
const result = await window.electronAPI.selectMappingDirectory();

// 读取文件内容
const content = await window.electronAPI.readFileContent(filePath);

// 选择单个源文件
const result = await window.electronAPI.selectSourceFile();
```

---

**最后更新**：2026 年 4 月 8 日