#
# A super simple XBMC JSON-RPC Interface for Python
# Control your XBMC in a Pythonic way!
#
import jsonrpclib, time

class XBMC(jsonrpclib.ServerProxy):
    def __init__(self, host, port=9090):
        super(XBMC, self).__init__('socket://%s:%s/' % (host, int(port)))
    def notification(self, title, message):
        return self.GUI.ShowNotification(title=title, message=message)
    def global_search(self, query):
        self.home()
        self.Input.Up()
        self.Input.Select()
        time.sleep(2) # Wait for keyboard on slower boxes.
        return self.Input.SendText(text=query)
    def weather(self):
        return self.GUI.ActivateWindow(window='weather')
    def home(self):
        return self.GUI.ActivateWindow(window='home')
    def favourites(self):
        return self.GUI.ActivateWindow(window='favourites')
    favorites = favourites
