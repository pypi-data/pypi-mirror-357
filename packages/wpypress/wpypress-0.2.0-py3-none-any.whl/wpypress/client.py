from wpypress.auth import BasicAuth
from wpypress.endpoints import posts, categories, tags, pages, media, seo, products, product_categories

class WPClient:
    def __init__(self, base_url, username=None, password=None):
        self.base_url = base_url.rstrip('/')
        self.auth = BasicAuth(username, password) if username and password else None

        self.posts = posts.PostsEndpoint(self)
        self.categories = categories.CategoriesEndpoint(self)
        self.tags = tags.TagsEndpoint(self)
        self.pages = pages.PagesEndpoint(self)
        self.media = media.MediaEndpoint(self)
        self.seo = seo.SEOEndpoint(self)
        self.products = seo.ProductsEndpoint(self)
        self.product_categories = seo.ProductCategoriesEndpoint(self)
