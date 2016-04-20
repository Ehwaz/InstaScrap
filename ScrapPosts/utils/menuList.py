import logging

logger = logging.getLogger(__name__)

class Menu:
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def getName(self):
        return self.name

    def getUrl(self):
        return self.url

class MenuList:
    menuList = [Menu('Crawl !!', "../crawl_posts"),
                Menu('Liked Posts', "../liked_posts"),
                Menu('Scrapped Posts', "../scrapped_posts")]

    @staticmethod
    def getList():
        return MenuList.menuList