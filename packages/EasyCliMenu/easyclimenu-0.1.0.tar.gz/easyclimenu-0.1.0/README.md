# cli-menu

Complete interactive CLI menu without external dependencies.

---

## Description

`cli-menu` is a Python library to easily create interactive command-line menus, compatible with Windows, Linux, and macOS, with **no external dependencies**.

Features:  
- Keyboard navigation (arrow keys up/down, left/right for paging)  
- Single or multiple selection mode (space bar to check/uncheck)  
- Quit with `q` or `ESC`  
- Colored display using ANSI codes  
- Customizable titles and descriptions  
- Automatic pagination  
- Callbacks for specific options  
- Windows and Unix compatible (handles console specifics)

---

## Installation

```bash
pip install cli-menu
```
## Basic Usage

```python
from cli_menu import CliMenu

menu = CliMenu(
    options=["Option 1", "Option 2", "Quit"],
    title="=== MAIN MENU ===",
    description="Use arrow keys and Enter to navigate.",
    multiselect=False
)

choice = menu.show()
print(f"You selected: {menu.options[choice]}")
```
## Main Parameters

| Parameter   | Type             | Description                              | Default          |
| ----------- | ---------------- | ---------------------------------------- | ---------------- |
| options     | list\[str]       | List of options displayed in the menu    | *Required*       |
| title       | str              | Title displayed above the menu           | `None`           |
| description | str              | Description displayed below the title    | `None`           |
| multiselect | bool             | Enable multiple selection with space bar | `False`          |
| page\_size  | int              | Max number of options displayed per page | `10`             |
| color       | bool             | Enable ANSI color output                 | `True`           |
| exit\_keys  | list\[str]       | Keys to exit menu (e.g., `q`, `ESC`)     | `['q', '\\x1b']` |
| callbacks   | dict\[int, func] | Functions triggered on option selection  | `{}`             |

## Methods

```python
 show()
```
Displays the menu and handles keyboard interaction.
Returns:

   - Selected index (int) in single-select mode

   - List of selected indices (list[int]) in multi-select mode

   - None if user exits with an exit key

### Author

Gaetan Lerley -- Hostinfire@gmail.com




