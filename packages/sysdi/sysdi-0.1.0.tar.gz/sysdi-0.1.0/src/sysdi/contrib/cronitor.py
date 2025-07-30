from furl import furl

from .. import core


class WebPing(core.WebPing):
    def __init__(self, *, api_key: str, monitor_key: str):
        self.base_url = furl('https://cronitor.link/p/') / api_key / monitor_key

    def pre_url(self):
        return self.base_url.set(args={'state': 'run'}).url

    def post_ok_url(self):
        return self.base_url.set(args={'state': 'complete'}).url

    def post_fail_url(self):
        return self.base_url.set(args={'state': 'fail'}).url
