# Render Engine Subcollections

A plugin system for [Render Engine](https://github.com/render-engine/render-engine) that enables automatic generation of subcollections based on page metadata like tags, dates, categories, and more.

## Overview

The subcollections plugin extends Render Engine's `Collection` and `Blog` classes with a powerful plugin architecture that automatically processes your content and creates organized subcollections. This makes it easy to generate tag pages, monthly archives, category listings, and any other groupings based on your page metadata.

## Features

- **Automatic subcollection generation** - Group pages by any metadata field
- **Built-in processors** - Common patterns like tags and monthly archives included
- **Plugin architecture** - Easy to create custom processors
- **Permalink generation** - Automatic URL generation for subcollection pages
- **Template support** - Custom templates for each subcollection type

## Installation

```bash
pip install render-engine-subcollections
```

## Quick Start

```python
from render_engine import Site, Blog
from render_engine_subcollections import subcollections, tags, monthly_archives

site = Site()

@site.collection
class MyBlog(Blog):
    content_path = "content/posts"

    # Register the subcollections plugin
    plugins = [subcollections]

    # Enable subcollection processing
    subcollections = [
        tags,  # Creates tag-based subcollections
        monthly_archives,  # Creates monthly archive subcollections
    ]
```

## Usage

### Basic Configuration

First, register the `subcollections` plugin, then use the `subcollections` attribute to specify processor functions or tuples containing a name and function:

```python
from render_engine_subcollections import subcollections

class MyBlog(Blog):
    content_path = "content/posts"

    # Register the plugin
    plugins = [subcollections]

    # Configure subcollections
    subcollections = [
        ("tags", process_tags),
        ("months", process_months),
        ("categories", process_categories),
    ]
```

### Built-in Processors

#### Tags Processor

Groups pages by their `tags` metadata field:

```python
from render_engine_subcollections import subcollections, tags

class MyBlog(Blog):
    plugins = [subcollections]
    subcollections = [tags]
```

This creates subcollections for each unique tag, accessible at URLs like `/tags/python/`, `/tags/javascript/`, etc.

#### Monthly Archives

Groups pages by their `date` metadata field into monthly collections:

```python
from render_engine_subcollections import subcollections, monthly_archives

class MyBlog(Blog):
    plugins = [subcollections]
    subcollections = [monthly_archives]
```

This creates subcollections for each month, accessible at URLs like `/2024/01/`, `/2024/02/`, etc.

### Creating Custom Processors

A processor is a function that takes a collection and returns a dictionary mapping subcollection names to lists of pages:

```python
from collections import defaultdict

def process_categories(collection):
    """Group pages by category metadata."""
    categories = defaultdict(list)

    for page in collection:
        if hasattr(page, 'category'):
            categories[page.category].append(page)

    return categories

def process_authors(collection):
    """Group pages by author metadata."""
    authors = defaultdict(list)

    for page in collection:
        # Handle multiple authors
        page_authors = getattr(page, 'authors', [])
        if isinstance(page_authors, str):
            page_authors = [page_authors]

        for author in page_authors:
            authors[author].append(page)

    return authors

# Use in your blog
from render_engine_subcollections import subcollections

class MyBlog(Blog):
    plugins = [subcollections]
    subcollections = [
        ("categories", process_categories),
        ("authors", process_authors),
    ]
```

### Advanced Example

```python
from datetime import datetime
from collections import defaultdict
from render_engine_subcollections import subcollections

def process_months(collection):
    """Group pages by month and year."""
    month_year = defaultdict(list)

    for page in collection:
        if hasattr(page, 'date'):
            # Parse the date string
            if isinstance(page.date, str):
                date_obj = datetime.strptime(page.date, "%Y-%m-%d")
            else:
                date_obj = page.date

            # Create month-year key
            month_key = date_obj.strftime("%B %Y")  # "January 2024"
            month_year[month_key].append(page)

    return month_year

def process_tags(collection):
    """Group pages by individual tags."""
    tags = defaultdict(list)

    for page in collection:
        page_tags = getattr(page, 'tags', [])

        # Handle both string and list formats
        if isinstance(page_tags, str):
            page_tags = [tag.strip() for tag in page_tags.split(',')]

        for tag in page_tags:
            tags[tag.lower()].append(page)

    return tags

class TechBlog(Blog):
    content_path = "content/posts"
    template = "post.html"

    plugins = [subcollections]
    subcollections = [
        ("tags", process_tags),
        ("monthly", process_months),
    ]
```

## Templates

### Subcollection Templates

Each subcollection type can have its own template. By default, subcollections use the collection's template, but you can specify custom templates:

```python
# In your processor function
def process_tags(collection):
    tags = defaultdict(list)

    for page in collection:
        for tag in getattr(page, 'tags', []):
            tags[tag].append(page)

    # Each subcollection can specify its template
    return {
        tag: {
            'pages': pages,
            'template': 'tag.html',  # Custom template for tag pages
            'title': f'Posts tagged with {tag}',
            'description': f'All posts about {tag}',
        }
        for tag, pages in tags.items()
    }
```

### Template Variables

Subcollection templates have access to:

- `pages` - List of pages in the subcollection
- `title` - Subcollection title
- `collection` - Parent collection data
- `subcollection_type` - The processor name (e.g., "tags", "months")
- `subcollection_key` - The specific subcollection identifier
- All collection template*vars prefixed with `collection*`(e.g.,`collection_site_title`, `collection_description`, etc.)

```html
<!-- tag.html template -->
<h1>{{ title }}</h1>
<p>{{ pages|length }} posts tagged with "{{ subcollection_key }}"</p>

<ul>
  {% for post in pages %}
  <li>
    <a href="{{ post.url_for() }}">{{ post.title }}</a>
    <time>{{ post.date }}</time>
  </li>
  {% endfor %}
</ul>
```

## URL Structure

Subcollections automatically generate URLs based on the collection path, subcollection name, and key:

`{collection-path}/{subcollection-name}/{key}/`

Examples:

- Tags: `/blog/tags/python/`
- Monthly archives: `/blog/monthly/january-2024/`
- Categories: `/blog/categories/web-development/`

## Integration Examples

### Complete Blog Setup

```python
from render_engine import Site, Blog
from render_engine_subcollections import tags, monthly_archives, subcollections

site = Site(
    SITE_TITLE="My Tech Blog",
    SITE_URL="https://example.com"
)

@site.collection
class Posts(Blog):
    content_path = "content/posts"
    template = "post.html"
    archive_template = "archive.html"
    has_archive = True

    plugins = [subcollections]
    subcollections = [
        tags,
        monthly_archives,
    ]

@site.page
class TagIndex:
    """Index page listing all tags"""
    template = "tag-index.html"

    def tags(self):
        # Access processed tags from the blog
        return site.collections['Posts'].subcollections.get('tags', {})

if __name__ == "__main__":
    site.render()
```

### Multi-language Blog

```python
def process_languages(collection):
    """Group posts by language."""
    languages = defaultdict(list)

    for page in collection:
        lang = getattr(page, 'language', 'en')
        languages[lang].append(page)

    return languages

from render_engine_subcollections import subcollections

class MultilangBlog(Blog):
    plugins = [subcollections]
    subcollections = [
        ("languages", process_languages),
        ("tags", process_tags),
    ]
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Render Engine](https://github.com/render-engine/render-engine) - The main static site generator
