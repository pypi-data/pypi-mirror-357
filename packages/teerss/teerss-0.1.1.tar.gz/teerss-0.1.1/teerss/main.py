import os
import feedparser
import requests
from readability import Document
from bs4 import BeautifulSoup
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
import textwrap

console = Console()


def get_feed_file_path():
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    config_dir = os.path.join(xdg_config_home, "teerss")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "feeds.txt")


def load_feeds():
    feed_file = get_feed_file_path()
    if not os.path.exists(feed_file):
        return []
    with open(feed_file, "r") as f:
        return [line.strip() for line in f if line.strip()]


def save_feeds(feeds):
    feed_file = get_feed_file_path()
    with open(feed_file, "w") as f:
        for feed in feeds:
            f.write(feed + "\n")


def add_feeds():
    urls = Prompt.ask("[cyan]Enter RSS feed URLs (comma-separated)[/cyan]")
    new_list = [url.strip() for url in urls.split(",") if url.strip()]
    feeds = load_feeds()
    feeds.extend(url for url in new_list if url not in feeds)
    save_feeds(feeds)
    console.print("[green]✅ Feeds added.[/green]\n")


def delete_feed():
    feeds = load_feeds()
    if not feeds:
        console.print("[yellow]No feeds to delete.[/yellow]\n")
        return

    table = Table(title="Saved Feeds", header_style="bold magenta")
    table.add_column("No.")
    table.add_column("URL")
    for i, url in enumerate(feeds):
        table.add_row(str(i + 1), url)
    console.print(table)

    try:
        index = int(Prompt.ask("Enter the number of the feed to delete")) - 1
        if 0 <= index < len(feeds):
            removed = feeds.pop(index)
            save_feeds(feeds)
            console.print(f"[red]❌ Removed:[/red] {removed}\n")
        else:
            console.print("[red]Invalid number.[/red]\n")
    except ValueError:
        console.print("[red]Please enter a valid number.[/red]\n")


def fetch_rss(url):
    feed = feedparser.parse(url)
    if feed.bozo:
        console.print("[red]❌ Failed to parse RSS feed.[/red]")
        return None
    return feed


def print_centered_block(lines):
    term_width = console.size.width
    term_height = console.size.height

    pad_top = max((term_height - len(lines)) // 2, 0)
    max_len = max(len(line) for line in lines)
    pad_left = max((term_width - max_len) // 2, 0)

    console.clear()
    console.print("\n" * pad_top, end="")

    for line in lines:
        console.print(" " * pad_left + line)


def fetch_full_article(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        doc = Document(response.text)
        summary_html = doc.summary()
        text = BeautifulSoup(summary_html, "html.parser").get_text(separator="\n")
        return text.strip()
    except Exception as e:
        return f"[⚠️ Error fetching article: {e}]"


def display_article(entry, entries, feed_url):
    full_text = fetch_full_article(entry.link)
    paragraphs = [p.strip() for p in full_text.split("\n") if p.strip()]
    if not paragraphs:
        summary = getattr(entry, "summary", "[No summary available]")
        paragraphs = [summary]

    wrapped_lines = []
    line_width = 80
    for para in paragraphs:
        wrapped = textwrap.wrap(para, width=line_width)
        wrapped_lines.extend(wrapped + [""])

    page_size = console.size.height - 7
    total_lines = len(wrapped_lines)
    total_pages = (total_lines + page_size - 1) // page_size
    page = 0

    term_width = console.size.width
    while page * page_size < total_lines:
        start = page * page_size
        end = start + page_size

        content_lines = []
        content_lines.append(f"📰 {entry.title}")
        content_lines.append(f"--- Page {page + 1}/{total_pages} ---\n")
        content_lines.extend(wrapped_lines[start:end])

        content_height = len(content_lines)
        pad_top = max((console.size.height - content_height) // 2, 0)
        max_line_length = max(len(line) for line in content_lines)
        pad_left = max((term_width - max_line_length) // 2, 0)

        console.clear()
        console.print("\n" * pad_top, end="")

        for line in content_lines:
            console.print(" " * pad_left + line)

        page += 1
        if end < total_lines:
            resp = Prompt.ask(
                "[dim]Press [Enter] to continue, 'b' to go back, 'm' for main menu or 'q' to quit[/dim]",
                default="",
            )
            if resp.lower() == "q":
                exit(0)
            elif resp.lower() == "m":
                return "main_menu"
            elif resp.lower() == "b":
                return "back_to_articles"

    while True:
        resp = Prompt.ask(
            "[dim]End of article. Press 'b' to go back, 'm' for main menu or 'q' to quit[/dim]"
        )
        if resp.lower() == "q":
            exit(0)
        elif resp.lower() == "m":
            return "main_menu"
        elif resp.lower() == "b":
            return "back_to_articles"


def select_feed_and_read():
    feeds = load_feeds()
    if not feeds:
        console.print("[yellow]No feeds saved yet. Please add some first.[/yellow]\n")
        return

    while True:
        lines = ["Saved Feeds", ""]
        for i, url in enumerate(feeds):
            lines.append(f"{i + 1}. {url}")
        lines.append("")
        lines.append("Select feed number to read")

        print_centered_block(lines)

        try:
            index = int(Prompt.ask("")) - 1
            if 0 <= index < len(feeds):
                feed_url = feeds[index]
                feed = fetch_rss(feed_url)
                if feed:
                    while True:
                        article_lines = [
                            f"📡 Feed: {feed.feed.get('title', 'No title')}",
                            "",
                        ]
                        for i, entry in enumerate(feed.entries[:10]):
                            article_lines.append(f"{i + 1}. {entry.title}")
                        article_lines.append("")
                        article_lines.append(
                            "Enter article number to read (or 'b' to go back, 'm' for main menu, 'q' to quit)"
                        )

                        print_centered_block(article_lines)

                        choice = Prompt.ask("")
                        if choice.lower() == "b":
                            break
                        if choice.lower() == "m":
                            return
                        if choice.lower() == "q":
                            exit(0)
                        if choice.isdigit():
                            idx = int(choice) - 1
                            if 0 <= idx < len(feed.entries[:10]):
                                action = display_article(
                                    feed.entries[idx], feed.entries, feed_url
                                )
                                if action == "back_to_articles":
                                    continue
                                elif action == "main_menu":
                                    return
                            else:
                                console.print("[red]Invalid article number.[/red]")
                        else:
                            console.print(
                                "[red]Please enter a valid number, 'b', 'm', or 'q'.[/red]"
                            )
            else:
                console.print("[red]Invalid selection.[/red]\n")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]\n")


def main_menu():
    while True:
        menu_lines = [
            "📘 TeeRSS Menu",
            "",
            "1. 📂 Explore RSS Feeds",
            "2. ➕ Add RSS Feed URL(s)",
            "3. ❌ Delete RSS Saved Feed",
            "4. 🚪 Quit",
            "",
            "Choose an option",
        ]

        print_centered_block(menu_lines)

        choice = Prompt.ask("")

        if choice == "1":
            select_feed_and_read()
        elif choice == "2":
            add_feeds()
        elif choice == "3":
            delete_feed()
        elif choice == "4":
            console.print("\n" + "👋 Goodbye!".center(console.size.width) + "\n")
            break
        else:
            console.print(
                "\n"
                + "[red]Invalid option. Please select 1–4.[/red]".center(
                    console.size.width
                )
                + "\n"
            )


def main():
    main_menu()


if __name__ == "__main__":
    main()
