import logging
import pathlib
from collections import defaultdict

from render_engine import Collection, Page
from render_engine.page import BasePage
from render_engine.plugins import hook_impl
from slugify import slugify


class SubCollector:
    """Perhaps an Abstract Base Class to ensure that the callable that SubCollections Uses is present"""

    name: str
    routes: list[str]

    def __init__(self, collection: Collection):
        self.collection = collection
        self.routes = list(map(lambda x: f"{x}/{self.name}", self.collection.routes))

    def gen_page(self, title: str, pages):
        """Create a page for based on the SubCollector Data and the pages data"""
        page = Page()
        page.title = title
        page.pages = pages
        page.template = self.collection.archive_template
        page.routes = self.routes
        return page

    def generate_subcollection(self):
        """
        The class that creates subcollections.

        Normally you will iterate through self.collections and create a defaultdict
        that will assign pages based on a filter
        """
        pass

    def __iter__(self):
        yield from self.generate_subcollection()


class SubCollections:

    @hook_impl
    def post_build_collection(collection, site, settings) -> None:
        """
        Build After Building the collection

        Create a new collection and render it.
        """

        if not hasattr(collection, "subcollections"):
            return

        for _subcollection in getattr(collection, "subcollections"):
            subcollection = _subcollection(collection=collection)

            for page in subcollection:
                for route in page.routes:
                    site._render_output(route, page)
