# 📘 PyLogCodeTrace User Manual

> **Version**: 1.0  
> **Last Updated**: April 4, 2026

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Requirements](#2-system-requirements)
3. [Installation Guide](#3-installation-guide)
4. [Quick Start Tutorial](#4-quick-start-tutorial)
5. [Using the Log Analyzer](#5-using-the-log-analyzer)
6. [Advanced Features](#6-advanced-features)
7. [Integrating with Your Own Project](#7-integrating-with-your-own-project)
8. [Configuration Options](#8-configuration-options)
9. [Troubleshooting](#9-troubleshooting)
10. [FAQ](#10-faq)
11. [Appendix](#11-appendix)

---

## 1. Introduction

### What is PyLogCodeTrace?

PyLogCodeTrace is a **Python runtime call chain visualization tool** that automatically captures function call relationships during code execution and displays them as an interactive tree diagram. It helps developers quickly understand complex program flows without spending hours on debugging.

### Key Features

| Feature | Description |
|---------|-------------|
| **Automatic Call Stack Capture** | Records complete function call paths with file names and line numbers |
| **Thread ID Tracking** | Groups logs by thread for multi-threaded applications |
| **Tree Visualization** | Converts flat logs into collapsible/expandable tree structures |
| **Source Code Viewer** | Click any function in the tree to view the corresponding source code |
| **Pure Frontend Web Tool** | No server required; opens directly in any modern browser |
| **Zero Code Modification** | Works with your existing code—just add log entry/exit statements |

### Typical Use Cases

- ✅ Learning and understanding unfamiliar codebases
- ✅ Debugging complex call chains
- ✅ Code review and architecture analysis
- ✅ Teaching and demonstrating program execution flow
- ✅ Performance bottleneck identification (by analyzing call depth)

---

## 2. System Requirements

### Python Environment

| Component | Requirement |
|-----------|-------------|
| **Python Version** | 3.12 or higher |
| **Operating System** | Windows, macOS, or Linux |
| **Required Package** | `loguru` (any version) |

### Web Browser

| Browser | Minimum Version |
|---------|-----------------|
| Google Chrome | 80+ |
| Mozilla Firefox | 75+ |
| Microsoft Edge | 80+ |
| Safari | 13+ |

**Note**: The web analyzer tool is a standalone HTML file with no external dependencies. It works offline and requires no server.

---

## 3. Installation Guide

### Step 1: Clone or Download the Project

```bash
# If using SVN
svn checkout <repository_url> PyLogCodeTrace

# Or simply copy the project files to your desired location
```

### Step 2: Install Python Dependencies

```bash
cd PyLogCodeTrace
pip install loguru
```

### Step 3: Verify Installation

```bash
python loguru_main.py
```

You should see enhanced log output in the console with call stacks and thread IDs.

**Example Output**:
```
tid:2136|<module>@loguru_main.py@51#main@function_calls.py@436#
tid:2136|================================================================================
tid:2136|<module>@loguru_main.py@51#main@function_calls.py@450#
tid:2136|Randomly selected start function: func_o
tid:2136|<module>@loguru_main.py@51#main@function_calls.py@453#func_o@function_calls.py@316#log_entry@function_calls.py@19#
tid:2136|▶ Enter: func_o | Current Depth: 1
...
```

---

## 4. Quick Start Tutorial

### Scenario: Analyzing the Demo Project

#### Step 1: Run the Demo Program

```bash
python loguru_main.py > demo.log
```

This runs the demo program and saves the output to `demo.log`.

#### Step 2: Open the Web Analyzer

1. Navigate to the project directory
2. Double-click `log_analyzer.html` or open it in your browser:

```bash
# On Windows
start log_analyzer.html

# On macOS
open log_analyzer.html

# On Linux
xdg-open log_analyzer.html
```

#### Step 3: Load the Log File

1. Click the **"📂 Open Log File"** button in the top toolbar
2. Select `demo.log` from the file dialog
3. Wait for the file to parse (usually instant for small files)

#### Step 4: Explore the Call Tree

1. In the **left panel**, you'll see a list of thread IDs (e.g., `tid:2136`)
2. Click on a thread ID to select it
3. In the **right panel**, the call tree will appear:

```
▶ main() (function_calls.py:436)
  ├─ ▶ func_o() (function_calls.py:316)
  │   ├─ ▶ func_t() (function_calls.py:416)
  │   │   ├─ ▶ func_q() (function_calls.py:356)
  │   │   │   └─ ...
  │   │   └─ ...
  │   └─ ...
  └─ ...
```

#### Step 5: Navigate the Tree

- **Expand/Collapse**: Click the ▶ arrow next to any node
- **View Details**: Hover over function names to see full file paths and line numbers
- **Check Statistics**: The bottom status bar shows total node count

---

## 5. Using the Log Analyzer

### 5.1 Interface Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 PyLogCodeTrace    [📂 Open Log File]  [📁 Map Directory]    │
├──────────────┬──────────────────────────────────────────────────┤
│  Thread List  │  Call Tree Display                             │
│              │                                                 │
│  ○ tid:2136  │  ▶ main()                                       │
│  ○ tid:3452  │     ├─ ▶ func_o()                               │
│              │     │   ├─ ▶ func_t()                           │
│              │     │   │   └─ ...                              │
│              │                                                 │
├──────────────┴──────────────────────────────────────────────────┤
│  Total 2 threads                     Total 245 nodes            │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Button Functions

| Button | Function |
|--------|----------|
| **📂 Open Log File** | Opens a file dialog to select a `.log` file |
| **📁 Map Directory** | Opens a directory picker to load source code files for viewing |

### 5.3 Thread List Panel (Left)

- Displays all unique thread IDs found in the log file
- Click a thread ID to view its call tree in the right panel
- The selected thread is highlighted in blue
- Bottom status shows total thread count

### 5.4 Call Tree Panel (Right)

- Displays the hierarchical call tree for the selected thread
- **Syntax Highlighting**:
  - Function names: Yellow (`func_o`)
  - File names: Yellow with underline (clickable)
  - Line numbers: Red
- **Interactive Features**:
  - Click ▶ to expand/collapse child nodes
  - Click file names to open the source code viewer
  - Scroll to navigate long call trees

### 5.5 Source Code Viewer

When you click a file name in the call tree:

```
┌─────────────────────────────────────────────────────────────────┐
│  function_calls.py (Line 316)                            [×]    │
├─────────────────────────────────────────────────────────────────┤
│  314 │ def func_o():                                           │
│  315 │     """Function O - may call func_e, func_l, or func_t"""│
│  316 │▶    log_entry("func_o")  ← Highlighted in yellow        │
│  317 │                                                          │
│  318 │     if should_return():                                  │
│  319 │         logger.debug("  Max depth reached, returning")   │
└─────────────────────────────────────────────────────────────────┘
```

**Features**:
- Automatically highlights the line where the call occurred
- Scrolls to center the highlighted line in the viewport
- Supports viewing multiple files (LRU cache, max 50 files)

---

## 6. Advanced Features

### 6.1 Mapping Source Code Directories

To enable direct source code viewing without manual file selection:

1. Click **"📁 Map Directory"**
2. Select a directory containing your `.py` files
3. The tool will scan and index all Python files (up to 1000 files, max 5MB each)

**Benefits**:
- Click any file name in the call tree to instantly view its source
- No need to manually select files each time
- Supports nested directory structures

### 6.2 Handling Multi-Threaded Logs

If your application uses multiple threads:

```
tid:2136|... (Thread 1 logs)
tid:3452|... (Thread 2 logs)
tid:7890|... (Thread 3 logs)
```

The analyzer automatically groups logs by thread ID. Simply click the desired thread in the left panel to view its isolated call tree.

### 6.3 Exporting Call Trees

Currently, the tool displays call trees in the browser. To export:

- **Copy as Text**: Select and copy the tree from the browser
- **Screenshot**: Use browser screenshot tools (Ctrl+Shift+S in Chrome)
- **Print**: Use browser print function (Ctrl+P) to save as PDF

---

## 7. Integrating with Your Own Project

### 7.1 Step-by-Step Integration Guide

#### Step 1: Add Log Entry/Exit to Your Functions

Modify your functions to include entry and exit logs:

```python
from loguru import logger

def my_function():
    logger.debug(f"▶ Enter: my_function")
    
    # Your business logic here
    result = some_operation()
    
    logger.debug(f"◀ Exit: my_function")
    return result
```

#### Step 2: Copy PyLogCodeTrace Files

Copy these files to your project:
- `loguru_main.py` (or integrate its logic into your entry point)
- `log_analyzer.html` (for analysis)

#### Step 3: Modify the Entry Point

Edit `loguru_main.py` to import your main function:

```python
# Change this line:
from function_calls import main as function_calls_main

# To your module:
from your_module import main as your_main
```

#### Step 4: Run and Capture Logs

```bash
# Run and save to file
python loguru_main.py > my_project.log

# Or run directly in your project
python -m your_module > my_project.log
```

#### Step 5: Analyze with Web Tool

1. Open `log_analyzer.html`
2. Load `my_project.log`
3. Explore your project's call tree!

### 7.2 Minimal Integration Example

Here's a minimal example to get started:

```python
# my_app.py
from loguru import logger

call_depth = 0
MAX_DEPTH = 10

def log_entry(func_name):
    global call_depth
    call_depth += 1
    logger.debug(f"▶ Enter: {func_name} | Depth: {call_depth}")

def log_exit(func_name):
    global call_depth
    logger.debug(f"◀ Exit: {func_name} | Depth: {call_depth}")
    call_depth -= 1

def func_a():
    log_entry("func_a")
    if call_depth < MAX_DEPTH:
        func_b()
    log_exit("func_a")

def func_b():
    log_entry("func_b")
    logger.debug("  Processing data...")
    log_exit("func_b")

def main():
    logger.debug("=" * 60)
    logger.debug("My Application Started")
    logger.debug("=" * 60)
    func_a()
    logger.debug("Application Finished")

if __name__ == "__main__":
    main()
```

**Enhance with loguru_main.py**:

```python
# run_with_trace.py
import sys
from loguru import logger
from my_app import main as app_main

def get_call_depth1(record):
    stack = ""
    frame = sys._getframe(4)
    while frame:
        filename = frame.f_code.co_filename
        stack = frame.f_code.co_name + "@" + filename + "@" + str(frame.f_lineno) + "#" + stack
        frame = frame.f_back
    record["extra"]["depth"] = stack
    return True

fmt = (
    "<cyan>tid:{thread.id}</cyan>|<yellow>{extra[depth]:<2}</yellow>\n"
    "<cyan>tid:{thread.id}</cyan>|<level>{message}</level>"
)

logger.remove()
logger.add(sink=sys.stdout, level="DEBUG", format=fmt, colorize=True, filter=get_call_depth1)

app_main()
```

Run it:
```bash
python run_with_trace.py > output.log
```

---

## 8. Configuration Options

### 8.1 Adjust Maximum Call Depth

In `function_calls.py` (or your code):

```python
MAX_DEPTH = 20  # Increase for deeper analysis, decrease for performance
```

**Recommendation**:
- Small projects: 10-15
- Medium projects: 20-30
- Large projects: 30-50 (watch for log file size)

### 8.2 Reproduce Call Chains

To get consistent results across runs:

```python
import random
random.seed(42)  # Uncomment or add this line
```

### 8.3 Customize Log Format

Edit the format string in `loguru_main.py`:

```python
fmt = (
    "<cyan>tid:{thread.id}</cyan>|<yellow>{extra[depth]:<2}</yellow>\n"
    "<cyan>tid:{thread.id}</cyan>|<level>{message}</level>"
)
```

**Available Variables**:
- `{thread.id}` - Thread ID
- `{extra[depth]}` - Call stack path
- `{level}` - Log level (DEBUG, INFO, etc.)
- `{message}` - Your log message
- `{time}` - Timestamp
- `{name}` - Logger name

**Example with Timestamp**:
```python
fmt = (
    "<green>{time:HH:mm:ss}</green> | "
    "<cyan>tid:{thread.id}</cyan>|<yellow>{extra[depth]}</yellow>\n"
    "<cyan>tid:{thread.id}</cyan>|<level>{message}</level>"
)
```

### 8.4 Save Logs to File

Modify the logger to write to a file instead of (or in addition to) stdout:

```python
# Add file output
logger.add(
    sink="output.log",
    level="DEBUG",
    format=fmt,
    filter=get_call_depth1
)
```

---

## 9. Troubleshooting

### Problem 1: No Call Stack in Logs

**Symptom**: Logs show only `tid:XXXX|` without the call stack path.

**Solution**:
- Ensure `get_call_depth1` function is properly configured as a filter
- Check that `sys._getframe(4)` has the correct frame offset (may need adjustment)
- Verify that `logger.add()` includes `filter=get_call_depth1`

### Problem 2: Web Tool Shows "No Threads Found"

**Symptom**: After loading a log file, the left panel is empty.

**Solution**:
- Ensure the log file uses the correct format: `tid:{ID}|{content}`
- Check for file encoding issues (must be UTF-8)
- Verify the file is not empty

### Problem 3: Source Code Viewer Shows "File Not Found"

**Symptom**: Clicking a file name shows an error message.

**Solution**:
- Use the **"📁 Map Directory"** button to load your source code directory
- Ensure the file paths in the log match the actual file structure
- Manually select the file using the file picker button in the viewer

### Problem 4: Logs Are Too Large

**Symptom**: Log file grows rapidly, causing browser slowdown.

**Solution**:
- Reduce `MAX_DEPTH` to limit call chain depth
- Filter logs by level (e.g., only log specific functions)
- Use log rotation:

```python
logger.add("output.log", rotation="10 MB")  # Auto-rotate at 10MB
```

### Problem 5: Multi-Threaded Logs Are Mixed

**Symptom**: Call trees from different threads are interleaved.

**Solution**:
- The web tool automatically separates logs by thread ID
- Click individual thread IDs in the left panel to view isolated call trees
- If threads are not separated, ensure each thread has a unique ID in the log format

---

## 10. FAQ

### Q1: Can I use this with languages other than Python?

**A**: Currently, the log generation part (`loguru_main.py`) is Python-specific. However, the web analyzer (`log_analyzer.html`) can parse any log file that follows the `tid:{ID}|{content}` format, regardless of the source language. You would need to implement equivalent call stack capture logic in your target language.

### Q2: Does this work with async/await code?

**A**: Yes, but with limitations. The `sys._getframe()` approach works for synchronous calls. For async code, you may need to use `asyncio.current_task()` or similar mechanisms to track async call chains.

### Q3: How large of a log file can the web tool handle?

**A**: The tool can comfortably handle log files up to ~50MB with thousands of nodes. For very large files (>100MB), consider:
- Filtering logs before analysis
- Splitting logs into smaller chunks
- Increasing browser memory limits

### Q4: Can I customize the tree colors and styling?

**A**: Yes! Open `log_analyzer.html` in a text editor and modify the CSS section. Key classes to modify:
- `.func-name` - Function name color
- `.file-name` - File name color
- `.line-number` - Line number color
- `.tree-node-header` - Node background and hover effects

### Q5: Is there a way to search for specific functions in the call tree?

**A**: The current version doesn't have a built-in search function. However, you can:
- Use your browser's Find feature (Ctrl+F) to search the rendered tree
- Filter the log file before loading it into the tool

### Q6: Can I compare call trees from two different runs?

**A**: The tool currently displays one thread at a time. To compare:
- Open two browser windows with the tool
- Load different log files in each
- Alternatively, merge logs with distinct thread IDs and switch between them

---

## 11. Appendix

### A. Log Format Reference

```
tid:{thread_id}|{call_stack_path}
tid:{thread_id}|{log_message}
```

**Call Stack Path Format**:
```
function_name@file_path@line_number#function_name@file_path@line_number#...
```

**Example**:
```
tid:2136|<module>@C:\project\main.py@50#func_a@C:\project\module.py@25#func_b@C:\project\module.py@40#
tid:2136|▶ Enter: func_b | Current Depth: 3
```

### B. File Structure

```
PyLogCodeTrace/
├── function_calls.py          # Demo business functions
├── loguru_main.py             # Log enhancement entry point
├── log_analyzer.html          # Web visualization tool
├── 1.log                      # Sample log file
├── README.md                  # Chinese documentation
├── README_en.md               # English documentation
├── USER_MANUAL_en.md          # This file (English user manual)
├── QWEN.md                    # Project context
└── .svn/                      # SVN version control
```

### C. Keyboard Shortcuts (Browser)

| Shortcut | Function |
|----------|----------|
| `Ctrl+F` | Search in page (browser native) |
| `Ctrl+O` | Open file (if supported by browser) |
| `Ctrl+P` | Print/Save as PDF |
| `Ctrl+Shift+I` | Open Developer Tools (for debugging) |

### D. Performance Tips

1. **Reduce Log Volume**: Only log critical functions
2. **Limit Depth**: Set `MAX_DEPTH` to the minimum necessary
3. **Use File Output**: Write to file instead of console for large runs
4. **Split Analysis**: Analyze different modules separately
5. **Clear Cache**: The web tool caches up to 50 files; refresh the page to clear

### E. Support & Resources

- **Project Context**: See `QWEN.md` for detailed technical background
- **Issues & Feedback**: Submit via SVN repository
- **Contributions**: Pull requests and suggestions welcome

---

**Thank you for using PyLogCodeTrace!**

For questions or support, please refer to the project repository.
