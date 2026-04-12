#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志分析工具 - Python/Tkinter 版
等价于 log_analyzer.html 的全部功能，仅使用 Python 标准库。

功能列表：
  1. 打开日志文件（自动检测 UTF-8 / UTF-16 LE / UTF-16 BE 编码）
  2. 左侧线程列表，点击切换线程
  3. 右侧日志内容区：树模式 / 列表模式切换
     - 树模式：按函数调用链展示，双击节点打开源码
     - 列表模式：按时间顺序显示用户消息，展开可查看调用栈，双击帧打开源码
  4. 底部源码查看器：带行号、高亮目标行、自动滚动到居中
  5. 映射目录：扫描 .py 文件，4 级策略匹配日志中的旧路径
  6. 可拖动分隔条（水平 / 垂直 PanedWindow）
"""

import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Optional


# ═══════════════════════════════════════════════════════════════
# 一、日志解析（纯函数，无 UI 依赖）
# ═══════════════════════════════════════════════════════════════

THREAD_RE = re.compile(r'^tid:(\d+)\|')


def read_file_smart(path: str) -> str:
    """智能编码读取文件，兼容 UTF-8 / UTF-16 LE / UTF-16 BE / GBK。"""
    with open(path, 'rb') as f:
        raw = f.read()
    # BOM 检测
    if raw[:3] == b'\xef\xbb\xbf':
        return raw[3:].decode('utf-8')
    if raw[:2] == b'\xff\xfe':
        return raw[2:].decode('utf-16-le')
    if raw[:2] == b'\xfe\xff':
        return raw[2:].decode('utf-16-be')
    # 启发式：前 40 字节奇数位大量为 0 → UTF-16 LE
    probe = raw[:40]
    zeros = sum(1 for i in range(1, len(probe), 2) if probe[i] == 0)
    if len(probe) > 4 and zeros / max(1, len(probe) // 2) > 0.25:
        return raw.decode('utf-16-le', errors='replace')
    for enc in ('utf-8', 'gbk', 'latin-1'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode('latin-1')


def parse_log_file(content: str) -> Dict[str, List[str]]:
    """按线程 ID 分组，返回 {tid: [原始行, ...]}。"""
    thread_map: Dict[str, List[str]] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        m = THREAD_RE.match(line)
        if m:
            tid = m.group(1)
            thread_map.setdefault(tid, []).append(line)
    return thread_map


def is_stack_line(content: str) -> bool:
    """调用栈行同时含有 @ 和 # 分隔符。"""
    return '@' in content and '#' in content


def parse_stack_trace(stack_str: str) -> List[dict]:
    """
    解析调用栈字符串（格式：函数名@文件路径@行号#函数名@...#）。
    返回 [{name, file_path, line_num}, ...]，顺序与原始帧顺序相同（外→内）。
    """
    stack_str = re.sub(r'#+\s*$', '', stack_str)
    frames = []
    for part in stack_str.split('#'):
        part = part.strip()
        if not part:
            continue
        segs = part.split('@')
        if len(segs) >= 3:
            frames.append({
                'name': segs[0],
                'file_path': segs[1],
                'line_num': segs[2],
            })
        else:
            frames.append({'name': part, 'file_path': '', 'line_num': ''})
    return frames


def _make_node(name: str, file_path: str = '', line_num: str = '') -> dict:
    return {'name': name, 'children': [], 'messages': [],
            'file_path': file_path, 'line_num': line_num}


def build_call_tree(lines: List[str]) -> dict:
    """
    从线程日志行列表增量构建调用树。
    与 HTML 版 buildCallTree() 逻辑完全一致：
      - 逐行解析调用栈，与上一条对比找到第一个差异位置
      - 差异位置之前的节点复用，之后的创建新节点
      - 消息行挂到当前路径最深节点
    """
    root = _make_node('root')
    last_frames: List[dict] = []
    path_nodes: List[dict] = []   # path_nodes[i] = 深度 i 的节点

    for line in lines:
        m = THREAD_RE.match(line)
        if not m:
            continue
        content = line[m.end():]

        if is_stack_line(content):
            frames = parse_stack_trace(content)

            # 找到与上一条调用栈的第一个不同位置
            diff = 0
            for i in range(min(len(frames), len(last_frames))):
                cf = f"{frames[i]['name']}@{frames[i]['file_path']}@{frames[i]['line_num']}"
                lf = f"{last_frames[i]['name']}@{last_frames[i]['file_path']}@{last_frames[i]['line_num']}"
                if cf == lf:
                    diff = i + 1
                else:
                    break

            # 确定父节点并截断路径
            if diff == 0 or diff - 1 >= len(path_nodes):
                parent = root
                path_nodes = []
            else:
                parent = path_nodes[diff - 1]
                path_nodes = path_nodes[:diff]

            # 从 diff 开始创建新节点
            for i in range(diff, len(frames)):
                f = frames[i]
                node = _make_node(f['name'], f['file_path'], f['line_num'])
                parent['children'].append(node)
                path_nodes.append(node)
                parent = node

            last_frames = frames

        else:
            # 用户消息行
            msg = content.strip()
            if msg and path_nodes:
                path_nodes[-1]['messages'].append(msg)

    return root


# ═══════════════════════════════════════════════════════════════
# 二、主应用
# ═══════════════════════════════════════════════════════════════

class LogAnalyzerApp:
    MAX_CACHED_FILES = 50

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('日志分析工具')
        self.root.geometry('1400x900')
        self.root.configure(bg='#f5f5f5')

        # 状态
        self.thread_map: Dict[str, List[str]] = {}
        self.selected_thread: Optional[str] = None
        self.view_mode: str = 'tree'          # 'tree' | 'list'
        self.mapping_files: Dict[str, str] = {}  # key → abs_path
        self.source_cache: Dict[str, str] = {}   # log_path → content
        self._item_meta: Dict[str, dict] = {}    # treeview item_id → meta

        self._source_visible = False

        self._configure_styles()
        self._build_ui()

    # ───────────────────────── TTK 样式 ──────────────────────────

    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # 日志内容 Treeview（深色背景）
        style.configure('Log.Treeview',
                         background='#1e1e1e',
                         foreground='#d4d4d4',
                         fieldbackground='#1e1e1e',
                         rowheight=26,
                         font=('Consolas', 11),
                         borderwidth=0)
        style.configure('Log.Treeview.Heading',
                         background='#2d2d2d',
                         foreground='#d4d4d4',
                         font=('Consolas', 11))
        style.map('Log.Treeview',
                  background=[('selected', '#264f78')],
                  foreground=[('selected', '#ffffff')])

        # 滚动条
        style.configure('Dark.Vertical.TScrollbar',
                         background='#3c3c3c', troughcolor='#1e1e1e',
                         arrowcolor='#858585')
        style.configure('Dark.Horizontal.TScrollbar',
                         background='#3c3c3c', troughcolor='#1e1e1e',
                         arrowcolor='#858585')

    # ───────────────────────── UI 构建 ───────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_main()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg='#2c3e50', height=44)
        hdr.pack(fill=tk.X, side=tk.TOP)
        hdr.pack_propagate(False)

        tk.Label(hdr, text='📊 日志分析工具',
                 bg='#2c3e50', fg='white',
                 font=('Microsoft YaHei', 12, 'bold')).pack(
                     side=tk.LEFT, padx=14, pady=8)

        self._mk_hdr_btn(hdr, '📂 打开日志文件', '#3498db', '#2980b9',
                          self.open_log_file).pack(side=tk.LEFT, padx=4, pady=7)

        self.btn_mapping = self._mk_hdr_btn(
            hdr, '📁 映射目录', '#27ae60', '#229954', self.select_mapping_dir)
        self.btn_mapping.pack(side=tk.LEFT, padx=4, pady=7)

    def _mk_hdr_btn(self, parent, text, bg, abg, cmd):
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg, activebackground=abg,
                         fg='white', activeforeground='white',
                         relief=tk.FLAT, padx=12, pady=3,
                         cursor='hand2',
                         font=('Microsoft YaHei', 10))

    def _build_main(self):
        self.h_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL,
                                       sashwidth=6, sashrelief=tk.FLAT,
                                       bg='#cccccc', handlesize=0)
        self.h_paned.pack(fill=tk.BOTH, expand=True)
        self._build_left_panel()
        self._build_right_panel()

    # ── 左侧：线程列表 ──

    def _build_left_panel(self):
        lf = tk.Frame(self.h_paned, bg='white', bd=0)

        tk.Label(lf, text='线程列表',
                 bg='#ecf0f1', fg='#2c3e50',
                 font=('Microsoft YaHei', 10, 'bold'),
                 anchor='w', padx=10, pady=6).pack(fill=tk.X)

        inner = tk.Frame(lf, bg='white')
        inner.pack(fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(inner, orient=tk.VERTICAL)
        self.thread_lb = tk.Listbox(
            inner, yscrollcommand=sb.set,
            font=('Consolas', 12),
            selectbackground='#3498db', selectforeground='white',
            bg='white', fg='#2c3e50',
            bd=0, highlightthickness=0,
            activestyle='none')
        sb.config(command=self.thread_lb.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.thread_lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.thread_lb.bind('<<ListboxSelect>>', self._on_thread_select)

        self.thread_stats = tk.Label(lf, text='',
                                      bg='#f8f9fa', fg='#888',
                                      font=('Arial', 9),
                                      anchor='w', padx=10, pady=3)
        self.thread_stats.pack(fill=tk.X)

        self.h_paned.add(lf, minsize=120, width=200)

    # ── 右侧：日志内容 + 源码查看器 ──

    def _build_right_panel(self):
        rf = tk.Frame(self.h_paned, bg='white', bd=0)

        # 标题栏
        title_bar = tk.Frame(rf, bg='#ecf0f1', height=32)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        tk.Label(title_bar, text='日志内容',
                 bg='#ecf0f1', fg='#2c3e50',
                 font=('Microsoft YaHei', 10, 'bold'),
                 padx=10).pack(side=tk.LEFT, pady=5)

        # 模式切换按钮
        self.btn_list_mode = tk.Button(
            title_bar, text='📋 列表',
            command=lambda: self.set_view_mode('list'),
            font=('Arial', 9), padx=8, pady=2,
            relief=tk.GROOVE, cursor='hand2')
        self.btn_list_mode.pack(side=tk.RIGHT, padx=2, pady=4)

        self.btn_tree_mode = tk.Button(
            title_bar, text='🌲 树',
            command=lambda: self.set_view_mode('tree'),
            font=('Arial', 9), padx=8, pady=2,
            relief=tk.GROOVE, cursor='hand2',
            bg='#2c3e50', fg='white',
            activebackground='#34495e', activeforeground='white')
        self.btn_tree_mode.pack(side=tk.RIGHT, padx=2, pady=4)

        # 垂直分割：日志区 | 源码区
        self.v_paned = tk.PanedWindow(rf, orient=tk.VERTICAL,
                                       sashwidth=6, sashrelief=tk.FLAT,
                                       bg='#cccccc', handlesize=0)
        self.v_paned.pack(fill=tk.BOTH, expand=True)

        self._build_log_view()
        self._build_source_viewer()

        self.h_paned.add(rf, minsize=400)

    def _build_log_view(self):
        frm = tk.Frame(self.v_paned, bg='#1e1e1e', bd=0)

        sb_y = ttk.Scrollbar(frm, orient=tk.VERTICAL,
                              style='Dark.Vertical.TScrollbar')
        sb_x = ttk.Scrollbar(frm, orient=tk.HORIZONTAL,
                              style='Dark.Horizontal.TScrollbar')

        self.log_tree = ttk.Treeview(
            frm, style='Log.Treeview',
            yscrollcommand=sb_y.set,
            xscrollcommand=sb_x.set,
            selectmode='browse',
            show='tree')

        sb_y.config(command=self.log_tree.yview)
        sb_x.config(command=self.log_tree.xview)

        # 颜色标签
        self.log_tree.tag_configure('func',     foreground='#dcdcaa')
        self.log_tree.tag_configure('msg',      foreground='#ce9178')
        self.log_tree.tag_configure('list_msg', foreground='#ce9178')
        self.log_tree.tag_configure('frame',    foreground='#6a9955')
        self.log_tree.tag_configure('hint',     foreground='#858585')

        sb_x.pack(side=tk.BOTTOM, fill=tk.X)
        sb_y.pack(side=tk.RIGHT,  fill=tk.Y)
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 双击打开源码
        self.log_tree.bind('<Double-Button-1>', self._on_tree_double_click)

        self.v_paned.add(frm, minsize=100)

    def _build_source_viewer(self):
        self.src_frame = tk.Frame(self.v_paned, bg='#1e1e1e', bd=0)

        # 头部
        hdr = tk.Frame(self.src_frame, bg='#2d2d2d', height=30)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        self.src_title = tk.Label(
            hdr, text='', bg='#2d2d2d', fg='#d4d4d4',
            font=('Consolas', 10), anchor='w', padx=10)
        self.src_title.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(hdr, text='✕',
                  command=self._close_source_viewer,
                  bg='#2d2d2d', fg='#d4d4d4',
                  activebackground='#f44747', activeforeground='white',
                  relief=tk.FLAT, font=('Arial', 12),
                  padx=10, cursor='hand2').pack(side=tk.RIGHT)

        # 内容区（带行号的 Text）
        content_frm = tk.Frame(self.src_frame, bg='#1e1e1e')
        content_frm.pack(fill=tk.BOTH, expand=True)

        sb_y = ttk.Scrollbar(content_frm, orient=tk.VERTICAL,
                              style='Dark.Vertical.TScrollbar')
        sb_x = ttk.Scrollbar(content_frm, orient=tk.HORIZONTAL,
                              style='Dark.Horizontal.TScrollbar')

        self.src_text = tk.Text(
            content_frm,
            bg='#1e1e1e', fg='#d4d4d4',
            font=('Consolas', 11),
            wrap=tk.NONE,
            state=tk.DISABLED,
            cursor='arrow',
            yscrollcommand=sb_y.set,
            xscrollcommand=sb_x.set,
            selectbackground='#264f78',
            highlightthickness=0,
            bd=0,
            padx=6, pady=4)

        sb_y.config(command=self.src_text.yview)
        sb_x.config(command=self.src_text.xview)

        sb_x.pack(side=tk.BOTTOM, fill=tk.X)
        sb_y.pack(side=tk.RIGHT,  fill=tk.Y)
        self.src_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Text 标签
        self.src_text.tag_configure('lineno',
                                     foreground='#858585',
                                     font=('Consolas', 11))
        self.src_text.tag_configure('sep',
                                     foreground='#3c3c3c')
        self.src_text.tag_configure('highlight',
                                     background='#3a3a00',
                                     foreground='#ffffff')

        # 初始不显示（不加入 v_paned）
        self._source_visible = False

    # ───────────────────────── 事件处理 ──────────────────────────

    def open_log_file(self):
        path = filedialog.askopenfilename(
            title='选择日志文件',
            filetypes=[('日志文件', '*.log *.txt'), ('所有文件', '*.*')])
        if not path:
            return
        try:
            content = read_file_smart(path)
            self.thread_map = parse_log_file(content)
            self.selected_thread = None
            self._render_thread_list()
            self._clear_log_view()
        except Exception as e:
            messagebox.showerror('错误', f'读取文件失败：\n{e}')

    def select_mapping_dir(self):
        dirpath = filedialog.askdirectory(title='选择源码目录')
        if not dirpath:
            return

        self.mapping_files.clear()
        count = 0
        MAX_FILES = 1000
        MAX_SIZE  = 5 * 1024 * 1024  # 5 MB

        for root_dir, dirs, files in os.walk(dirpath):
            # 跳过隐藏目录和 node_modules
            dirs[:] = [d for d in dirs
                       if not d.startswith('.') and d != 'node_modules']
            for fname in files:
                if not fname.endswith('.py'):
                    continue
                abs_path = os.path.join(root_dir, fname)
                try:
                    if os.path.getsize(abs_path) > MAX_SIZE:
                        continue
                except OSError:
                    continue
                rel_path = os.path.relpath(abs_path, dirpath)
                # 同时用绝对路径、相对路径、文件名作为 key
                self.mapping_files[abs_path]            = abs_path
                self.mapping_files[rel_path]            = abs_path
                self.mapping_files[fname]               = abs_path
                count += 1
                if count >= MAX_FILES:
                    break
            if count >= MAX_FILES:
                break

        self.btn_mapping.config(
            text=f'📁 映射目录 ({count} 文件)',
            bg='#1e8449')
        messagebox.showinfo('映射目录',
                            f'成功加载 {count} 个 .py 文件\n目录：{dirpath}')

    def _on_thread_select(self, event=None):
        sel = self.thread_lb.curselection()
        if not sel:
            return
        text = self.thread_lb.get(sel[0])           # "tid:XXXXX"
        tid  = text[len('tid:'):]
        self.selected_thread = tid
        self._render_log_content()

    def set_view_mode(self, mode: str):
        self.view_mode = mode
        # 更新按钮样式
        if mode == 'tree':
            self.btn_tree_mode.config(bg='#2c3e50', fg='white',
                                       activebackground='#34495e')
            self.btn_list_mode.config(bg='#f0f0f0', fg='black',
                                       activebackground='#ddd')
        else:
            self.btn_list_mode.config(bg='#2c3e50', fg='white',
                                       activebackground='#34495e')
            self.btn_tree_mode.config(bg='#f0f0f0', fg='black',
                                       activebackground='#ddd')
        if self.selected_thread is not None:
            self._render_log_content()

    def _on_tree_double_click(self, event):
        item = self.log_tree.focus()
        meta = self._item_meta.get(item, {})
        fp   = meta.get('file_path', '')
        ln   = meta.get('line_num', '')
        if fp and ln:
            self._show_source_file(fp, ln)

    def _close_source_viewer(self):
        if self._source_visible:
            self.v_paned.forget(self.src_frame)
            self._source_visible = False

    # ───────────────────────── 渲染 ──────────────────────────────

    def _render_thread_list(self):
        self.thread_lb.delete(0, tk.END)
        for tid in sorted(self.thread_map.keys()):
            self.thread_lb.insert(tk.END, f'tid:{tid}')
        n = len(self.thread_map)
        self.thread_stats.config(text=f'共 {n} 个线程' if n else '')

    def _clear_log_view(self):
        self.log_tree.delete(*self.log_tree.get_children())
        self._item_meta.clear()

    def _render_log_content(self):
        self._clear_log_view()
        lines = self.thread_map.get(self.selected_thread, [])
        if not lines:
            return
        if self.view_mode == 'tree':
            self._render_tree_mode(lines)
        else:
            self._render_list_mode(lines)

    # ── 树模式 ──

    def _render_tree_mode(self, lines: List[str]):
        tree_root = build_call_tree(lines)
        for child in tree_root['children']:
            self._insert_tree_node(child, '')
        # 若根节点有消息（极少见），也插入
        for msg in tree_root['messages']:
            if msg:
                self.log_tree.insert('', 'end', text=f'  {msg}',
                                      tags=('msg',))

    def _insert_tree_node(self, node: dict, parent_id: str):
        # 构造显示文本
        fp   = node.get('file_path', '')
        ln   = node.get('line_num',  '')
        name = node['name']

        if fp:
            fname = os.path.basename(fp)
            dname = os.path.dirname(fp).replace('\\', '/')
            loc   = f'({dname}/{fname}:{ln})' if dname else f'({fname}:{ln})'
            label = f'{name}  {loc}'
        else:
            label = name

        own_id = self.log_tree.insert(
            parent_id, 'end',
            text=f'  {label}',
            tags=('func',),
            open=False)

        self._item_meta[own_id] = {'file_path': fp, 'line_num': ln}

        # 消息行
        for msg in node['messages']:
            if msg.strip():
                mid = self.log_tree.insert(own_id, 'end',
                                            text=f'      {msg}',
                                            tags=('msg',))
                self._item_meta[mid] = {}

        # 子节点递归
        for child in node['children']:
            self._insert_tree_node(child, own_id)

    # ── 列表模式 ──

    def _render_list_mode(self, lines: List[str]):
        seq         = 0
        last_stack  = None          # 最近一条调用栈原始字符串

        for line in lines:
            m = THREAD_RE.match(line)
            if not m:
                continue
            content = line[m.end():].strip()

            if is_stack_line(content):
                last_stack = content
                continue
            if not content:
                continue

            seq += 1
            # 顶层：消息
            msg_id = self.log_tree.insert(
                '', 'end',
                text=f'  {seq:>4}.  {content}',
                tags=('list_msg',),
                open=False)
            self._item_meta[msg_id] = {}

            # 子层：调用栈帧（逆序：最内层在最上方）
            if last_stack:
                frames = parse_stack_trace(last_stack)
                for idx, frame in enumerate(reversed(frames)):
                    fp    = frame['file_path']
                    ln    = frame['line_num']
                    fname = os.path.basename(fp) if fp else ''
                    dname = os.path.dirname(fp).replace('\\', '/') if fp else ''
                    if fname:
                        loc = f'({dname}/{fname}:{ln})' if dname else f'({fname}:{ln})'
                    else:
                        loc = ''
                    fid = self.log_tree.insert(
                        msg_id, 'end',
                        text=f'  {idx:>3}  {frame["name"]}  {loc}',
                        tags=('frame',))
                    self._item_meta[fid] = {'file_path': fp, 'line_num': ln}

    # ───────────────────────── 源码查看器 ────────────────────────

    def _resolve_file_path(self, log_path: str) -> Optional[str]:
        """4 级策略匹配日志中的路径到当前实际路径。"""
        if not self.mapping_files:
            return None
        fname = os.path.basename(log_path)

        # 策略 1：绝对路径精确匹配
        if log_path in self.mapping_files:
            return self.mapping_files[log_path]
        # 策略 2：文件名精确匹配
        if fname in self.mapping_files:
            return self.mapping_files[fname]
        # 策略 3：key 以 /filename 或 \filename 结尾
        for key, val in self.mapping_files.items():
            if key.endswith('/' + fname) or key.endswith('\\' + fname):
                return val
        # 策略 4：绝对路径以文件名结尾
        for key, val in self.mapping_files.items():
            if val.endswith(fname):
                return val
        return None

    def _show_source_file(self, log_path: str, line_num):
        try:
            line_num = int(str(line_num))
        except (ValueError, TypeError):
            line_num = 1

        # 显示源码查看器
        if not self._source_visible:
            self.v_paned.add(self.src_frame, minsize=120)
            self._source_visible = True

        self.src_title.config(text=f'{log_path}  (行 {line_num})')

        # 命中缓存
        if log_path in self.source_cache:
            self._render_source(self.source_cache[log_path], line_num)
            return

        # 查找实际文件
        real_path = self._resolve_file_path(log_path)
        if real_path is None and os.path.isfile(log_path):
            real_path = log_path

        if real_path:
            try:
                content = read_file_smart(real_path)
                self._cache_source(log_path, content)
                self._render_source(content, line_num)
                return
            except Exception as e:
                messagebox.showerror('错误', f'读取文件失败：\n{e}')
                return

        # 找不到 → 提示手动选择
        ans = messagebox.askyesno(
            '找不到源文件',
            f'无法找到源文件：\n{log_path}\n\n是否手动选择？')
        if not ans:
            return
        chosen = filedialog.askopenfilename(
            title='选择源文件',
            filetypes=[('Python 文件', '*.py'), ('所有文件', '*.*')])
        if not chosen:
            return
        try:
            content = read_file_smart(chosen)
            self._cache_source(log_path, content)
            self._render_source(content, line_num)
        except Exception as e:
            messagebox.showerror('错误', f'读取文件失败：\n{e}')

    def _cache_source(self, key: str, content: str):
        """简单 LRU：超出上限时淘汰最早的条目。"""
        if len(self.source_cache) >= self.MAX_CACHED_FILES:
            oldest = next(iter(self.source_cache))
            del self.source_cache[oldest]
        self.source_cache[key] = content

    def _render_source(self, content: str, target_line: int):
        """渲染源码：带行号列、高亮目标行、滚动到居中。"""
        code_lines = content.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        total = len(code_lines)
        target_line = max(1, min(target_line, total))

        gutter_w = len(str(total))      # 行号宽度

        self.src_text.config(state=tk.NORMAL)
        self.src_text.delete('1.0', tk.END)

        for i, line_text in enumerate(code_lines, start=1):
            lineno_str = f'{i:>{gutter_w}}'
            sep_str    = ' │ '

            self.src_text.insert(tk.END, lineno_str, 'lineno')
            self.src_text.insert(tk.END, sep_str,    'sep')

            if i == target_line:
                self.src_text.insert(tk.END, line_text + '\n', 'highlight')
            else:
                self.src_text.insert(tk.END, line_text + '\n')

        self.src_text.config(state=tk.DISABLED)

        # 滚动使目标行居中（延迟 50ms 确保布局完成）
        def do_scroll():
            widget_h = self.src_text.winfo_height()
            # 用 dlineinfo 获取行高（更准确）
            try:
                info = self.src_text.dlineinfo(f'{target_line}.0')
                line_h = info[3] if info else 20
            except Exception:
                line_h = 20
            visible_lines = max(1, widget_h // line_h)
            start_line    = max(1, target_line - visible_lines // 2)
            fraction      = (start_line - 1) / max(1, total)
            self.src_text.yview_moveto(fraction)

        self.src_text.after(50, do_scroll)


# ═══════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    root = tk.Tk()
    app  = LogAnalyzerApp(root)
    root.mainloop()
