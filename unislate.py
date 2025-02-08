import curses
import sys
import os
import re
import signal

try:
    import pyperclip
except ImportError:
    pyperclip = None

##############################
# Editor Settings
##############################

TAB_SPACES = " " * 4  # 4 пробела вместо табуляции

##############################
# Синтаксическая подсветка
##############################

# --- Python ---
PYTHON_KEYWORDS = {
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
    'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
    'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
    'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield'
}
RE_PY_COMMENT = re.compile(r"#.*")
RE_PY_STRING = re.compile(r'(\'[^\']*\'|"[^"]*")')
RE_PY_KEYWORD = re.compile(r'\b(' + '|'.join(PYTHON_KEYWORDS) + r')\b')
RE_PY_NUMBER  = re.compile(r'\b\d+(\.\d+)?\b')

def highlight_python_line(line, colors):
    """Подсветка для Python."""
    segments = []
    tokens = []
    for m in RE_PY_COMMENT.finditer(line):
        tokens.append((m.start(), m.end(), "comment"))
    for m in RE_PY_STRING.finditer(line):
        tokens.append((m.start(), m.end(), "string"))
    for m in RE_PY_KEYWORD.finditer(line):
        tokens.append((m.start(), m.end(), "keyword"))
    for m in RE_PY_NUMBER.finditer(line):
        tokens.append((m.start(), m.end(), "number"))
    if not tokens:
        return [(line, colors["default"])]
    tokens.sort(key=lambda x: x[0])
    last_idx = 0
    for start, end, ttype in tokens:
        if start > last_idx:
            segments.append((line[last_idx:start], colors["default"]))
        segments.append((line[start:end], colors.get(ttype, colors["default"])))
        last_idx = end
    if last_idx < len(line):
        segments.append((line[last_idx:], colors["default"]))
    return segments

# --- JavaScript ---
JS_KEYWORDS = {
    'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
    'default', 'delete', 'do', 'else', 'export', 'extends', 'finally', 'for',
    'function', 'if', 'import', 'in', 'instanceof', 'let', 'new', 'return',
    'super', 'switch', 'this', 'throw', 'try', 'typeof', 'var', 'void',
    'while', 'with', 'yield'
}
RE_JS_COMMENT = re.compile(r"(//.*|/\*.*?\*/)", re.DOTALL)
RE_JS_STRING = re.compile(r'(".*?"|\'.*?\'|`.*?`)', re.DOTALL)
RE_JS_KEYWORD = re.compile(r'\b(' + '|'.join(JS_KEYWORDS) + r')\b')
RE_JS_NUMBER  = re.compile(r'\b\d+(\.\d+)?\b')

# --- C ---
C_KEYWORDS = {
    'auto','break','case','char','const','continue','default','do','double',
    'else','enum','extern','float','for','goto','if','inline','int','long',
    'register','restrict','return','short','signed','sizeof','static','struct',
    'switch','typedef','union','unsigned','void','volatile','while'
}
RE_C_COMMENT = re.compile(r"(//.*|/\*.*?\*/)", re.DOTALL)
RE_C_STRING = re.compile(r'(".*?"|\'.*?\')', re.DOTALL)
RE_C_KEYWORD = re.compile(r'\b(' + '|'.join(C_KEYWORDS) + r')\b')
RE_C_NUMBER  = re.compile(r'\b\d+(\.\d+)?\b')

# --- Java ---
JAVA_KEYWORDS = {
    'abstract','assert','boolean','break','byte','case','catch','char','class',
    'const','continue','default','do','double','else','enum','extends','final',
    'finally','float','for','goto','if','implements','import','instanceof','int',
    'interface','long','native','new','package','private','protected','public',
    'return','short','static','strictfp','super','switch','synchronized','this',
    'throw','throws','transient','try','void','volatile','while'
}
RE_JAVA_COMMENT = re.compile(r"(//.*|/\*.*?\*/)", re.DOTALL)
RE_JAVA_STRING = re.compile(r'(".*?"|\'.*?\')', re.DOTALL)
RE_JAVA_KEYWORD = re.compile(r'\b(' + '|'.join(JAVA_KEYWORDS) + r')\b')
RE_JAVA_NUMBER  = re.compile(r'\b\d+(\.\d+)?\b')

# Функция-генератор подсветки для языков с похожей структурой
def highlight_line_generic(line, comment_re, string_re, keyword_re, number_re, colors):
    segments = []
    tokens = []
    for m in comment_re.finditer(line):
        tokens.append((m.start(), m.end(), "comment"))
    for m in string_re.finditer(line):
        tokens.append((m.start(), m.end(), "string"))
    for m in keyword_re.finditer(line):
        tokens.append((m.start(), m.end(), "keyword"))
    for m in number_re.finditer(line):
        tokens.append((m.start(), m.end(), "number"))
    if not tokens:
        return [(line, colors["default"])]
    tokens.sort(key=lambda x: x[0])
    last_idx = 0
    for start, end, ttype in tokens:
        if start > last_idx:
            segments.append((line[last_idx:start], colors["default"]))
        segments.append((line[start:end], colors.get(ttype, colors["default"])))
        last_idx = end
    if last_idx < len(line):
        segments.append((line[last_idx:], colors["default"]))
    return segments

def highlight_js_line(line, colors):
    return highlight_line_generic(line, RE_JS_COMMENT, RE_JS_STRING, RE_JS_KEYWORD, RE_JS_NUMBER, colors)

def highlight_c_line(line, colors):
    return highlight_line_generic(line, RE_C_COMMENT, RE_C_STRING, RE_C_KEYWORD, RE_C_NUMBER, colors)

def highlight_java_line(line, colors):
    return highlight_line_generic(line, RE_JAVA_COMMENT, RE_JAVA_STRING, RE_JAVA_KEYWORD, RE_JAVA_NUMBER, colors)

# --- Markdown и базовая подсветка по умолчанию ---
RE_MD_HEADER = re.compile(r'^(#{1,6})\s*(.*)$')
RE_MD_LINK = re.compile(r'(\[.*?\]\(.*?\))')

def highlight_markdown_line(line, colors):
    segments = []
    m = RE_MD_HEADER.match(line)
    if m:
        header_marks, header_text = m.groups()
        segments.append((header_marks + " ", colors["default"]))
        segments.append((header_text, colors["md_header"]))
        return segments
    parts = []
    last = 0
    for m in RE_MD_LINK.finditer(line):
        start, end = m.span()
        if start > last:
            parts.append((line[last:start], "default"))
        parts.append((line[start:end], "md_link"))
        last = end
    if last < len(line):
        parts.append((line[last:], "default"))
    for text, typ in parts:
        segments.append((text, colors.get(typ, colors["default"])))
    if not segments:
        segments = [(line, colors["default"])]
    return segments

def default_highlight_line(line, colors):
    return [(line, colors["default"])]

HIGHLIGHT_FUNCTIONS = {
    ".py": highlight_python_line,
    ".js": highlight_js_line,
    ".ts": highlight_js_line,
    ".jsx": highlight_js_line,
    ".tsx": highlight_js_line,
    ".c": highlight_c_line,
    ".cpp": highlight_c_line,
    ".cc": highlight_c_line,
    ".cxx": highlight_c_line,
    ".h": highlight_c_line,
    ".hpp": highlight_c_line,
    ".java": highlight_java_line,
    ".md": highlight_markdown_line,
    # Для остальных файлов используем базовую подсветку:
    ".html": default_highlight_line,
    ".htm": default_highlight_line,
    ".css": default_highlight_line,
    ".json": default_highlight_line,
    ".xml": default_highlight_line,
    ".rb": default_highlight_line,
    ".php": default_highlight_line,
    ".go": default_highlight_line,
    ".rs": default_highlight_line,
    ".sh": default_highlight_line,
    ".sql": default_highlight_line,
    ".ini": default_highlight_line,
    ".cfg": default_highlight_line,
    ".yaml": default_highlight_line,
    ".yml": default_highlight_line,
    ".bat": default_highlight_line,
    ".ps1": default_highlight_line,
    ".swift": default_highlight_line,
    ".kt": default_highlight_line,
    ".lua": default_highlight_line,
    ".pl": default_highlight_line,
    ".r": default_highlight_line,
    ".scala": default_highlight_line,
    ".vb": default_highlight_line,
    ".fs": default_highlight_line,
    ".erl": default_highlight_line,
    ".ex": default_highlight_line,
    ".exs": default_highlight_line,
}

##############################
# Другие функции редактора
##############################

def load_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
    except Exception:
        lines = [""]
    if not lines:
        lines = [""]
    return lines

def save_file(filename, lines):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

def prompt_user(stdscr, prompt):
    curses.echo()
    height, width = stdscr.getmaxyx()
    stdscr.move(height - 1, 0)
    stdscr.clrtoeol()
    stdscr.addstr(height - 1, 0, prompt)
    stdscr.refresh()
    inp = stdscr.getstr(height - 1, len(prompt), width - len(prompt) - 1)
    curses.noecho()
    try:
        return inp.decode("utf-8").strip()
    except Exception:
        return ""

def prompt_user_cancelable(stdscr, prompt):
    height, width = stdscr.getmaxyx()
    input_str = ""
    pos = len(prompt)
    stdscr.move(height - 1, 0)
    stdscr.clrtoeol()
    stdscr.addstr(height - 1, 0, prompt)
    stdscr.refresh()
    while True:
        ch = stdscr.getch()
        if ch == 27:
            return None
        elif ch in (curses.KEY_ENTER, 10, 13):
            break
        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            if len(input_str) > 0:
                input_str = input_str[:-1]
                pos -= 1
                stdscr.move(height - 1, pos)
                stdscr.delch(height - 1, pos)
        else:
            if 0 <= ch < 256:
                c = chr(ch)
                if c.isprintable():
                    input_str += c
                    stdscr.addstr(height - 1, pos, c)
                    pos += 1
        stdscr.refresh()
    return input_str.strip()

# ASCII art и приветственное сообщение
ASCII_ART = r"""
  _    _       _     _       _       
 | |  | |     (_)   | |     | |      
 | |  | |_ __  _ ___| | __ _| |_ ___ 
 | |  | | '_ \| / __| |/ _` | __/ _ \
 | |__| | | | | \__ \ | (_| | ||  __/
  \____/|_| |_|_|___/_|\__,_|\__\___|
                                                   
developed by qwez with ♥️
"""

def draw_welcome(stdscr, colors):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    ascii_lines = ASCII_ART.strip("\n").splitlines()
    total_lines = len(ascii_lines) + 3
    start_y = max((height - total_lines) // 2, 0)
    for idx, line in enumerate(ascii_lines):
        x = max((width - len(line)) // 2, 0)
        try:
            stdscr.addstr(start_y + idx, x, line, colors["default"])
        except curses.error:
            pass
    prompt_msg = "Press any key to start..."
    try:
        stdscr.addstr(start_y + len(ascii_lines) + 2, max((width - len(prompt_msg)) // 2, 0),
                      prompt_msg, colors["default"])
    except curses.error:
        pass
    stdscr.refresh()
    key = stdscr.getch()
    if key == 17:
        curses.endwin()
        sys.exit(0)

##############################
# Функции для выделения
##############################

def get_line_selection_range(line_no, sel_start, sel_end, line_length):
    if sel_start is None or sel_end is None:
        return None
    (sy, sx) = sel_start
    (ey, ex) = sel_end
    if (sy, sx) > (ey, ex):
        sy, sx, ey, ex = ey, ex, sy, sx
    if line_no < sy or line_no > ey:
        return None
    if sy == ey:
        return (min(sx, ex), max(sx, ex))
    if line_no == sy:
        return (sx, line_length)
    elif line_no == ey:
        return (0, ex)
    else:
        return (0, line_length)

def apply_selection_to_segment(text, seg_start, seg_end, sel_start, sel_end, base_attr):
    result = []
    if seg_end <= sel_start or seg_start >= sel_end:
        return [(text, base_attr)]
    if seg_start < sel_start:
        prefix_len = sel_start - seg_start
        result.append((text[:prefix_len], base_attr))
        text = text[prefix_len:]
        seg_start = sel_start
    overlap = min(seg_end, sel_end) - seg_start
    if overlap > 0:
        result.append((text[:overlap], base_attr | curses.A_REVERSE))
        text = text[overlap:]
        seg_start += overlap
    if seg_start < seg_end:
        result.append((text, base_attr))
    return result

def get_selected_text(lines, sel_start, sel_end):
    (sy, sx) = sel_start
    (ey, ex) = sel_end
    if (sy, sx) > (ey, ex):
        sy, sx, ey, ex = ey, ex, sy, sx
    if sy == ey:
        return lines[sy][sx:ex]
    result = []
    result.append(lines[sy][sx:])
    for i in range(sy + 1, ey):
        result.append(lines[i])
    result.append(lines[ey][:ex])
    return "\n".join(result)

def remove_selected_text(lines, sel_start, sel_end):
    (sy, sx) = sel_start
    (ey, ex) = sel_end
    if (sy, sx) > (ey, ex):
        sy, sx, ey, ex = ey, ex, sy, sx
    if sy == ey:
        lines[sy] = lines[sy][:sx] + lines[sy][ex:]
        return lines
    first_part = lines[sy][:sx]
    last_part = lines[ey][ex:]
    new_line = first_part + last_part
    new_lines = lines[:sy] + [new_line] + lines[ey+1:]
    return new_lines

##############################
# Отрисовка редактора с номерами строк и выделением
##############################

def draw_editor(stdscr, lines, cursor_y, cursor_x, offset_y, offset_x, filename, colors, sel_start, sel_end):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    ext = os.path.splitext(filename)[1].lower() if filename else ""
    highlighter = HIGHLIGHT_FUNCTIONS.get(ext, default_highlight_line)
    
    line_num_width = len(str(len(lines))) + 2
    
    for i, line in enumerate(lines[offset_y: offset_y + height - 1]):
        actual_line = i + offset_y
        line_number = f"{actual_line+1}".rjust(line_num_width - 1) + " "
        try:
            stdscr.addstr(i, 0, line_number, curses.A_DIM)
        except curses.error:
            pass
        
        segments = highlighter(line, colors)
        x = line_num_width
        sel_range = get_line_selection_range(actual_line, sel_start, sel_end, len(line))
        current_index = 0
        for text, attr in segments:
            seg_start = current_index
            seg_end = current_index + len(text)
            current_index = seg_end
            if sel_range is None:
                if x + len(text) > width:
                    text = text[:max(width - x, 0)]
                try:
                    stdscr.addstr(i, x, text, attr)
                except curses.error:
                    pass
                x += len(text)
            else:
                sub_segments = apply_selection_to_segment(text, seg_start, seg_end, sel_range[0], sel_range[1], attr)
                for sub_text, sub_attr in sub_segments:
                    if x + len(sub_text) > width:
                        sub_text = sub_text[:max(width - x, 0)]
                    try:
                        stdscr.addstr(i, x, sub_text, sub_attr)
                    except curses.error:
                        pass
                    x += len(sub_text)
                    
    # Статусная строка – только информация, без управления.
    # Добавлено указание, если файл новый (еще не существует).
    if filename is None:
        status_filename = "untitled (new)"
    elif not os.path.exists(filename):
        status_filename = f"{filename} (new)"
    else:
        status_filename = filename

    status = f"{status_filename} | Ln {cursor_y+1}/{len(lines)} | Col {cursor_x+1} | EDIT"
    try:
        stdscr.addstr(height - 1, 0, status[:width].ljust(width), colors["default"])
    except curses.error:
        pass
    scr_y = cursor_y - offset_y
    scr_x = (cursor_x - offset_x) + line_num_width
    if 0 <= scr_y < height - 1 and 0 <= scr_x < width:
        try:
            stdscr.move(scr_y, scr_x)
        except curses.error:
            pass
    stdscr.refresh()

##############################
# Main Editor Function
##############################

def main(stdscr):
    # Инициализация curses – используем raw() чтобы Ctrl+C не обрабатывался терминалом
    curses.noecho()
    curses.raw()
    stdscr.keypad(True)
    curses.curs_set(1)
    curses.start_color()
    curses.use_default_colors()
    stdscr.bkgd(' ', curses.A_NORMAL)
    
    signal.signal(signal.SIGINT, lambda sig, frame: None)

    # Инициализация цветовых пар
    curses.init_pair(1, curses.COLOR_WHITE, -1)    # default
    curses.init_pair(2, curses.COLOR_CYAN, -1)       # keyword (жирный)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)     # string
    curses.init_pair(4, curses.COLOR_GREEN, -1)      # comment
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)    # number
    curses.init_pair(6, curses.COLOR_BLUE, -1)       # md_header
    curses.init_pair(7, curses.COLOR_CYAN, -1)       # md_link

    colors = {
        "default": curses.A_NORMAL,
        "keyword": curses.color_pair(2) | curses.A_BOLD,
        "string": curses.color_pair(3),
        "comment": curses.color_pair(4),
        "number": curses.color_pair(5),
        "md_header": curses.color_pair(6) | curses.A_BOLD,
        "md_link": curses.color_pair(7)
    }

    # Загрузка файла или приветственный экран
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        lines = load_file(filename)
    else:
        draw_welcome(stdscr, colors)
        filename = None
        lines = [""]

    cursor_y = 0
    cursor_x = 0
    offset_y = 0
    offset_x = 0
    modified = False
    undo_stack = []
    redo_stack = []
    clipboard = ""  # Внутренний буфер

    # Параметры выделения
    select_mode = False
    selection_start = None
    selection_end = None

    def get_state():
        return (list(lines), cursor_y, cursor_x, offset_y, offset_x, modified)

    def set_state(state):
        nonlocal lines, cursor_y, cursor_x, offset_y, offset_x, modified
        lines, cursor_y, cursor_x, offset_y, offset_x, modified = state

    def record_undo():
        undo_stack.append(get_state())
        redo_stack.clear()

    def cancel_selection():
        nonlocal select_mode, selection_start, selection_end
        select_mode = False
        selection_start = None
        selection_end = None

    while True:
        height, width = stdscr.getmaxyx()
        draw_editor(stdscr, lines, cursor_y, cursor_x, offset_y, offset_x, filename, colors, selection_start, selection_end)
        key = stdscr.getch()

        if key == curses.KEY_RESIZE:
            stdscr.clear()
            offset_y = 0
            offset_x = 0
            continue

        # Выход: Ctrl+Q (код 17)
        if key == 17:
            if modified:
                stdscr.move(height - 1, 0)
                stdscr.clrtoeol()
                stdscr.addstr(height - 1, 0, "Unsaved changes! Quit without saving? (y/n): ", colors["default"])
                stdscr.refresh()
                confirm = stdscr.getch()
                if confirm not in (ord('y'), ord('Y')):
                    continue
            break

        elif key == 19:  # Сохранение Ctrl+S
            if not filename:
                name = prompt_user_cancelable(stdscr, "Save as: ")
                if name is None or name == "":
                    continue
                filename = name
            try:
                save_file(filename, lines)
                modified = False
                msg = f"Saved: {filename}"
                try:
                    stdscr.addstr(height - 1, 0, msg[:width].ljust(width), colors["default"])
                except curses.error:
                    pass
                stdscr.refresh()
                curses.napms(800)
            except Exception:
                pass

        elif key == 26:  # Undo: Ctrl+Z
            if undo_stack:
                redo_stack.append(get_state())
                set_state(undo_stack.pop())
                cancel_selection()
            else:
                curses.beep()

        elif key == 25:  # Redo: Ctrl+Y
            if redo_stack:
                undo_stack.append(get_state())
                set_state(redo_stack.pop())
                cancel_selection()
            else:
                curses.beep()

        # Обработка обычных стрелок — сбрасываем выделение
        elif key == curses.KEY_UP:
            cancel_selection()
            if cursor_y > 0:
                cursor_y -= 1
                if cursor_y < offset_y:
                    offset_y = cursor_y
                cursor_x = min(cursor_x, len(lines[cursor_y]))
            else:
                curses.beep()
        elif key == curses.KEY_DOWN:
            cancel_selection()
            if cursor_y < len(lines) - 1:
                cursor_y += 1
                if cursor_y >= offset_y + height - 1:
                    offset_y += 1
                cursor_x = min(cursor_x, len(lines[cursor_y]))
            else:
                curses.beep()
        elif key == curses.KEY_LEFT:
            cancel_selection()
            if cursor_x > 0:
                cursor_x -= 1
            elif cursor_y > 0:
                cursor_y -= 1
                cursor_x = len(lines[cursor_y])
                if cursor_y < offset_y:
                    offset_y = cursor_y
            else:
                curses.beep()
        elif key == curses.KEY_RIGHT:
            cancel_selection()
            if cursor_x < len(lines[cursor_y]):
                cursor_x += 1
            elif cursor_y < len(lines) - 1:
                cursor_y += 1
                cursor_x = 0
                if cursor_y >= offset_y + height - 1:
                    offset_y += 1
            else:
                curses.beep()

        # Обработка Shift+стрелок для выделения
        elif key in (getattr(curses, "KEY_SLEFT", -1),):
            if not select_mode:
                select_mode = True
                selection_start = (cursor_y, cursor_x)
            if cursor_x > 0:
                cursor_x -= 1
            elif cursor_y > 0:
                cursor_y -= 1
                cursor_x = len(lines[cursor_y])
            else:
                curses.beep()
            selection_end = (cursor_y, cursor_x)
        elif key in (getattr(curses, "KEY_SRIGHT", -1),):
            if not select_mode:
                select_mode = True
                selection_start = (cursor_y, cursor_x)
            if cursor_x < len(lines[cursor_y]):
                cursor_x += 1
            elif cursor_y < len(lines) - 1:
                cursor_y += 1
                cursor_x = 0
            else:
                curses.beep()
            selection_end = (cursor_y, cursor_x)
        elif key in (getattr(curses, "KEY_SUP", -1),):
            if not select_mode:
                select_mode = True
                selection_start = (cursor_y, cursor_x)
            if cursor_y > 0:
                cursor_y -= 1
                cursor_x = min(cursor_x, len(lines[cursor_y]))
            else:
                curses.beep()
            selection_end = (cursor_y, cursor_x)
        elif key in (getattr(curses, "KEY_SDOWN", -1),):
            if not select_mode:
                select_mode = True
                selection_start = (cursor_y, cursor_x)
            if cursor_y < len(lines) - 1:
                cursor_y += 1
                cursor_x = min(cursor_x, len(lines[cursor_y]))
            else:
                curses.beep()
            selection_end = (cursor_y, cursor_x)

        # Копирование: Ctrl+C
        elif key == 3:
            if selection_start is not None and selection_end is not None and selection_start != selection_end:
                clipboard = get_selected_text(lines, selection_start, selection_end)
                cancel_selection()
            else:
                clipboard = lines[cursor_y]
            if pyperclip:
                try:
                    pyperclip.copy(clipboard)
                except Exception:
                    pass

        # Вырезание: Ctrl+X
        elif key == 24:
            record_undo()
            if selection_start is not None and selection_end is not None and selection_start != selection_end:
                clipboard = get_selected_text(lines, selection_start, selection_end)
                lines = remove_selected_text(lines, selection_start, selection_end)
                (cursor_y, cursor_x) = selection_start
                cancel_selection()
                modified = True
            else:
                clipboard = lines[cursor_y]
                if len(lines) > 1:
                    del lines[cursor_y]
                    if cursor_y >= len(lines):
                        cursor_y = len(lines) - 1
                    cursor_x = min(cursor_x, len(lines[cursor_y]))
                else:
                    lines[0] = ""
                    cursor_x = 0
                modified = True
            if pyperclip:
                try:
                    pyperclip.copy(clipboard)
                except Exception:
                    pass

        # Вставка: Ctrl+V
        elif key == 22:
            if pyperclip:
                try:
                    clipboard = pyperclip.paste()
                except Exception:
                    pass
            if clipboard:
                record_undo()
                if selection_start is not None and selection_end is not None and selection_start != selection_end:
                    lines = remove_selected_text(lines, selection_start, selection_end)
                    cursor_y, cursor_x = selection_start
                    cancel_selection()
                if "\n" in clipboard:
                    clipboard_lines = clipboard.split("\n")
                else:
                    clipboard_lines = [clipboard]
                if len(clipboard_lines) == 1:
                    line = lines[cursor_y]
                    lines[cursor_y] = line[:cursor_x] + clipboard_lines[0] + line[cursor_x:]
                    cursor_x += len(clipboard_lines[0])
                else:
                    line = lines[cursor_y]
                    before = line[:cursor_x]
                    after = line[cursor_x:]
                    new_lines = [before + clipboard_lines[0]] + clipboard_lines[1:-1] + [clipboard_lines[-1] + after]
                    lines[cursor_y:cursor_y+1] = new_lines
                    cursor_y = cursor_y + len(new_lines) - 1
                    cursor_x = len(clipboard_lines[-1])
                modified = True

        # Backspace
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if cursor_x > 0:
                record_undo()
                line = lines[cursor_y]
                lines[cursor_y] = line[:cursor_x - 1] + line[cursor_x:]
                cursor_x -= 1
                modified = True
                cancel_selection()
            elif cursor_y > 0:
                record_undo()
                prev_line = lines[cursor_y - 1]
                curr_line = lines[cursor_y]
                cursor_x = len(prev_line)
                lines[cursor_y - 1] = prev_line + curr_line
                del lines[cursor_y]
                cursor_y -= 1
                modified = True
                cancel_selection()

        # Enter
        elif key in (curses.KEY_ENTER, 10, 13):
            record_undo()
            line = lines[cursor_y]
            indent_match = re.match(r'(\s*)', line)
            indent = indent_match.group(1) if indent_match else ""
            new_line = indent + line[cursor_x:]
            lines[cursor_y] = line[:cursor_x]
            lines.insert(cursor_y + 1, new_line)
            cursor_y += 1
            cursor_x = len(indent)
            if cursor_y >= offset_y + height - 1:
                offset_y += 1
            modified = True
            cancel_selection()

        # Tab
        elif key == 9:
            record_undo()
            line = lines[cursor_y]
            lines[cursor_y] = line[:cursor_x] + TAB_SPACES + line[cursor_x:]
            cursor_x += len(TAB_SPACES)
            modified = True
            cancel_selection()

        # Печатаемые символы
        else:
            try:
                ch = chr(key)
            except ValueError:
                continue
            if ch.isprintable():
                record_undo()
                line = lines[cursor_y]
                lines[cursor_y] = line[:cursor_x] + ch + line[cursor_x:]
                cursor_x += 1
                if cursor_x >= offset_x + width:
                    offset_x += 1
                modified = True
                cancel_selection()

    stdscr.clear()
    stdscr.refresh()

def main_wrapper():
    curses.wrapper(main)

if __name__ == '__main__':
    main_wrapper()
