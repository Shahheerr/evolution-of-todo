"""
Todo App UI - Beautiful terminal interface using Rich library.
"""

import os
from datetime import datetime
from typing import Optional, List

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich import box
from rich.align import Align

from .models import Todo
from .manager import TodoManager


# ═══════════════════════════════════════════════════════════════
# THEME CONFIGURATION
# ═══════════════════════════════════════════════════════════════

COLORS = {
    "primary": "#7C3AED",       # Purple
    "secondary": "#06B6D4",     # Cyan
    "success": "#10B981",       # Green
    "warning": "#F59E0B",       # Amber
    "danger": "#EF4444",        # Red
    "info": "#3B82F6",          # Blue
    "muted": "#6B7280",         # Gray
    "accent": "#EC4899",        # Pink
    "text": "#E5E7EB",          # Light gray
    "dim": "#9CA3AF",           # Dimmed
}

ICONS = {
    "complete": "✓",
    "incomplete": "○",
    "sparkle": "✨",
    "check_mark": "✅",
    "cross": "❌",
    "clock": "⏰",
    "pencil": "✏️",
    "trash": "🗑️",
    "plus": "➕",
    "list": "📋",
    "target": "🎯",
    "rocket": "🚀",
    "wave": "👋",
    "arrow": "→",
}


class TodoUI:
    """Beautiful terminal UI for the Todo application."""

    def __init__(self, manager: Optional[TodoManager] = None):
        self.console = Console()
        self.manager = manager or TodoManager()

    def clear_screen(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self) -> None:
        """Display ASCII logo and stats."""
        logo = """
╔══════════════════════════════════════════════════════════════════════╗
║     ████████╗ ██████╗ ██████╗  ██████╗      █████╗ ██████╗ ██████╗   ║
║     ╚══██╔══╝██╔═══██╗██╔══██╗██╔═══██╗    ██╔══██╗██╔══██╗██╔══██╗  ║
║        ██║   ██║   ██║██║  ██║██║   ██║    ███████║██████╔╝██████╔╝  ║
║        ██║   ██║   ██║██║  ██║██║   ██║    ██╔══██║██╔═══╝ ██╔═══╝   ║
║        ██║   ╚██████╔╝██████╔╝╚██████╔╝    ██║  ██║██║     ██║       ║
║        ╚═╝    ╚═════╝ ╚═════╝  ╚═════╝     ╚═╝  ╚═╝╚═╝     ╚═╝       ║
╚══════════════════════════════════════════════════════════════════════╝"""

        self.console.print(Text(logo, style=f"bold {COLORS['primary']}"), justify="center")

        # Stats bar
        total, completed, pending = self.manager.get_task_count()
        stats = Text()
        stats.append(f"  {ICONS['target']} Total: ", style=f"bold {COLORS['text']}")
        stats.append(f"{total}", style=f"bold {COLORS['info']}")
        stats.append(f"  │  {ICONS['check_mark']} Done: ", style=f"bold {COLORS['text']}")
        stats.append(f"{completed}", style=f"bold {COLORS['success']}")
        stats.append(f"  │  {ICONS['clock']} Pending: ", style=f"bold {COLORS['text']}")
        stats.append(f"{pending}", style=f"bold {COLORS['warning']}")

        self.console.print(Panel(Align.center(stats), border_style=COLORS['secondary'],
                                  box=box.DOUBLE_EDGE))
        self.console.print()

    def display_menu(self) -> None:
        """Display main menu options."""
        menu = Table.grid(padding=(0, 4))
        menu.add_column(justify="center")
        menu.add_column(justify="center")
        menu.add_column(justify="center")

        menu.add_row(
            Text(f"[1] {ICONS['plus']} Add", style=f"bold {COLORS['success']}"),
            Text(f"[2] {ICONS['list']} View All", style=f"bold {COLORS['info']}"),
            Text(f"[3] {ICONS['pencil']} Update", style=f"bold {COLORS['warning']}"),
        )
        menu.add_row(
            Text(f"[4] {ICONS['trash']} Delete", style=f"bold {COLORS['danger']}"),
            Text(f"[5] {ICONS['check_mark']} Toggle", style=f"bold {COLORS['accent']}"),
            Text(f"[6] {ICONS['sparkle']} Pending", style=f"bold {COLORS['secondary']}"),
        )
        menu.add_row(
            Text(f"[7] ⭐ Completed", style=f"bold {COLORS['muted']}"),
            Text(f"[8] 🔥 Clear Done", style=f"bold {COLORS['muted']}"),
            Text(f"[0] {ICONS['wave']} Exit", style=f"bold {COLORS['danger']}"),
        )

        self.console.print(Panel(Align.center(menu), title=f"[bold {COLORS['primary']}]✨ MENU ✨[/]",
                                  border_style=COLORS['primary'], box=box.ROUNDED))
        self.console.print()

    def display_tasks_table(self, todos: List[Todo], title: str = "Your Tasks") -> None:
        """Display tasks in a beautiful table."""
        if not todos:
            self.console.print(Panel(
                Align.center(Text(f"\n📁 No tasks found!\n", style=f"italic {COLORS['muted']}")),
                title=f"[bold {COLORS['info']}]{title}[/]",
                border_style=COLORS['muted'], box=box.ROUNDED
            ))
            return

        table = Table(
            title=f"[bold {COLORS['primary']}]{ICONS['list']} {title}[/]",
            box=box.ROUNDED,
            border_style=COLORS['secondary'],
            header_style=f"bold {COLORS['primary']}",
            expand=True,
        )

        table.add_column("Status", justify="center", width=8)
        table.add_column("ID", style=f"bold {COLORS['info']}", justify="center", width=10)
        table.add_column("Title", style=f"bold {COLORS['text']}", min_width=20)
        table.add_column("Description", style=COLORS['dim'], min_width=25)
        table.add_column("Created", style=COLORS['muted'], justify="center", width=12)

        for todo in todos:
            if todo.completed:
                status = f"[bold {COLORS['success']}]{ICONS['complete']}[/]"
                title_style = f"strike {COLORS['muted']}"
            else:
                status = f"[bold {COLORS['warning']}]{ICONS['incomplete']}[/]"
                title_style = f"bold {COLORS['text']}"

            desc = todo.description if todo.description else "—"
            if len(desc) > 40:
                desc = desc[:37] + "..."

            table.add_row(
                status,
                f"[bold cyan]{todo.id}[/]",
                f"[{title_style}]{todo.title}[/]",
                desc,
                todo.created_at.strftime("%b %d, %H:%M"),
            )

        self.console.print(table)
        self.console.print()

    def display_success(self, message: str) -> None:
        self.console.print(Panel(
            Align.center(Text(message, style=f"bold {COLORS['success']}")),
            border_style=COLORS['success'], box=box.ROUNDED
        ))

    def display_error(self, message: str) -> None:
        self.console.print(Panel(
            Align.center(Text(f"{ICONS['cross']} {message}", style=f"bold {COLORS['danger']}")),
            border_style=COLORS['danger'], box=box.ROUNDED
        ))

    def display_info(self, message: str) -> None:
        self.console.print(Panel(
            Align.center(Text(message, style=f"bold {COLORS['info']}")),
            border_style=COLORS['info'], box=box.ROUNDED
        ))

    def get_menu_choice(self) -> str:
        return Prompt.ask(
            f"[bold {COLORS['secondary']}]{ICONS['arrow']} Enter choice[/]",
            choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            default="2"
        )

    def get_task_input(self) -> tuple[str, str]:
        self.console.print(Panel(
            f"[bold {COLORS['info']}]{ICONS['plus']} Create New Task[/]",
            border_style=COLORS['info'], box=box.ROUNDED
        ))
        title = Prompt.ask(f"[bold {COLORS['primary']}]Task title[/]")
        description = Prompt.ask(f"[{COLORS['dim']}]Description (optional)[/]", default="")
        return title, description

    def get_task_id(self, action: str = "select") -> str:
        return Prompt.ask(f"[bold {COLORS['secondary']}]Enter task ID to {action}[/]")

    def confirm_action(self, message: str) -> bool:
        return Confirm.ask(f"[bold {COLORS['warning']}]{message}[/]", default=False)

    def wait_for_key(self) -> None:
        self.console.print()
        Prompt.ask(f"[{COLORS['dim']}]Press Enter to continue...[/]", default="")

    def action_add_task(self) -> None:
        title, description = self.get_task_input()
        if not title.strip():
            self.display_error("Title cannot be empty!")
            return
        todo = self.manager.add_task(title.strip(), description.strip())
        self.display_success(f"{ICONS['sparkle']} Task '{todo.title}' added!")

    def action_view_all_tasks(self) -> None:
        self.display_tasks_table(self.manager.get_all_tasks(), "All Tasks")

    def action_view_pending(self) -> None:
        self.display_tasks_table(self.manager.get_pending_tasks(), "Pending Tasks")

    def action_view_completed(self) -> None:
        self.display_tasks_table(self.manager.get_completed_tasks(), "Completed Tasks")

    def action_update_task(self) -> None:
        self.action_view_all_tasks()
        if not self.manager.get_all_tasks():
            return
        task_id = self.get_task_id("update")
        todo = self.manager.get_task_by_id(task_id)
        if not todo:
            self.display_error(f"Task '{task_id}' not found!")
            return
        new_title = Prompt.ask("New title", default=todo.title)
        new_desc = Prompt.ask("New description", default=todo.description)
        success, msg = self.manager.update_task(task_id, new_title, new_desc)
        self.display_success(msg) if success else self.display_error(msg)

    def action_delete_task(self) -> None:
        self.action_view_all_tasks()
        if not self.manager.get_all_tasks():
            return
        task_id = self.get_task_id("delete")
        todo = self.manager.get_task_by_id(task_id)
        if not todo:
            self.display_error(f"Task '{task_id}' not found!")
            return
        if self.confirm_action(f"Delete '{todo.title}'?"):
            success, msg = self.manager.delete_task(task_id)
            self.display_success(msg) if success else self.display_error(msg)
        else:
            self.display_info("Cancelled.")

    def action_toggle_complete(self) -> None:
        self.action_view_all_tasks()
        if not self.manager.get_all_tasks():
            return
        task_id = self.get_task_id("toggle")
        success, msg = self.manager.toggle_task(task_id)
        self.display_success(msg) if success else self.display_error(msg)

    def action_clear_completed(self) -> None:
        completed = self.manager.get_completed_tasks()
        if not completed:
            self.display_info("No completed tasks to clear!")
            return
        if self.confirm_action(f"Clear {len(completed)} completed task(s)?"):
            success, msg = self.manager.clear_completed_tasks()
            self.display_success(msg) if success else self.display_error(msg)

    def display_goodbye(self) -> None:
        """Display exit message."""
        msg = f"""
{ICONS['wave']} Thank you for using Todo App!
{ICONS['sparkle']} Stay productive! {ICONS['rocket']}
        """
        self.console.print(Panel(
            Align.center(Text(msg, style=f"bold {COLORS['primary']}")),
            border_style=COLORS['accent'], box=box.DOUBLE_EDGE
        ))

    def run(self) -> None:
        """Main application loop."""
        while True:
            try:
                self.clear_screen()
                self.display_header()
                self.display_menu()

                choice = self.get_menu_choice()
                self.console.print()

                if choice == "0":
                    self.display_goodbye()
                    break
                elif choice == "1":
                    self.action_add_task()
                elif choice == "2":
                    self.action_view_all_tasks()
                elif choice == "3":
                    self.action_update_task()
                elif choice == "4":
                    self.action_delete_task()
                elif choice == "5":
                    self.action_toggle_complete()
                elif choice == "6":
                    self.action_view_pending()
                elif choice == "7":
                    self.action_view_completed()
                elif choice == "8":
                    self.action_clear_completed()

                self.wait_for_key()

            except KeyboardInterrupt:
                self.console.print()
                self.display_goodbye()
                break
            except Exception as e:
                self.display_error(f"Error: {str(e)}")
                self.wait_for_key()


def main():
    """Entry point."""
    ui = TodoUI()
    ui.run()


if __name__ == "__main__":
    main()