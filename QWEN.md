# PyLogCodeTrace（代码追踪器）

## 项目概述

这是一个用于**测试和生成复杂函数调用链日志**的 Python 工具项目，同时包含一个**基于 Web 的日志可视化分析工具**。项目模拟了多个函数之间相互调用的场景，使用 `loguru` 日志库记录详细的调用栈信息，并提供 HTML 前端工具用于分析和可视化展示调用链。

核心功能：
- 函数进入/退出日志记录
- 调用深度追踪（最大深度 20）
- 线程 ID 记录
- 完整的调用栈路径（包含文件名、函数名、行号）
- 基于浏览器的日志可视化工具

## 项目结构

```
日志分析工具/
├── 1.log                    # 日志输出示例（完整调用链日志）
├── log_analyzer.html        # Web 端日志分析工具：可视化展示调用链
├── QWEN.md                  # 项目上下文文档
├── function_calls.py         # 核心业务函数模块（20 个函数互相调用）
├── loguru_main.py           # 日志配置和主程序入口
└── .svn/                    # SVN 版本控制目录
```

## 核心模块说明

### function_calls.py
- **核心业务函数模块**
- 包含 20 个函数（`func_a` ~ `func_t`），每个函数随机调用其他函数
- 使用全局变量 `call_depth` 追踪调用深度，最大深度为 20
- 提供 `log_entry()` 和 `log_exit()` 函数记录函数进入/退出日志
- `main()` 函数随机选择 3 个起始函数进行调用链演示
- 支持通过 `random.seed(42)` 复现调用链（代码中已注释）

### loguru_main.py
- **日志配置和主程序入口**
- 使用 `loguru` 库配置自定义日志格式
- 通过 `sys._getframe()` 获取完整的调用栈路径
- 日志输出格式：`tid:{线程ID}|{调用栈路径}` + `tid:{线程ID}|{日志消息}`（两行一条日志）
- 调用 `function_calls.main()` 启动程序

### log_analyzer.html
- **独立的 Web 端日志分析工具**（纯前端，无需服务器）- PyLogCodeTrace 可视化前端
- 功能特性：
  - 支持打开 `.log` 文件
  - 按线程 ID 分组显示日志
  - **树状结构展示函数调用链**
  - 可折叠/展开调用树节点
  - 语法高亮（函数名、文件名、行号）
  - 实时统计节点数量
- 技术栈：HTML5 + CSS3 + 原生 JavaScript（无外部依赖）
- 总计 1141 行代码

### 1.log（日志示例）
- 包含完整的函数调用链日志
- 展示了从 `func_o` 开始的深度调用树（最深达到 20 层）
- 日志路径引用：`C:\hh\svn\yy\学习\日志分析工具\function_calls.py` 和 `loguru_main.py`

## 依赖

### Python 模块
- **Python 3.12+**
- **loguru** - 第三方日志库

安装依赖：
```bash
pip install loguru
```

### Web 工具
- 现代浏览器（Chrome、Firefox、Edge 等）
- 无需任何服务器或构建工具，直接打开 HTML 文件即可使用

## 运行方式

### 生成日志（Python 主程序）

```bash
python loguru_main.py
```

可选：取消注释 `loguru_main.py` 或 `function_calls.py` 中的 `random.seed(42)` 可以复现相同的调用链。

### 使用日志分析工具

1. 在浏览器中打开 `log_analyzer.html`
2. 点击 "📂 打开日志文件" 按钮
3. 选择 `.log` 文件（如 `1.log`）
4. 在左侧面板选择线程 ID
5. 在右侧面板查看树状调用链

## 日志格式说明

### 输出格式

```
tid:{线程ID}|{调用栈路径}
tid:{线程ID}|{日志消息}
```

> 注：每条日志占用**两行**，第一行是调用栈路径，第二行是日志消息。

### 字段详解

| 字段 | 示例 | 说明 |
|------|------|------|
| **线程ID** | `tid:2136` | 当前执行线程的ID |
| **日志消息** | `▶ 进入函数: func_o | 当前深度: 1` | 具体的日志内容 |
| **调用栈路径** | `<module>@C:\...\loguru_main.py@51#main@C:\...\function_calls.py@436#...` | 完整的函数调用链 |

### 调用栈路径格式

```
函数名@文件路径@行号#函数名@文件路径@行号#...
```

每个调用帧包含：
- `函数名` - 被调用的函数
- `文件路径` - 完整绝对路径
- `行号` - 调用发生的行号
- `#` - 分隔符

### 日志消息类型

| 类型 | 示例 |
|------|------|
| 程序开始/结束分隔线 | `================================================================================` |
| 程序状态 | `程序开始执行 - 使用loguru日志库` |
| 随机选择函数 | `随机选择起始函数: func_d` |
| 函数进入 | `▶ 进入函数: func_d | 当前深度: 1` |
| 函数退出 | `◀ 退出函数: func_d | 当前深度: 20` |
| 达到最大深度 | `  达到最大深度,返回` |

### 调用深度机制

- 最大深度限制：**20**
- 达到最大深度时打印 `达到最大深度,返回` 并逐层返回
- 退出日志显示当前深度（返回值时深度不变，退出后才递减）

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

## 开发约定

- 使用 `loguru` 进行日志记录，统一使用 `logger.debug()` 级别
- 函数命名简单（`func_a` ~ `func_t`），便于测试
- 调用关系是随机的，用于模拟复杂调用场景
- 通过 `random.seed(42)` 可以复现调用链（代码中可能已注释）
- Web 工具使用纯前端技术，无外部依赖，易于部署和使用

## 注意事项

1. 日志中的调用栈路径非常长，使用 `log_analyzer.html` 工具可以更方便地分析
2. 每次运行会随机选择 3 个起始函数，如需复现结果，可以取消注释 `random.seed(42)`
3. Web 工具支持树状展开和折叠，适合分析深层调用链
4. 本项目使用 SVN 进行版本控制
