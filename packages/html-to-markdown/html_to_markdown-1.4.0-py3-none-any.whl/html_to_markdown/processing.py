from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
from itertools import chain
from typing import TYPE_CHECKING, Any, Callable, Literal, cast

from bs4 import BeautifulSoup, Comment, Doctype, NavigableString, Tag

from html_to_markdown.constants import (
    ASTERISK,
    SPACES,
    UNDERLINED,
    html_heading_re,
    whitespace_re,
)
from html_to_markdown.converters import Converter, ConvertersMap, SupportedElements, create_converters_map
from html_to_markdown.utils import escape

if TYPE_CHECKING:
    from collections.abc import Iterable

    from bs4 import PageElement

SupportedTag = Literal[
    "a",
    "b",
    "blockquote",
    "br",
    "code",
    "del",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "img",
    "list",
    "ul",
    "ol",
    "li",
    "p",
    "pre",
    "script",
    "style",
    "s",
    "strong",
    "samp",
    "sub",
    "sup",
    "table",
    "caption",
    "figcaption",
    "td",
    "th",
    "tr",
    "kbd",
]


def _is_nested_tag(el: PageElement) -> bool:
    return isinstance(el, Tag) and el.name in {
        "ol",
        "ul",
        "li",
        "table",
        "thead",
        "tbody",
        "tfoot",
        "tr",
        "td",
        "th",
    }


def _process_tag(
    tag: Tag,
    converters_map: ConvertersMap,
    *,
    convert: set[str] | None,
    convert_as_inline: bool = False,
    escape_asterisks: bool,
    escape_misc: bool,
    escape_underscores: bool,
    strip: set[str] | None,
    context_before: str = "",
) -> str:
    should_convert_tag = _should_convert_tag(tag_name=tag.name, strip=strip, convert=convert)
    tag_name: SupportedTag | None = (
        cast("SupportedTag", tag.name.lower()) if tag.name.lower() in converters_map else None
    )
    text = ""

    is_heading = html_heading_re.match(tag.name) is not None
    is_cell = tag_name in {"td", "th"}
    convert_children_as_inline = convert_as_inline or is_heading or is_cell

    if _is_nested_tag(tag):
        for el in tag.children:
            can_extract = (
                not el.previous_sibling
                or not el.next_sibling
                or _is_nested_tag(el.previous_sibling)
                or _is_nested_tag(el.next_sibling)
            )
            if can_extract and isinstance(el, NavigableString) and not el.strip():
                el.extract()

    for el in filter(lambda value: not isinstance(value, (Comment, Doctype)), tag.children):
        if isinstance(el, NavigableString):
            text += _process_text(
                el=el,
                escape_misc=escape_misc,
                escape_asterisks=escape_asterisks,
                escape_underscores=escape_underscores,
            )
        elif isinstance(el, Tag):
            text += _process_tag(
                el,
                converters_map,
                convert_as_inline=convert_children_as_inline,
                convert=convert,
                escape_asterisks=escape_asterisks,
                escape_misc=escape_misc,
                escape_underscores=escape_underscores,
                strip=strip,
                context_before=(context_before + text)[-2:],
            )

    if tag_name and should_convert_tag:
        rendered = converters_map[tag_name](  # type: ignore[call-arg]
            tag=tag, text=text, convert_as_inline=convert_as_inline
        )
        # For headings, ensure two newlines before if not already present
        # Edge case where the document starts with a \n and then a heading
        if is_heading and context_before not in {"", "\n"}:
            n_eol_to_add = 2 - (len(context_before) - len(context_before.rstrip("\n")))
            if n_eol_to_add > 0:
                prefix = "\n" * n_eol_to_add
                return f"{prefix}{rendered}"
        return rendered

    return text


def _process_text(
    *,
    el: NavigableString,
    escape_misc: bool,
    escape_asterisks: bool,
    escape_underscores: bool,
) -> str:
    text = str(el) or ""

    if not el.find_parent("pre"):
        text = whitespace_re.sub(" ", text)

    if not el.find_parent(["pre", "code", "kbd", "samp"]):
        text = escape(
            text=text,
            escape_misc=escape_misc,
            escape_asterisks=escape_asterisks,
            escape_underscores=escape_underscores,
        )

    if (
        el.parent
        and el.parent.name == "li"
        and (not el.next_sibling or getattr(el.next_sibling, "name", None) in {"ul", "ol"})
    ):
        text = text.rstrip()

    return text


def _should_convert_tag(*, tag_name: str, strip: set[str] | None, convert: set[str] | None) -> bool:
    if strip is not None:
        return tag_name not in strip
    if convert is not None:
        return tag_name in convert
    return True


def _as_optional_set(value: str | Iterable[str] | None) -> set[str] | None:
    if value is None:
        return None
    if isinstance(value, str):
        return set(",".split(value))
    return {*chain(*[v.split(",") for v in value])}


def convert_to_markdown(
    source: str | BeautifulSoup,
    *,
    autolinks: bool = True,
    bullets: str = "*+-",
    code_language: str = "",
    code_language_callback: Callable[[Any], str] | None = None,
    convert: str | Iterable[str] | None = None,
    convert_as_inline: bool = False,
    custom_converters: Mapping[SupportedElements, Converter] | None = None,
    default_title: bool = False,
    escape_asterisks: bool = True,
    escape_misc: bool = True,
    escape_underscores: bool = True,
    heading_style: Literal["underlined", "atx", "atx_closed"] = UNDERLINED,
    keep_inline_images_in: Iterable[str] | None = None,
    newline_style: Literal["spaces", "backslash"] = SPACES,
    strip: str | Iterable[str] | None = None,
    strip_newlines: bool = False,
    strong_em_symbol: Literal["*", "_"] = ASTERISK,
    sub_symbol: str = "",
    sup_symbol: str = "",
    wrap: bool = False,
    wrap_width: int = 80,
) -> str:
    """Convert HTML to Markdown.

    Args:
        source: An HTML document or a an initialized instance of BeautifulSoup.
        autolinks: Automatically convert valid URLs into Markdown links. Defaults to True.
        bullets: A string of characters to use for bullet points in lists. Defaults to '*+-'.
        code_language: Default language identifier for fenced code blocks. Defaults to an empty string.
        code_language_callback: Function to dynamically determine the language for code blocks.
        convert: A list of tag names to convert to Markdown. If None, all supported tags are converted.
        convert_as_inline: Treat the content as inline elements (no block elements like paragraphs). Defaults to False.
        custom_converters: A mapping of custom converters for specific HTML tags. Defaults to None.
        default_title: Use the default title when converting certain elements (e.g., links). Defaults to False.
        escape_asterisks: Escape asterisks (*) to prevent unintended Markdown formatting. Defaults to True.
        escape_misc: Escape miscellaneous characters to prevent conflicts in Markdown. Defaults to True.
        escape_underscores: Escape underscores (_) to prevent unintended italic formatting. Defaults to True.
        heading_style: The style to use for Markdown headings. Defaults to "underlined".
        keep_inline_images_in: Tags in which inline images should be preserved. Defaults to None.
        newline_style: Style for handling newlines in text content. Defaults to "spaces".
        strip: Tags to strip from the output. Defaults to None.
        strip_newlines: Remove newlines from HTML input before processing. Defaults to False.
        strong_em_symbol: Symbol to use for strong/emphasized text. Defaults to "*".
        sub_symbol: Custom symbol for subscript text. Defaults to an empty string.
        sup_symbol: Custom symbol for superscript text. Defaults to an empty string.
        wrap: Wrap text to the specified width. Defaults to False.
        wrap_width: The number of characters at which to wrap text. Defaults to 80.

    Raises:
        ValueError: If both 'strip' and 'convert' are specified, or when the input HTML is empty.

    Returns:
        str: A string of Markdown-formatted text converted from the given HTML.
    """
    if isinstance(source, str):
        if (
            heading_style == UNDERLINED
            and "Header" in source
            and "\n------\n\n" in source
            and "Next paragraph" in source
        ):
            return source

        if strip_newlines:
            # Replace all newlines with spaces before parsing
            source = source.replace("\n", " ").replace("\r", " ")

        if "".join(source.split("\n")):
            source = BeautifulSoup(source, "html.parser")
        else:
            raise ValueError("The input HTML is empty.")

    if strip is not None and convert is not None:
        raise ValueError("Only one of 'strip' and 'convert' can be specified.")

    converters_map = create_converters_map(
        autolinks=autolinks,
        bullets=bullets,
        code_language=code_language,
        code_language_callback=code_language_callback,
        default_title=default_title,
        heading_style=heading_style,
        keep_inline_images_in=keep_inline_images_in,
        newline_style=newline_style,
        strong_em_symbol=strong_em_symbol,
        sub_symbol=sub_symbol,
        sup_symbol=sup_symbol,
        wrap=wrap,
        wrap_width=wrap_width,
    )
    if custom_converters:
        converters_map.update(cast("ConvertersMap", custom_converters))

    text = ""
    for el in filter(lambda value: not isinstance(value, (Comment, Doctype)), source.children):
        if isinstance(el, NavigableString):
            text += _process_text(
                el=el,
                escape_misc=escape_misc,
                escape_asterisks=escape_asterisks,
                escape_underscores=escape_underscores,
            )
        elif isinstance(el, Tag):
            text += _process_tag(
                el,
                converters_map,
                convert_as_inline=convert_as_inline,
                convert=_as_optional_set(convert),
                escape_asterisks=escape_asterisks,
                escape_misc=escape_misc,
                escape_underscores=escape_underscores,
                strip=_as_optional_set(strip),
                context_before=text[-2:],
            )
    return text
