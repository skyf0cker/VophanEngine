from urllib import parse

class Context:

    def __init__(self, pre_url="", url="", content="", title="", time=""):
        self.pre_url = pre_url
        self.url = self._fix_url(url)
        self.content = content
        self.title = title
        self.time = time

    def _fix_url(self, url):
        if url != "":
            if "http" not in url:
                t, other = parse.splittype(self.pre_url)
                host, path = parse.splithost(other)

                if url[0] != "/":
                    url = t + "://" + host + "/" + url
                else:
                    url = t + "://" + host + url
        return url

    def to_string(self):
        return self.pre_url + "|" + self.url + "|" + self.content + "|" + self.title + "|" + self.time
