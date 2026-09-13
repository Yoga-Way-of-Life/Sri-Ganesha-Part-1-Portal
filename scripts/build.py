#!/usr/bin/env python3
"""
Sri Gaṇeśa — Part 1 Portal
Static-site build engine.

Architecture:
    Markdown → Python build engine → Jinja2 templates → Static HTML

The build engine is intentionally lightweight and transparent.
"""

from __future__ import annotations

import re
import shutil
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader, StrictUndefined


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = PROJECT_ROOT
TEMPLATE_DIR = PROJECT_ROOT / "templates"
BUILD_DIR = PROJECT_ROOT / "_build"

EXCLUDED_DIRECTORIES = {
    ".git",
    "ARCHIVED",
    "_build",
    "build",
    "dist",
    "venv",
    "__pycache__",
}

MARKDOWN_PATTERN = "*.md"
PAGE_TEMPLATE = "page.html"


class HeadingParser(HTMLParser):
    """Extract H2 headings and their generated HTML IDs."""

    def __init__(self) -> None:
        super().__init__()
        self.headings: list[dict[str, str]] = []
        self._current_heading: dict[str, str] | None = None
        self._current_text: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        """Capture the start of an H2 element."""
        if tag != "h2":
            return

        attributes = dict(attrs)
        heading_id = attributes.get("id")

        if heading_id:
            self._current_heading = {"id": heading_id}
            self._current_text = []

    def handle_data(self, data: str) -> None:
        """Capture text contained inside the current H2."""
        if self._current_heading is not None:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        """Complete the current H2 heading."""
        if tag != "h2" or self._current_heading is None:
            return

        title = "".join(self._current_text).strip()

        if title:
            self._current_heading["title"] = title
            self.headings.append(self._current_heading)

        self._current_heading = None
        self._current_text = []


def build_page_toc(content_html: str) -> str:
    """Build an in-page navigation component from H2 headings."""
    parser = HeadingParser()
    parser.feed(content_html)

    if not parser.headings:
        return ""

    items = []

    for heading in parser.headings:
        items.append(
            f'<li><a href="#{heading["id"]}">{heading["title"]}</a></li>'
        )

    return (
        '<nav class="page-toc" aria-label="On this page">'
        '<p class="page-toc__label">On this page</p>'
        '<ul class="page-toc__list">'
        + "".join(items)
        + "</ul>"
        "</nav>"
    )


@dataclass(frozen=True)
class Page:
    """
    Represents one Markdown source page prepared for rendering.

    Navigation relationships are connected after all pages have been
    discovered and prepared.
    """

    source_path: Path
    relative_path: Path
    output_path: Path
    title: str
    slug: str
    url: str
    content_html: str
    page_toc: str
    previous_page: "Page | None" = None
    next_page: "Page | None" = None


def is_excluded(path: Path) -> bool:
    """Return True when a path contains an excluded directory."""
    return any(part in EXCLUDED_DIRECTORIES for part in path.parts)


def discover_markdown_sources() -> list[Path]:
    """Discover canonical Markdown source pages in reading order."""
    sources: list[Path] = []

    for path in SOURCE_ROOT.rglob(MARKDOWN_PATTERN):
        relative_path = path.relative_to(SOURCE_ROOT)

        if is_excluded(relative_path):
            continue

        sources.append(path)

    sources.sort()

    print_info(f"Discovered {len(sources)} Markdown source file(s).")

    for source in sources:
        print_info(f"  - {source.relative_to(PROJECT_ROOT)}")

    return sources


def extract_title(markdown_source: str, source_path: Path) -> str:
    """Extract the first H1 heading from a Markdown source."""
    for line in markdown_source.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)

        if match:
            return match.group(1).strip()

    raise ValueError(
        f"No H1 title found in Markdown source: {source_path}"
    )


def create_slug(source_path: Path) -> str:
    """Create a URL-friendly slug from the source filename."""
    stem = source_path.stem.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", stem)
    return slug.strip("-")


def render_markdown(markdown_source: str) -> str:
    """Convert Markdown source into HTML."""
    return markdown.markdown(
        markdown_source,
        extensions=[
            "extra",
            "toc",
            "sane_lists",
            "tables",
            "fenced_code",
            "attr_list",
        ],
        output_format="html5",
    )


def prepare_page(source_path: Path) -> Page:
    """Prepare one Markdown source page for rendering."""
    markdown_source = source_path.read_text(
        encoding="utf-8-sig"
    )

    title = extract_title(markdown_source, source_path)
    slug = create_slug(source_path)
    content_html = render_markdown(markdown_source)
    page_toc = build_page_toc(content_html)

    relative_path = source_path.relative_to(PROJECT_ROOT)
    output_path = BUILD_DIR / relative_path.with_suffix(".html")
    url = relative_path.with_suffix(".html").as_posix()

    return Page(
        source_path=source_path,
        relative_path=relative_path,
        output_path=output_path,
        title=title,
        slug=slug,
        url=url,
        content_html=content_html,
        page_toc=page_toc,
    )


def connect_page_navigation(pages: list[Page]) -> None:
    """
    Connect pages in canonical reading order.

    The first page has no previous page.
    The last page has no next page.
    """

    for index, page in enumerate(pages):
        previous_page = pages[index - 1] if index > 0 else None
        next_page = pages[index + 1] if index < len(pages) - 1 else None

        object.__setattr__(
            page,
            "previous_page",
            previous_page,
        )
        object.__setattr__(
            page,
            "next_page",
            next_page,
        )


def create_template_environment() -> Environment:
    """Create the Jinja2 template environment."""
    return Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        undefined=StrictUndefined,
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_page(page: Page, environment: Environment) -> str:
    """Render one prepared page through the global page template."""
    template = environment.get_template(PAGE_TEMPLATE)

    return template.render(
        page=page,
        site_title="Śrī Gaṇeśa's Wisdom",
        site_description=(
            "A digital companion to Sri Gaṇeśa's Wisdom — "
            "A Handbook of Symbolism and Daily Practice."
        ),
    )


def prepare_build_directory() -> None:
    """Remove and recreate the static build directory."""
    if BUILD_DIR.exists():
        print_info(f"Removing previous build directory: {BUILD_DIR}")
        shutil.rmtree(BUILD_DIR)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    print_success(f"Build directory prepared: {BUILD_DIR}")


def write_page(page: Page, html: str) -> None:
    """Write rendered HTML to the page's build path."""
    page.output_path.parent.mkdir(parents=True, exist_ok=True)

    page.output_path.write_text(
        html,
        encoding="utf-8",
        newline="\n",
    )

    print_success(
        "Generated: "
        f"{page.output_path.relative_to(PROJECT_ROOT)}"
    )


def copy_static_assets() -> None:
    """Copy the project's static assets into the build directory."""
    source_assets = PROJECT_ROOT / "assets"
    target_assets = BUILD_DIR / "assets"

    if not source_assets.exists():
        print_warning("No assets directory found. Skipping asset copy.")
        return

    shutil.copytree(source_assets, target_assets)
    print_success(
        f"Copied static assets to: {target_assets.relative_to(PROJECT_ROOT)}"
    )


def validate_project_structure() -> None:
    """Validate the minimum project structure required for a build."""
    required_paths = {
        "templates": TEMPLATE_DIR,
        "page template": TEMPLATE_DIR / PAGE_TEMPLATE,
        "assets": PROJECT_ROOT / "assets",
    }

    missing = [
        name
        for name, path in required_paths.items()
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Missing required project structure: "
            + ", ".join(missing)
        )


def print_header(message: str) -> None:
    """Print a build-section heading."""
    print()
    print("=" * 72)
    print(message)
    print("=" * 72)


def print_info(message: str) -> None:
    """Print an informational build message."""
    print(f"[INFO] {message}")


def print_success(message: str) -> None:
    """Print a successful build message."""
    print(f"[OK]   {message}")


def print_warning(message: str) -> None:
    """Print a warning build message."""
    print(f"[WARN] {message}")


def print_error(message: str) -> None:
    """Print an error build message."""
    print(f"[ERROR] {message}", file=sys.stderr)


def build() -> int:
    """Execute the complete static-site build."""
    print_header("Sri Gaṇeśa — Part 1 Portal")

    try:
        validate_project_structure()
        sources = discover_markdown_sources()

        if not sources:
            print_warning(
                "Nothing to build yet. "
                "Create the first canonical Markdown page."
            )
            return 0

        prepare_build_directory()
        environment = create_template_environment()

        print_header("Preparing pages")

        pages: list[Page] = []

        for source_path in sources:
            page = prepare_page(source_path)
            pages.append(page)

        connect_page_navigation(pages)

        print_header("Rendering pages")

        for page in pages:
            html = render_page(page, environment)
            write_page(page, html)

        print_header("Copying static assets")
        copy_static_assets()

        print_header("Build complete")
        print_success(
            f"Generated {len(pages)} page(s) in {BUILD_DIR}"
        )

        return 0

    except Exception as exc:
        print_error(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(build())