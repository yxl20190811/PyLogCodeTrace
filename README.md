# 📊 PyLogCodeTrace - Make Code Learning Easier

> **Core Value**: Automatically captures runtime call relationships and displays them as a clear tree diagram. No more tedious debugging—let the code reveal its own execution flow!

---

## 🎯 Background & Pain Points

### How do you learn a new codebase?

Beyond reading documentation, the most effective approach is **combining documentation with actual code execution**!

Log files represent the runtime execution path of your source code. However, traditional logs have several problems:

| Pain Point | Description |
|------------|-------------|
| ❌ **Hard to Understand** | Raw logs are flat text; call relationships require mental reconstruction |
| ❌ **Inefficient** | Requires repeated debugging, tracing, and cross-referencing code |
| ❌ **Scattered Information** | Call stacks, thread IDs, and log messages are spread across multiple lines |
| ❌ **No Visualization** | Deep call chains (e.g., 20 levels) are nearly impossible to analyze manually |

### 💡 Our Solution

PyLogCodeTrace provides a **toolchain that quickly combines code with execution flow**:

1. **Run Code** → Use `loguru_main.py` to invoke your business code, automatically enriching logs with call stacks, thread IDs, and more
2. **Analyze Logs** → Use `log_analyzer.html` to load runtime logs and automatically parse call relationships
3. **Visualize** → Get a runtime call tree for any feature, **fully aligned with the actual code**

```
Raw Logs (Hard to Read)          →         Call Tree (Clear Visualization)
─────────────────────────────────────────────────────────────────────────────
tid:2136|func_a@...@36#                    ▶ main()
tid:2136|▶ Enter: func_a                    ├─ ▶ func_o()
tid:2136|func_a@...@45#func_b@...           │   ├─ ▶ func_t()
tid:2136|▶ Enter: func_b                    │   │   ├─ ▶ func_q()
...                                          │   │   │   └─ ...
```

**Fully aligned with actual code execution! No more repetitive debugging or cross-referencing. The program automatically displays runtime call relationships in a clear tree diagram!**

---

## 📁 Project Structure

```
PyLogCodeTrace/
├── function_calls.py          # Business function module (20 interconnected functions)
├── loguru_main.py             # Log formatting config + program entry point
├── log_analyzer.html          # Web-based log visualization tool (pure frontend)
├── 1.log                      # Sample log file (open directly with the analyzer)
├── README.md                  # This documentation
├── README_en.md               # English documentation (this file)
├── QWEN.md                    # Project context documentation
└── .svn/                      # SVN version control directory
```

---

## 🏗️ Core Architecture

### Three-Module Workflow

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│  function_calls.py  │────▶│   loguru_main.py     │────▶│  log_analyzer.html  │
│                     │     │                      │     │                     │
│ • Business logic    │     │ • Log format config  │     │ • Log file parsing  │
│ • Inter-function    │     │ • Call stack capture │     │ • Call tree build   │
│   calls             │     │ • Thread ID logging  │     │ • Tree visualization│
│ • Call depth count  │     │ • Program entry      │     │ • Source code viewer│
└─────────────────────┘     └──────────────────────┘     └─────────────────────┘
      Business Layer              Log Enhancement Layer         Visualization Layer
```

### Module Responsibilities

| Module | Responsibility | Tech Stack | Lines of Code |
|--------|----------------|------------|---------------|
| **function_calls.py** | Business function definitions, inter-call logic, depth control | Python 3.12+ | ~480 |
| **loguru_main.py** | Log format configuration, call stack capture, entry point | Python + loguru | ~55 |
| **log_analyzer.html** | Log parsing, call tree construction, visualization | HTML5 + CSS3 + JS | ~1141 |

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install loguru
```

> Only the Python part requires a dependency. The web analyzer needs no server or build tools.

### Step 2: Run the Program to Generate Logs

```bash
python loguru_main.py
```

This outputs enhanced-format logs to the console, including:
- Thread ID
- Complete call stack path
- Function enter/exit messages
- Call depth information

### Step 3: Use the Visualization Tool to Analyze

1. Open `log_analyzer.html` in a browser (double-click or drag into browser)
2. Click **"📂 Open Log File"** button
3. Select a `.log` file (e.g., `1.log`)
4. Select a thread ID in the left panel
5. View the **tree-structured call chain** in the right panel

### Step 4: Map Source Code Directory (Optional)

Click the **"📁 Map Directory"** button and select a directory containing `.py` files. After that, clicking a filename in the call tree opens the corresponding source code in the bottom viewer, automatically highlighting the line where the call occurred.

---

## 📖 Log Format Explained

### Output Format

Each log entry occupies **two lines**:

```
tid:{thread_id}|{call_stack_path}
tid:{thread_id}|{log_message}
```

### Call Stack Path Format

```
function_name@file_path@line_number#function_name@file_path@line_number#...
```

| Field | Example | Description |
|-------|---------|-------------|
| **Function Name** | `func_o` | The called function |
| **File Path** | `C:\hh\svn\yy\study\PyLogCodeTrace\function_calls.py` | Full absolute path |
| **Line Number** | `316` | Line where the call occurs |
| **#** | Separator | Call chain from outer to inner |

### Call Stack Example

```
tid:2136|<module>@loguru_main.py@51#main@function_calls.py@453#func_o@function_calls.py@329#func_t@function_calls.py@427#func_q@function_calls.py@369#func_b@function_calls.py@67#func_e@function_calls.py@129#func_j@function_calls.py@227#func_g@function_calls.py@165#func_a@function_calls.py@45#func_b@function_calls.py@67#func_e@function_calls.py@129#func_j@function_calls.py@216#log_entry@function_calls.py@19#
tid:2136|▶ Enter: func_e | Current Depth: 10
```

**Call Chain Breakdown** (from outer to inner):
```
<module>(loguru_main.py:51)
  └─ main(function_calls.py:453)
       └─ func_o(function_calls.py:329)
            └─ func_t(function_calls.py:427)
                 └─ func_q(function_calls.py:369)
                      └─ func_b(function_calls.py:67)
                           └─ func_e(function_calls.py:129)
                                └─ func_j(function_calls.py:227)
                                     └─ func_g(function_calls.py:165)
                                          └─ func_a(function_calls.py:45)
                                               └─ func_b(function_calls.py:67)
                                                    └─ func_e(function_calls.py:129)
                                                         └─ func_j(function_calls.py:216)
                                                              └─ log_entry(function_calls.py:19) ← Current execution point
```

### Log Message Types

| Type | Example | Description |
|------|---------|-------------|
| Separator | `================================================================================` | Program start/end markers |
| Program State | `Program started - using loguru logger` | Key events |
| Random Selection | `Randomly selected start function: func_o` | Entry function selection |
| Function Enter | `▶ Enter: func_o \| Current Depth: 1` | Function call entry |
| Function Exit | `◀ Exit: func_d \| Current Depth: 20` | Function return |
| Max Depth Reached | `  Max depth reached, returning` | Depth limit triggered |

---

## 🔧 Core Implementation Principles

### 1. Call Stack Capture (`loguru_main.py`)

Uses Python's `sys._getframe()` to capture the call stack:

```python
def get_call_depth1(record):
    """Get current call depth (fast version)"""
    stack = ""
    frame = sys._getframe(4)  # Skip get_call_depth and caller frames
    while frame:
        filename = frame.f_code.co_filename
        stack = frame.f_code.co_name + "@" + filename + "@" + str(frame.f_lineno) + "#" + stack
        frame = frame.f_back
    record["extra"]["depth"] = stack
    return True
```

**Key Points**:
- `sys._getframe(4)` skips internal loguru frames, starting capture from business code
- Traverses the entire call chain via `frame.f_back`
- Injects the call stack into loguru's `extra` field

### 2. Log Format Configuration (`loguru_main.py`)

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

**Output Effect**:
```
tid:2136|func_a@...@36#func_b@...@56#
tid:2136|▶ Enter: func_b | Current Depth: 2
```

### 3. Business Function Call Logic (`function_calls.py`)

Each business function follows a unified pattern:

```python
def func_x():
    log_entry("func_x")          # Log entry
    
    if should_return():          # Check depth limit
        logger.debug("  Max depth reached, returning")
        log_exit("func_x")
        return
    
    choice = random.choice(['a', 'b', 'c'])  # Randomly select next function
    if choice == 'a':
        func_a()
    # ... other branches
    
    log_exit("func_x")           # Log exit
```

**Key Features**:
- Maximum depth limit: **20** (controlled via `MAX_DEPTH` constant)
- Call relationships generated randomly (reproducible via `random.seed(42)`)
- Global call depth counter (`call_depth`)

### 4. Call Tree Construction Algorithm (`log_analyzer.html`)

The frontend converts flat logs into a tree structure using a **path matching algorithm**:

```javascript
function buildCallTree(lines, threadIdRegex) {
    const root = { name: 'root', children: [], messages: [], depth: -1 };
    let lastStackTrace = [];
    let pathNodes = [];  // Path stack to track all ancestors of current node

    lines.forEach(line => {
        const stackTrace = parseStackTrace(content);

        // Compare with previous call stack, find first difference
        let diffIndex = 0;
        for (let i = 0; i < Math.min(stackTrace.length, lastStackTrace.length); i++) {
            if (current_frame === previous_frame) {
                diffIndex = i + 1;
            } else {
                break;
            }
        }

        // Create new nodes starting from diffIndex
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

**Algorithm Features**:
- Automatically identifies call chain branches and returns
- Maintains a path stack to ensure correct parent node assignment
- Supports deep nesting (tested up to 20 levels)

---

## 🎨 Web Tool Features

### Core Features

| Feature | Description |
|---------|-------------|
| **Log File Parsing** | Automatically parses `tid:{ID}|{content}` format logs |
| **Thread ID Grouping** | Left panel groups logs by thread ID |
| **Tree Call Chain** | Right panel displays complete call chain in tree structure |
| **Node Collapse/Expand** | Click arrows to collapse/expand child nodes |
| **Syntax Highlighting** | Function names (yellow), file names (yellow), line numbers (red) |
| **Real-time Statistics** | Bottom status bar shows node count |
| **Source Code Viewer** | Click file names to open corresponding source code with automatic line highlighting |
| **Directory Mapping** | Map source code directories to automatically load `.py` files |

### Interface Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 PyLogCodeTrace    [📂 Open Log File]  [📁 Map Directory]    │
├──────────────┬──────────────────────────────────────────────────┤
│  Thread List  │  Log Content                                    │
│              │                                                 │
│  ○ tid:2136  │  ▶ main() (function_calls.py:436)               │
│              │     ├─ ▶ func_o() (function_calls.py:316)        │
│              │     │   ├─ ▶ func_t() (function_calls.py:416)    │
│              │     │   │   └─ ...                               │
│              │     │   └─ ...                                   │
│              │     └─ ...                                       │
│              │                                                 │
├──────────────┴──────────────────────────────────────────────────┤
│  Total 1 threads                     Total 245 nodes            │
├─────────────────────────────────────────────────────────────────┤
│  Source Code Viewer                                             │
│  function_calls.py (Line 316)                            [×]    │
│  314 │ def func_o():                                           │
│  315 │     """Function O - may call func_e, func_l, or func_t"""│
│  316 │▶    log_entry("func_o")  ← Highlighted                  │
│  317 │                                                          │
│  318 │     if should_return():                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Draggable Splitter

- The splitter between left and right panels supports **mouse dragging**
- Minimum width: 120px
- Maximum width: container width - 200px

---

## 📊 Example Call Chain Analysis

Using actual execution from `1.log`:

### First Call Chain (Depth 20)

```
main()
  └─ func_o()           ← Randomly selected start function
       └─ func_t()
            └─ func_q()
                 └─ func_b()
                      └─ func_e()
                           └─ func_j()
                                └─ func_g()
                                     └─ func_a()
                                          └─ func_b()
                                               └─ func_e()
                                                    └─ func_j()
                                                         └─ func_d()
                                                              └─ func_a()
                                                                   └─ func_c()
                                                                        └─ func_d()
                                                                             └─ func_i()
                                                                                  └─ func_f()
                                                                                       └─ func_g()
                                                                                            └─ func_a()
                                                                                                 └─ func_d()  ← Max depth 20 reached
```

### Call Characteristics

- **Depth**: 20 levels (reaches maximum limit)
- **Branches**: Each function randomly selects the next call
- **Return**: After reaching max depth, returns layer by layer, printing `◀ Exit function`

---

## 🛠️ How to Apply to Your Project

### Scenario: Learning Call Relationships in a System

#### Step 1: Prepare Business Code

Ensure your business code uses `loguru` for logging, or add enter/exit logs at key functions:

```python
from loguru import logger

def your_function():
    logger.debug(f"▶ Enter: your_function")
    # ... business logic
    logger.debug(f"◀ Exit: your_function")
```

#### Step 2: Integrate Log Enhancement Module

Copy `loguru_main.py` to your project and modify the import path:

```python
# Change to your business module
from your_module import main as your_main
```

#### Step 3: Run and Generate Logs

```bash
python loguru_main.py > output.log
```

#### Step 4: Analyze with Visualization Tool

1. Open `log_analyzer.html`
2. Load `output.log`
3. View the call tree

#### Step 5: Map Source Code Directory

Click **"📁 Map Directory"**, select your source code directory. Then click file names in the call tree to view the corresponding code.

---

## ⚙️ Configuration & Customization

### Adjust Maximum Call Depth

Modify in `function_calls.py`:

```python
MAX_DEPTH = 20  # Change to your desired depth
```

### Reproduce Call Chains

Uncomment `random.seed(42)`:

```python
# At the end of function_calls.py
if __name__ == "__main__":
    random.seed(42)  # Uncomment to reproduce results
    main()
```

### Customize Log Format

Modify the `fmt` variable in `loguru_main.py`:

```python
fmt = (
    "<cyan>tid:{thread.id}</cyan>|<yellow>{extra[depth]:<2}</yellow>\n"
    "<cyan>tid:{thread.id}</cyan>|<level>{message}</level>"
)
```

### Adjust Call Stack Capture Start Point

Modify the parameter of `sys._getframe(4)`:

```python
frame = sys._getframe(4)  # Increase or decrease to adjust capture start point
```

---

## 📋 Dependencies

### Python Modules

| Dependency | Version | Description |
|------------|---------|-------------|
| **Python** | 3.12+ | Runtime environment |
| **loguru** | Any | Third-party logging library |

Installation:
```bash
pip install loguru
```

### Web Tool

| Requirement | Description |
|-------------|-------------|
| **Browser** | Modern browsers (Chrome, Firefox, Edge, etc.) |
| **External Dependencies** | None (pure frontend) |
| **Server** | Not required (open HTML file directly) |

---

## 📝 Development Conventions

### Python Code

- Use `logger.debug()` uniformly for logging
- Simple function naming (`func_a` ~ `func_t`) for testing
- Random call relationships to simulate complex scenarios
- Use `random.seed(42)` to reproduce call chains

### Log Format

- Each log entry occupies **two lines** (call stack + message)
- Call stack paths separated by `#`, format: `function_name@file_path@line_number`
- Function enter/exit logs appear in pairs

### Web Tool

- Pure frontend implementation, no build tools
- Native JavaScript (no framework dependencies)
- LRU cache support (max 50 files)
- File mapping limit: 1000 `.py` files, max 5MB per file

---

## ⚠️ Notes

1. **Call stack paths in logs are very long**; using `log_analyzer.html` is recommended instead of manual reading
2. **Each run randomly selects start functions**; uncomment `random.seed(42)` to reproduce results
3. **Web tool supports tree expansion and collapse**, suitable for analyzing deep call chains
4. **Browser security restrictions**: Cannot read local files directly; use "Map Directory" or manually select source files
5. **Call depth counter is global**: May need adjustment for multi-threaded scenarios

---

## 🎓 Learning Tips

### How to Use This Tool to Learn New Systems

1. **Run the Target System**: Use this tool's log enhancement feature to run the target system
2. **View Call Trees**: Use the visualization tool to view actual runtime call relationships
3. **Cross-reference Source Code**: Click file names in the call tree to jump to corresponding code lines
4. **Understand Business Flow**: Understand program execution flow through call trees, instead of reading code line by line

### Comparison

| Traditional Approach | Using This Tool |
|----------------------|-----------------|
| Read code line by line | View actual runtime call chains |
| Manual debugging and tracing | Automatically record complete call relationships |
| Mentally construct call trees | Visual tree display |
| Easy to miss call paths | Records all paths completely |
| Requires repeated debugging verification | One run, clear display |

---

## 📄 License

This project is for learning and research purposes, no specific license applied.

---

## 📮 Feedback & Support

For questions or suggestions, please contact via:

- Check `QWEN.md` for more project context
- Submit issues or suggestions through the SVN repository

---

**Last Updated**: April 4, 2026
