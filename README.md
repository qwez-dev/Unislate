<div align="center">
  <img src="https://github.com/Qwez-source/Unislate/blob/main/demo.gif?raw=true">
  
  <h1>Unislate</h1>
  
  [![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)
  [![Version](https://img.shields.io/badge/version-0.1.3-blue.svg)](#)
  [![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](#)
</div>

---

## About the project

**Unislate** is a minimalist console editor with advanced syntax highlighting and a set of convenient functions for editing text and source code directly in the terminal.

---

## Features

- **Syntax Highlighting:**  
  Support for multiple languages, including:
  - **Python**
  - **JavaScript, TypeScript, JSX, TSX**
  - **C/C++**
  - **Java**
  - **Markdown**  
  As well as basic highlighting for other text formats (HTML, CSS, JSON, XML, etc.).

- **Convenient Editing:**  
  - Input characters, delete (Backspace), create a new line (Enter) while preserving indentation.
  - Insert tab (4 spaces) using the Tab key.

- **Text Selection:**  
  Use **Shift + arrow keys** to select text fragments.

- **Clipboard:**  
  - **Copy:** `Ctrl+C` – copies the selected text (or the current line if nothing is selected).
  - **Cut:** `Ctrl+X` – cuts the selected text (or the line if nothing is selected).
  - **Paste:** `Ctrl+V` – pastes the clipboard content.  

- **Undo and Redo:**  
  - **Undo:** `Ctrl+Z` – step back.
  - **Redo:** `Ctrl+Y` – restores the undone action.

- **Welcome Screen:**  
  When launched without specifying a file, a screen with ASCII art and a prompt to start working is displayed.

- **Status Bar:**  
  The bottom of the screen displays file information (name, "new" status if the file has not yet been saved), current line, and cursor position.

---

## Installation

### Requirements

- Python 3.6+
- Terminal that supports ANSI colors and Unicode characters

### Installation from source

1. **Install package:**

   ```bash
   pip install unislate
   ```

2. **Run editor:**

   ```bash
   unislate [filename]
   ```

   If the filename is not specified, the welcome screen will be shown first, after which a new file will be created.

---

## Usage

- **Text Navigation:**  
  Use arrow keys to move the cursor through the file.

- **Editing:**  
  Simply type characters to change the line. Use Backspace to delete characters.

- **New Line:**  
  Press Enter to move to a new line. The indentation of the previous line is automatically preserved.

- **Insert Tab:**  
  Press Tab to add an indent (4 spaces).

- **Text Selection:**  
  To select text, hold Shift and use the arrow keys.

- **Copying and Cutting:**  
  - `Ctrl+C` – copies the selected text or the current line.
  - `Ctrl+X` – cuts the selected text or the current line.

- **Pasting:**  
  `Ctrl+V` – pastes the clipboard content.

- **Undo/Redo:**  
  - `Ctrl+Z` – undoes the last change.
  - `Ctrl+Y` – redoes the undone action.

- **Saving File:**  
  `Ctrl+S` – saves changes. If the file is new, the editor will prompt for a name.

- **Exiting Editor:**  
  `Ctrl+Q` – exits the program. If there are unsaved changes, a confirmation prompt to exit without saving will appear.

---

## Contribution

We welcome any ideas and improvements!

1. **Fork** the repository.
2. Create a new **branch** (e.g., `git checkout -b feature/YourFeature`).
3. **Commit** your changes (e.g., `git commit -m 'Add a new feature'`).
4. **Push** the branch (`git push origin feature/YourFeature`).
5. Open a **Pull Request** for discussion and merging of changes.

---

## License

This project is distributed under the [MIT License](LICENSE).

---

<div align="center">
  <sub>Made with ♥️ by <a href="https://github.com/qwez-dev">Qwez</a></sub>
</div>
