import pathlib
from collections import defaultdict

import pytest
from render_engine import Collection, Page, Site

from subcollections.plugin import SubCollections, SubCollector


def test_subcollection(tmp_path):
    """Tests that a subcollection will create a page with the pages"""

    class TestPage(Page):
        content = "Some Content"  # Page needs either content or a template

    page1 = TestPage()
    page2 = TestPage()
    page3 = TestPage()

    page1.title = "Page1"
    page2.title = "Page2"
    page3.title = "Page3"

    output_path = tmp_path / "output"

    site = Site()
    site.output_path = output_path

    class TestSubCollector(SubCollector):
        name = "last_1"

        def generate_subcollection(self):
            """This simple subcollection generator will create a value based on the last character in the page's title."""
            pages = defaultdict(set)

            for subcollection_page in self.collection:
                pages[str(subcollection_page.title[-1])].add(subcollection_page)

            for page_title, subpages in pages.items():
                page = self.gen_page(page_title, subpages)

                yield page

    class TestCollection(Collection):
        pages = [page1, page2, page3]
        plugins = [SubCollections]
        has_feed = False
        subcollections = [TestSubCollector]

    site.collection(TestCollection)
    site.render()

    for path in ("1.html", "2.html", "3.html"):
        test_path = pathlib.Path(output_path / "last_1" / path)
        assert test_path.exists()
