import curses
import sys
import os
import re

##############################
# Editor Settings
##############################

TAB_SPACES = " " * 4  # 4 spaces instead of a tab

##############################
# Python Syntax Highlighting
##############################

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
    """Syntax highlighting for Python: comments, strings, keywords, and numbers."""
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

##############################
# Markdown and Default Highlighting
##############################

RE_MD_HEADER = re.compile(r'^(#{1,6})\s*(.*)$')
RE_MD_LINK = re.compile(r'(\[.*?\]\(.*?\))')

def highlight_markdown_line(line, colors):
    """
    Basic highlighting for Markdown: headers and links.
    """
    segments = []
    m = RE_MD_HEADER.match(line)
    if m:
        header_marks, header_text = m.groups()
        segments.append((header_marks + " ", colors["default"]))
        segments.append((header_text, colors["md_header"]))
        return segments
    # Highlight links
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
    ".md": highlight_markdown_line,
    ".js": default_highlight_line,
    ".ts": default_highlight_line,
    ".jsx": default_highlight_line,
    ".tsx": default_highlight_line,
    ".html": default_highlight_line,
    ".htm": default_highlight_line,
    ".css": default_highlight_line,
    ".json": default_highlight_line,
    ".xml": default_highlight_line,
    ".c": default_highlight_line,
    ".cpp": default_highlight_line,
    ".cc": default_highlight_line,
    ".cxx": default_highlight_line,
    ".h": default_highlight_line,
    ".hpp": default_highlight_line,
    ".java": default_highlight_line,
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
# Other Editor Functions
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
    """
    Prompt the user for input on the status line.
    Returns an empty string if no input is provided.
    """
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

# ASCII art and welcome messages
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
    """Welcome screen with controls. Press any key to start (or Ctrl+Q to quit)."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    ascii_lines = ASCII_ART.strip("\n").splitlines()
    
    # Calculate starting y-coordinate so that the ascii art and messages are centered vertically.
    total_lines = len(ascii_lines) + 3  # ASCII art + blank line + controls line + "Press any key..." message
    start_y = max((height - total_lines) // 2, 0)
    
    # Display ASCII art centered horizontally
    for idx, line in enumerate(ascii_lines):
        x = max((width - len(line)) // 2, 0)
        try:
            stdscr.addstr(start_y + idx, x, line, colors["default"])
        except curses.error:
            pass

    # Display controls info below the ASCII art
    controls_msg = "Controls: Ctrl+S: Save, Ctrl+Q: Quit"
    try:
        stdscr.addstr(start_y + len(ascii_lines), max((width - len(controls_msg)) // 2, 0), controls_msg, colors["default"])
    except curses.error:
        pass

    # Display the prompt message
    prompt_msg = "Press any key to start..."
    try:
        stdscr.addstr(start_y + len(ascii_lines) + 2, max((width - len(prompt_msg)) // 2, 0), prompt_msg, colors["default"])
    except curses.error:
        pass

    stdscr.refresh()
    key = stdscr.getch()
    # Allow quitting from the welcome screen using Ctrl+Q (ASCII 17)
    if key == 17:
        curses.endwin()
        sys.exit(0)

def draw_editor(stdscr, lines, cursor_y, cursor_x, offset_y, offset_x, filename, colors):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    ext = os.path.splitext(filename)[1].lower() if filename else ""
    highlighter = HIGHLIGHT_FUNCTIONS.get(ext, default_highlight_line)
    for i, line in enumerate(lines[offset_y: offset_y + height - 1]):
        if ext == ".md":
            segments = highlight_markdown_line(line, colors)
        else:
            segments = highlighter(line, colors)
        x = 0
        for text, attr in segments:
            if x + len(text) > width:
                text = text[: max(width - x, 0)]
            try:
                stdscr.addstr(i, x, text, attr)
            except curses.error:
                pass
            x += len(text)
    mode = "EDIT"
    status = f"{filename if filename else 'untitled'} | Ln {cursor_y+1}/{len(lines)} | {mode} | Ctrl+S: Save, Ctrl+Q: Quit"
    try:
        stdscr.addstr(height - 1, 0, status[:width].ljust(width), colors["default"])
    except curses.error:
        pass
    scr_y = cursor_y - offset_y
    scr_x = cursor_x - offset_x
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
    # Initialize curses
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(1)
    curses.start_color()
    curses.use_default_colors()  # Use terminal's default colors
    stdscr.bkgd(' ', curses.A_NORMAL)

    # Initialize color pairs (using -1 for background to be transparent)
    curses.init_pair(1, curses.COLOR_WHITE, -1)    # default
    curses.init_pair(2, curses.COLOR_CYAN, -1)       # keyword (bold)
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

    # Load file if provided as an argument; otherwise show the welcome screen.
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

    while True:
        height, width = stdscr.getmaxyx()
        draw_editor(stdscr, lines, cursor_y, cursor_x, offset_y, offset_x, filename, colors)
        key = stdscr.getch()

        # Handle window resize
        if key == curses.KEY_RESIZE:
            stdscr.clear()
            offset_y = 0
            offset_x = 0
            continue

        # Quit: Ctrl+Q (ASCII code 17)
        if key == 17:
            break
        # Save: Ctrl+S (ASCII code 19)
        elif key == 19:
            if not filename:
                name = prompt_user(stdscr, "Save as: ")
                if name:
                    filename = name
                else:
                    continue  # Cancel save if no input
            try:
                save_file(filename, lines)
                msg = f"Saved: {filename}"
                try:
                    stdscr.addstr(height - 1, 0, msg[:width].ljust(width), colors["default"])
                except curses.error:
                    pass
                stdscr.refresh()
                curses.napms(800)
            except Exception:
                pass
        # Cursor navigation
        elif key == curses.KEY_UP:
            if cursor_y > 0:
                cursor_y -= 1
                if cursor_y < offset_y:
                    offset_y = cursor_y
                cursor_x = min(cursor_x, len(lines[cursor_y]))
        elif key == curses.KEY_DOWN:
            if cursor_y < len(lines) - 1:
                cursor_y += 1
                if cursor_y >= offset_y + height - 1:
                    offset_y += 1
                cursor_x = min(cursor_x, len(lines[cursor_y]))
        elif key == curses.KEY_LEFT:
            if cursor_x > 0:
                cursor_x -= 1
                if cursor_x < offset_x:
                    offset_x = cursor_x
            elif cursor_y > 0:
                cursor_y -= 1
                cursor_x = len(lines[cursor_y])
                if cursor_y < offset_y:
                    offset_y = cursor_y
        elif key == curses.KEY_RIGHT:
            if cursor_x < len(lines[cursor_y]):
                cursor_x += 1
                if cursor_x >= offset_x + width:
                    offset_x += 1
            elif cursor_y < len(lines) - 1:
                cursor_y += 1
                cursor_x = 0
                if cursor_y >= offset_y + height - 1:
                    offset_y += 1
        # Backspace
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if cursor_x > 0:
                line = lines[cursor_y]
                lines[cursor_y] = line[:cursor_x - 1] + line[cursor_x:]
                cursor_x -= 1
            elif cursor_y > 0:
                prev_line = lines[cursor_y - 1]
                curr_line = lines[cursor_y]
                cursor_x = len(prev_line)
                lines[cursor_y - 1] = prev_line + curr_line
                del lines[cursor_y]
                cursor_y -= 1
        # Enter – new line
        elif key in (curses.KEY_ENTER, 10, 13):
            line = lines[cursor_y]
            new_line = line[cursor_x:]
            lines[cursor_y] = line[:cursor_x]
            lines.insert(cursor_y + 1, new_line)
            cursor_y += 1
            cursor_x = 0
            if cursor_y >= offset_y + height - 1:
                offset_y += 1
        # Tab – insert 4 spaces
        elif key == 9:
            line = lines[cursor_y]
            lines[cursor_y] = line[:cursor_x] + TAB_SPACES + line[cursor_x:]
            cursor_x += len(TAB_SPACES)
        # Insert printable characters
        else:
            try:
                ch = chr(key)
            except ValueError:
                continue
            if ch.isprintable():
                line = lines[cursor_y]
                lines[cursor_y] = line[:cursor_x] + ch + line[cursor_x:]
                cursor_x += 1
                if cursor_x >= offset_x + width:
                    offset_x += 1

    # Before exit, clear the screen so no status remains
    stdscr.clear()
    stdscr.refresh()

if __name__ == '__main__':
    curses.wrapper(main)
