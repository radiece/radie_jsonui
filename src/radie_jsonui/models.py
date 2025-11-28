"""Pydantic models describing the radie_jsonui schema."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

SectionType = Literal[
    "hero",
    "markdown",
    "cards",
    "callout",
    "stats",
    "code",
    "timeline",
    "faq",
    "columns",
    "tabs",
    "accordion",
]


class Meta(BaseModel):
    title: str
    description: str | None = None
    language: str = "en"
    favicon: str | None = None
    og_image: str | None = Field(default=None, alias="ogImage")


class ThemeColors(BaseModel):
    primary: str = "#0d6efd"
    secondary: str = "#6610f2"
    surface: str = "#ffffff"
    muted: str = "#f8f9fa"


class ThemeTypography(BaseModel):
    font_family: str = Field(
        default="Inter, system-ui, -apple-system, BlinkMacSystemFont",
        alias="fontFamily",
    )
    headings_font: str = Field(default="Space Grotesk, Inter, sans-serif", alias="headingsFont")
    base_size: str = Field(default="1rem", alias="baseSize")


class ThemeLayout(BaseModel):
    max_width: str = Field(default="960px", alias="maxWidth")
    gutter: str = "1.5rem"
    radius: str = "0.75rem"


class Theme(BaseModel):
    colors: ThemeColors = Field(default_factory=ThemeColors)
    typography: ThemeTypography = Field(default_factory=ThemeTypography)
    layout: ThemeLayout = Field(default_factory=ThemeLayout)


class NavLink(BaseModel):
    label: str
    href: str
    external: bool = False


class Navigation(BaseModel):
    brand: str | None = None
    links: list[NavLink] = Field(default_factory=list)


class FooterLink(BaseModel):
    label: str
    href: str
    external: bool = False


class Footer(BaseModel):
    text: str | None = None
    links: list[FooterLink] = Field(default_factory=list)


class ActionLink(BaseModel):
    label: str
    href: str
    variant: Literal["primary", "secondary", "link"] = "primary"
    external: bool = False


class MediaAsset(BaseModel):
    src: str
    alt: str | None = None
    caption: str | None = None


class SectionBase(BaseModel):
    id: str | None = None


class HeroSection(SectionBase):
    type: Literal["hero"] = "hero"
    heading: str = ""
    subheading: str = ""
    actions: list[ActionLink] = Field(default_factory=list)
    media: MediaAsset | None = None


class MarkdownSection(SectionBase):
    type: Literal["markdown"] = "markdown"
    content: str = ""
    background: Literal["default", "muted"] = "default"
    columns: int = 1
    rendered_html: str | None = None


class CardAction(ActionLink):
    pass


class CardItem(BaseModel):
    title: str
    body: str
    icon: str | None = None
    badge: str | None = None
    actions: list[CardAction] = Field(default_factory=list)


class CardsSection(SectionBase):
    type: Literal["cards"] = "cards"
    title: str | None = None
    layout: Literal["grid", "list"] = "grid"
    cards: list[CardItem] = Field(default_factory=list, alias="items")


class CalloutSection(SectionBase):
    type: Literal["callout"] = "callout"
    title: str = ""
    body: str = ""
    variant: Literal["info", "success", "warning", "danger"] = "info"
    actions: list[ActionLink] = Field(default_factory=list)


class StatItem(BaseModel):
    label: str
    value: str
    description: str | None = None


class StatsSection(SectionBase):
    type: Literal["stats"] = "stats"
    title: str | None = None
    stats: list[StatItem] = Field(default_factory=list, alias="items")


class CodeSection(SectionBase):
    type: Literal["code"] = "code"
    title: str | None = None
    language: str = ""
    content: str = ""
    show_line_numbers: bool = Field(default=True, alias="showLineNumbers")


class TimelineItem(BaseModel):
    title: str
    description: str
    timestamp: str | None = None
    status: Literal["pending", "active", "done"] | None = None


class TimelineSection(SectionBase):
    type: Literal["timeline"] = "timeline"
    title: str | None = None
    events: list[TimelineItem] = Field(default_factory=list, alias="items")


class FaqItem(BaseModel):
    question: str
    answer: str


class FaqSection(SectionBase):
    type: Literal["faq"] = "faq"
    title: str | None = None
    faqs: list[FaqItem] = Field(default_factory=list, alias="items")


class Column(BaseModel):
    width: int | str = "col"
    sections: list[Section] = Field(default_factory=list)


class ColumnsSection(SectionBase):
    type: Literal["columns"] = "columns"
    columns: list[Column] = Field(default_factory=list)


class Tab(BaseModel):
    label: str
    sections: list[Section] = Field(default_factory=list)


class TabsSection(SectionBase):
    type: Literal["tabs"] = "tabs"
    tabs: list[Tab] = Field(default_factory=list, alias="items")


class AccordionItem(BaseModel):
    title: str
    sections: list[Section] = Field(default_factory=list)


class AccordionSection(SectionBase):
    type: Literal["accordion"] = "accordion"
    panels: list[AccordionItem] = Field(default_factory=list, alias="items")


Section = Annotated[
    HeroSection
    | MarkdownSection
    | CardsSection
    | CalloutSection
    | StatsSection
    | CodeSection
    | TimelineSection
    | FaqSection
    | ColumnsSection
    | TabsSection
    | AccordionSection,
    Field(discriminator="type"),
]


class Page(BaseModel):
    path: str = "index.html"
    title: str | None = None
    sections: list[Section] = Field(default_factory=list)


class SiteConfig(BaseModel):
    meta: Meta
    pages: list[Page] = Field(default_factory=list)
    theme: Theme = Field(default_factory=Theme)
    navigation: Navigation | None = None
    footer: Footer | None = None
