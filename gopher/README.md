This an update to the once removed gopherlib from Python 2.5, this updated module
is not compatible with the original one shipped with Python 2.5 and below, as it
has been fully updated to be class-based and work better all around than the original
library.  Now you might be asking yourself, why revive this module, isn't Gopher dead?

Read this article located in Gopher and you tell me?
gopher://gopher.floodgap.com/0/gopher/relevance.txt

The irony being that you need a Gopher client to actually read this article.

### Usage

Using this updated library is easier than the original one, here's an example:

from gopherlib import Gopher

g = Gopher('gopher.floodgap.com')
print g.get_selector('0/gopher/relevance.txt')

This will actually display the article I mentioned above for your convenience.
Using Gopher menus is pretty easy using this library as well, here's how:

g = Gopher('gopher.floodgap.com')
mnu = g.get_root_menu()
print mnu

This will display the menu in plain text as you would see it in most clients.
You can also use some of the included functions to get additional data
from the menu:

mnu.get_data() returns a list of dictionary objects for each entry in the menu.

If you wanted to access a specific menu entry, here's how easy it is:
print mnu.get_entry(17)

This will print the document from index 17 of that menu, it will even traverse
hosts as well.

### Command-line client usage

There is also a basic command-line client included as with all Python modules
like this.  Here's the command-line format:

python gopherlib.py [-h|--help] [--host=HOST] [-p PORT|--port=PORT]
                    [-s SELECTOR|--selector=SELECTOR] [-q QUERY|--query QUERY]
                    [HOST SELECTOR]

For example to access the root of my own gopher server:
python gopherlib.py --host=gopher.veroneau.net

To download this library from my gopher server:
python gopherlib.py gopher.veroneau.net 0library/gopherlib.py > gopherlib.py
