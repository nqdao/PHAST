__author__ = 'Nhat-Quang'

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self, strict=False)
    def feed(self, in_html):
        self.output = ""
        super(MyHTMLParser, self).feed(in_html)
        return self.output
    def handle_data(self, data):
        self.output += data.strip()
    def handle_starttag(self, tag, attrs):
        if tag == 'li':
            self.output += linesep + '* '
        elif tag == 'blockquote' :
            self.output += linesep + linesep + '\t'
    def handle_endtag(self, tag):
        if tag == 'blockquote':
            self.output += linesep + linesep

parser = MyHTMLParser()
content = "<ul><li>One</li><li>Two</li></ul>"
print(linesep + "Example 1:")
print(parser.feed(content))
content = "Some text<blockquote>More magnificent text here</blockquote>Final text"
print(linesep + "Example 2:")
print(parser.feed(content))