import os
import time
import requests
from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich import box
from rich.progress import Progress

# URL untuk mengambil logo
LOGO_URL = "https://raw.githubusercontent.com/choir94/Airdropguide/refs/heads/main/logo.sh"

def fetch_logo():
    """Mengambil logo dari URL"""
    try:
        response = requests.get(LOGO_URL)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return "Gagal mengambil logo: " + str(e)

def show_logo():
    """Menampilkan logo dengan efek loading"""
    os.system("cls" if os.name == "nt" else "clear")
    console = Console()

    with Progress() as progress:
        task = progress.add_task("[cyan]Mengambil logo...", total=100)
        for _ in range(10):
            time.sleep(0.1)
            progress.update(task, advance=10)

    logo_text = fetch_logo()
    gradient_logo = Text(logo_text)
    gradient_logo.stylize("bold bright_green")

    console.print(gradient_logo)
    print()

def show_dev_info():
    """Menampilkan informasi bot dengan tampilan unik"""
    console = Console()

    table = Table(
        show_header=False,
        box=box.ROUNDED,
        border_style="bright_magenta",
        pad_edge=True,
        width=60,
        highlight=True,
    )

    table.add_column("Content", style="bold bright_blue", justify="center")

    # Menambahkan teks dengan efek warna yang berbeda
    table.add_row("[bold gradient]✨ Bot Monad Testnet ✨[/bold gradient]")
    table.add_row("─" * 55)
    table.add_row("[bright_yellow]⚡ GitHub: [link]https://github.com/choir94/[/link][/bright_yellow]")
    table.add_row("[bright_red]?? Chat: [link]https://t.me/airdrop_node[/link][/bright_red]")

    console.print("\n")
    console.print(table, justify="center")
    console.print("\n")

if __name__ == "__main__":
    show_logo()
    show_dev_info()

