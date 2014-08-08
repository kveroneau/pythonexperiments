"""Gopher protocol client interface."""
# gopher://uninformativ.de/0/gopher/RFCs/rfc1436.txt
import socket

# Recognized file types
A_TEXT       = '0'
A_MENU       = '1'
A_CSO        = '2'
A_ERROR      = '3'
A_MACBINHEX  = '4'
A_PCBINHEX   = '5'
A_UUENCODED  = '6'
A_INDEX      = '7'
A_TELNET     = '8'
A_BINARY     = '9'
A_DUPLICATE  = '+'
A_SOUND      = 's'
A_EVENT      = 'e'
A_CALENDAR   = 'c'
A_HTML       = 'h'
A_TN3270     = 'T'
A_MIME       = 'M'
A_IMAGE      = 'I'
A_WHOIS      = 'w'
A_QUERY      = 'q'
A_GIF        = 'g'
A_HTML       = 'h'          # HTML file
A_WWW        = 'w'          # WWW address
A_PLUS_IMAGE = ':'
A_PLUS_MOVIE = ';'
A_PLUS_SOUND = '<'

TEXT_TYPES = ['0', '1', '7']

class GopherType(object):
    text_only = True
    def __init__(self, data, gtype, client):
        self._data = data
        self._gtype = gtype
        self._client = client
    def get_data(self):
        return self._data
    def __str__(self):
        return self._data
    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._gtype)

class TextFile(GopherType):
    def __str__(self):
        return '\n'.join(self._data)

class GopherMenu(GopherType):
    _menu = None
    def get_data(self):
        if self._menu is None:
            self._menu = []
            for item in self._data:
                gtype = item[0]
                entry = item[1:].split('\t')
                self._menu.append({'type':gtype, 'name':entry[0], 'selector':'%s%s' % (gtype,entry[1]), 'host':entry[2], 'port':entry[3]})
        return self._menu
    def name_list(self):
        names = []
        menu = self.get_data()
        for entry in menu:
            names.append(entry['name'])
        return names
    def display_names(self):
        print '\n'.join(self.name_list())
    def get_entry(self, index):
        entry = self.get_data()[index]
        if self._client._host == entry['host'] and self._client._port == entry['port']:
            return self._client.get_selector(entry['selector'])
        g = Gopher(entry['host'], entry['port'])
        return g.get_selector(entry['selector'])
    def __str__(self):
        return '\n'.join(self.name_list())

class Gopher(object):
    def __init__(self, host, port=70):
        self._host, self._port = host, int(port)
    def send_selector(self, selector, query=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._host, self._port))
        if query is not None:
            selector += '\t%s' % query
        sock.sendall('%s\r\n' % selector)
        sock.shutdown(1)
        return sock.makefile('rb')
    def path_to_selector(self, path):
        return path[2:]
    def get_textfile(self, selector, query=None):
        f = self.send_selector(selector, query)
        lines = []
        while True:
            line = f.readline()
            if not line:
                break
            if line[-2:] == '\r\n':
                line = line[:-2]
            elif line[-1:] in '\r\n':
                line = line[:-1]
            if line == '.':
                break
            if line[:2] == '..':
                line = line[1:]
            lines.append(line)
        return lines
    def get_binary(self, selector):
        f = self.send_selector(selector)
        return f.read()
    def get_selector(self, selector, query=None):
        gtype = selector[0]
        selector = selector[1:]
        if gtype in TEXT_TYPES:
            data = self.get_textfile(selector, query)
            if gtype == '0':
                return TextFile(data, gtype, self)
            else:
                return GopherMenu(data, gtype, self)
        return self.get_binary(selector)
    def get_root_menu(self):
        return self.get_selector('1')

def test():
    """Trivial test program."""
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--host', dest='host', default='gopher.floodgap.com', help='Gopher hostname to connect to')
    parser.add_option('-p', '--port', type='int', dest='port', default=70, help='Gopher port to connect to')
    parser.add_option('-s', '--selector', dest='selector', default='0/gopher/proxy', help='Gopher selector to use')
    parser.add_option('-q', '--query', dest='query', help='Gopher search query to use.')
    options, args = parser.parse_args()
    if options.host != 'gopher.floodgap.com' and options.selector == '0/gopher/proxy':
        options.selector = '1'
    if len(args) == 2:
        options.host, options.selector = args[0:2]
    g = Gopher(options.host, options.port)
    data = g.get_selector(options.selector, options.query)
    print data

# Run the test when run as script
if __name__ == '__main__':
    test()
