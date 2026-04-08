# PyLogCodeTrace 项目功能整理

> 整理时间：2026-04-09

---

## 一、项目总览

**PyLogCodeTrace** 是一套"Python 运行时调用链追踪 + 可视化分析"工具链。  
其核心价值是：**无需手动 Debug，直接通过日志文件还原代码真实运行时的函数调用树**，帮助开发者快速理解陌生代码库的执行流程。

---

## 二、文件结构说明

```
PyLogCodeTrace/
├── function_calls.py      # 业务函数模块（20 个互相调用的演示函数）
├── loguru_main.py         # 日志格式配置 + Python 程序入口
├── log_analyzer.html      # 纯前端日志可视化分析工具（也支持 Electron 桌面版）
├── main.js                # Electron 主进程（桌面版入口）
├── preload.js             # Electron 预加载脚本（IPC 桥接）
├── package.json           # Electron 项目配置
├── 1.log                  # 示例日志文件
├── README.md              # 项目说明文档（中文）
├── QWEN.md                # 项目上下文文档
└── USER_MANUAL.md         # 用户手册
```

---

## 三、各模块功能详解

### 3.1 `function_calls.py` — 业务演示模块

**作用**：提供一组互相随机调用的演示函数，产生具有真实深度的调用链日志。

| 要素 | 说明 |
|------|------|
| 函数数量 | 20 个（`func_a` ~ `func_t`） |
| 调用方式 | 每个函数随机选择 3 个候选函数之一进行递归调用 |
| 深度控制 | 全局变量 `call_depth`，上限 `MAX_DEPTH = 20`，超过则返回 |
| 日志埋点 | `log_entry(func_name)` 进入时打印 `▶ 进入函数`；`log_exit(func_name)` 退出时打印 `◀ 退出函数` |
| 主函数 | `main()` 随机选 3 次起始函数，依次调用，形成 3 段调用树 |

**函数调用关系图**：

```
func_a → func_b / func_c / func_d
func_b → func_a / func_e / func_f
func_c → func_d / func_g / func_h
func_d → func_a / func_e / func_i
func_e → func_b / func_f / func_j
func_f → func_c / func_g / func_k
func_g → func_a / func_d / func_l
func_h → func_b / func_e / func_m
func_i → func_c / func_f / func_n
func_j → func_d / func_g / func_o
func_k → func_a / func_h / func_p
func_l → func_b / func_i / func_q
func_m → func_c / func_j / func_r
func_n → func_d / func_k / func_s
func_o → func_e / func_l / func_t
func_p → func_f / func_m / func_a
func_q → func_g / func_n / func_b
func_r → func_h / func_o / func_c
func_s → func_i / func_p / func_d
func_t → func_j / func_q / func_e
```

---

### 3.2 `loguru_main.py` — 日志格式配置 + 程序入口

**作用**：配置 loguru 日志格式，将**完整调用栈**注入每一条日志，然后调用 `function_calls.main()`。

**关键设计**：

```python
def get_call_depth1(record):
    """遍历 Python 运行时帧栈，将调用链序列化到日志 extra 字段"""
    frame = sys._getframe(4)   # 跳过 loguru 内部帧
    while frame:
        stack = 函数名 + "@" + 文件绝对路径 + "@" + 行号 + "#" + stack
        frame = frame.f_back
    record["extra"]["depth"] = stack
```

**日志输出格式**：

```
tid:{线程ID}|{函数名}@{文件路径}@{行号}#{函数名}@{文件路径}@{行号}#...
tid:{线程ID}|{实际日志消息}
```

每条日志前都有一行调用栈行（以 `@` 和 `#` 为分隔符），后跟一行消息行。

**示例日志**（来自 `1.log`）：
```
tid:2136|<module>@...\loguru_main.py@51#main@...\function_calls.py@453#func_o@...\function_calls.py@316#log_entry@...\function_calls.py@19#
tid:2136|▶ 进入函数: func_o | 当前深度: 1
```

---

### 3.3 `log_analyzer.html` — 日志可视化分析前端

**作用**：解析上述格式的日志文件，**按线程还原函数调用树**，支持源码跳转查看。

#### 主要功能区域

| 区域 | 功能 |
|------|------|
| 顶部工具栏 | 打开日志文件、映射源码目录按钮 |
| 左侧线程面板 | 列出日志中出现的所有线程 ID，点击切换 |
| 中间调用树面板 | 树形展示选中线程的函数调用链，可折叠展开 |
| 底部源码查看器 | 点击文件名后显示对应源文件，高亮目标行，支持拖拽调整高度 |

#### 核心 JS 函数说明

| 函数名 | 职责 |
|--------|------|
| `parseLogFile(content)` | 按 `tid:线程ID|` 分组所有日志行，构建 `threadMap` |
| `buildCallTree(lines)` | 对每条调用栈行解析并与上一条比较差异，增量构建树节点 |
| `parseStackTrace(stackTrace)` | 将 `函数名@文件路径@行号#` 格式解析为结构化对象数组 |
| `renderTree(node, container)` | 递归渲染调用树 DOM |
| `createTreeNode(node)` | 创建单个树节点，含折叠按钮、函数名、文件路径（可点击）、行号 |
| `showSourceFile(filePath, lineNumber)` | 打开源码查看器，支持目录映射 + 直接路径 + 手动选择 4 种文件查找策略 |
| `renderSourceContent(content, filePath, targetLine)` | 渲染源码，高亮目标行并自动滚动到视图中央 |

#### 文件查找策略（优先级从高到低）

1. **绝对路径精确匹配**：用日志中的绝对路径直接在已映射目录中查找
2. **相对路径精确匹配**：用文件名在映射目录中查找
3. **文件名后缀模糊匹配**：匹配路径末尾包含目标文件名的条目
4. **路径包含关系匹配**：最宽松的兼容匹配
5. **Electron 直接读取原始路径**（仅桌面版）
6. **手动选择文件**（所有策略失败时弹出文件选择框）

---

### 3.4 `main.js` — Electron 主进程

**作用**：创建桌面窗口，托管 `log_analyzer.html`，并通过 IPC 向前端提供文件系统能力。

| IPC 事件 | 功能 |
|----------|------|
| `open-log-file` | 弹出原生文件选择框，读取日志文件（支持 UTF-8 / UTF-16 LE / UTF-16 BE 自动检测） |
| `select-mapping-directory` | 弹出目录选择框，递归扫描所有 `.py` 文件（最多 1000 个，单文件最大 5MB） |
| `read-file-content` | 按路径读取任意文件内容（同样支持编码自动检测） |
| `select-source-file` | 弹出文件选择框让用户手动指定源文件 |

**编码自动检测逻辑**：
1. 检测 UTF-16 LE BOM（`FF FE`）
2. 检测 UTF-16 BE BOM（`FE FF`）
3. 检测 UTF-8 BOM（`EF BB BF`）
4. 无 BOM 时启发式检测：统计前 40 字节中偶数位为零的比例，超过 25% 则视为 UTF-16 LE

---

### 3.5 `preload.js` — Electron 预加载脚本

通过 `contextBridge` 安全地将主进程 IPC 接口暴露给渲染进程（`window.electronAPI`），遵循 Electron 安全最佳实践（`contextIsolation: true`，`nodeIntegration: false`）。

---

## 四、完整运行流程

### 流程 1：Python 端 —— 生成带调用栈的日志

```
1. 运行 loguru_main.py
   ↓
2. 配置 loguru 自定义 filter（get_call_depth1）
   ↓
3. 调用 function_calls.main()
   ↓
4. main() 随机选择起始函数，开始递归调用链
   ↓
5. 每次 logger.debug() 时，filter 触发：
   - 遍历当前 Python 帧栈
   - 序列化为  函数名@文件路径@行号# 格式
   - 写入 record["extra"]["depth"]
   ↓
6. loguru 按格式输出到 stdout（或文件）：
   tid:线程ID|调用栈字符串
   tid:线程ID|日志消息
   ↓
7. 生成 1.log（或重定向到其他 .log 文件）
```

### 流程 2：前端端 —— 可视化分析日志

```
1. 用浏览器（或 Electron 桌面版）打开 log_analyzer.html
   ↓
2. 点击「打开日志文件」
   - Electron：主进程弹出文件选择框，读取并返回内容
   - 浏览器：<input type="file"> 读取
   ↓
3. parseLogFile(content)
   - 按行扫描，正则提取 tid:线程ID|
   - 构建 threadMap（线程ID → 行数组）
   ↓
4. renderThreadList()
   - 左侧面板展示所有线程 ID
   ↓
5. 用户点击某个线程
   ↓
6. buildCallTree(lines)
   - 逐行解析调用栈行（含 @ 和 #）
   - 与上一条调用栈对比，找到首个差异位置
   - 差异之前的节点复用（路径不变），差异之后创建新节点
   - 消息行挂载到最近的调用栈节点
   ↓
7. renderTree(root, container)
   - 递归渲染树形 DOM
   - 每个节点显示：函数名 + (目录/文件名:行号)
   - 有子节点的显示折叠按钮（默认折叠）
   ↓
8. 用户点击节点中的文件名
   ↓
9. showSourceFile(filePath, lineNumber)
   - 按 4 级策略查找映射目录中的源文件
   - 找到后通过 Electron IPC 读取，或浏览器提示手动选择
   ↓
10. renderSourceContent(content, filePath, targetLine)
    - 渲染全部源码，带行号 gutter
    - 高亮目标行（红色背景）
    - 自动滚动使高亮行居中可见
```

---

## 五、核心技术要点

| 技术点 | 说明 |
|--------|------|
| **调用栈注入** | 利用 `sys._getframe()` 遍历运行时帧栈，将完整调用链序列化进每条日志 |
| **增量树构建** | 比较相邻两条调用栈的差异，找到第一个不同位置，仅创建新增节点，避免重复 |
| **多线程支持** | 日志中携带线程 ID，前端按线程分组，独立还原每条线程的调用树 |
| **文件编码兼容** | 支持 UTF-8（含 BOM）、UTF-16 LE、UTF-16 BE 的自动检测 |
| **源码映射** | 支持映射目录（批量预加载）+ 直接路径读取 + 手动选择，兼容跨机器路径变更 |
| **LRU 缓存** | 源码文件读取后缓存，最多 20 个文件，超出时淘汰最旧条目 |
| **双运行环境** | 同一个 HTML 文件既可在浏览器中运行（文件 input），也可在 Electron 中运行（原生文件对话框） |

---

## 六、快速使用步骤

### 方式一：浏览器（最简单）

```bash
# 1. 生成日志
python loguru_main.py > 1.log

# 2. 直接用浏览器打开
# 打开 log_analyzer.html → 点击「打开日志文件」→ 选择 1.log
```

### 方式二：Electron 桌面版

```bash
# 安装依赖
npm install

# 启动
npm start

# 开发模式（含 DevTools）
npm run dev
```

---

## 七、日志格式规范

每个日志块由两行组成：

```
tid:{线程ID}|{帧1函数名}@{帧1文件绝对路径}@{帧1行号}#{帧2函数名}@...#
tid:{线程ID}|{用户日志消息}
```

- `tid:` 前缀标识线程 ID
- `@` 分隔函数名、文件路径、行号
- `#` 分隔各帧（调用栈从外到内排列）
- 调用栈行（含 `@` 和 `#`）与消息行交替出现
