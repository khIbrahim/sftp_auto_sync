from rich.console import Console

console = Console()

def info(msg): console.log(f"[cyan][INFO][/cyan] {msg}")
def warn(msg): console.log(f"[yellow][WARN][/yellow] {msg}")
def error(msg): console.log(f"[bold red][ERROR][/bold red] {msg}")
def success(msg): console.log(f"[bold green][SUCCESS][/bold green] {msg}")
def debug(msg): console.log(f"[dim][DEBUG][/dim] {msg}")