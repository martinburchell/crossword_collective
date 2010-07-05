from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        self.pdf_url = False
        HTMLParser.__init__(self)
             
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == u"href" and attr[1][-4:] == u".pdf":
                    self.pdf_url = attr[1]
