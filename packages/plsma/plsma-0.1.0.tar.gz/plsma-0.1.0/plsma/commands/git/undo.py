"""
Git undo command implementation
"""

from rich.console import Console

from ..base import BaseCommand
from ..registry import registry

console = Console()


class UndoCommand(BaseCommand):
    """Git undo utilities"""

    def execute(self, _):
        """Undo the last commit but keep changes"""
        self.info("Undoing last commit (keeping changes)...")

        # Show last commit
        result = self._run_command("git log --oneline -1")
        if result.returncode == 0:
            console.print(f"Last commit: [cyan]{result.stdout.strip()}[/cyan]")

        if self.ask_confirmation("Undo this commit?"):
            result = self._run_command("git reset --soft HEAD~1")
            if result.returncode == 0:
                self.success("Last commit undone (changes preserved)")
            else:
                self.error("Undoing commit")
                return False

        return True


def register_undo_command():
    """Register the undo command"""
    cmd = UndoCommand()
    registry.register(
        name="undo",
        description="Undo the last commit (keep changes)",
        category="git",
        func=cmd.execute,
        usage="git:undo",
    )
