#  Control XBMC using the Android voice control system and Python!
#  You can see a live demonstration of this on my YouTube:
#  https://www.youtube.com/watch?v=4zpTPrysNoo
#  https://www.youtube.com/watch?v=3N0j84TKYfs
#
#  In order to use this software, you will need to install the scripting layer for Android on your device:
#  https://code.google.com/p/android-scripting/
#
import android, time, xmlrpclib, socket, json

droid = android.Android()

videodb = xmlrpclib.ServerProxy('http://sys1.home.lan:7070/RPC2')
notify = xmlrpclib.ServerProxy('https://sys1.home.lan:5199/RPC2')

class VoiceActions(object):
    PREFIX_MAP = (
        'find',
        'enter text',
        'play',
        'tell kevin',
    )
    def __init__(self):
        self._xbmc_sock = None
    def say(self, text):
        if droid.ttsIsSpeaking().result:
            time.sleep(1)
        droid.ttsSpeak(text)
    def sanitize(self, cmd):
        return cmd.replace(' ', '_')
    def chkwifi(self):
        if droid.checkWifiState().result:
            return
        self.say('I am turning on your WiFi.')
        droid.toggleWifiState(True)
        time.sleep(10)
    def xbmc_send(self, method, params=None, keep_alive=False, **kwargs):
        self.chkwifi()
        if self._xbmc_sock is None:
            try:
                self._xbmc_sock = socket.socket()
                self._xbmc_sock.connect(('xbmc.home.lan', 9090))
            except:
                self.say('I was unable to talk with XBMC.')
                return False
        data = {"jsonrpc": "2.0", "method": method, "id":1}
        if params:
            data.update({'params':params})
        if kwargs != {}:
            data.update({'params':kwargs})
        self._xbmc_sock.send(json.dumps(data))
        resp = json.loads(self._xbmc_sock.recv(512))
        print resp
        if not keep_alive:
            self._xbmc_sock.close()
            self._xbmc_sock = None
        return resp['result']
    def xbmc_notification(self, title, message, keep_alive=False):
        self.xbmc_send('GUI.ShowNotification', title=title, message=message, keep_alive=keep_alive)
    def run(self):
        self.chkwifi()
        cmd = droid.recognizeSpeech().result.lower()
        for k in self.PREFIX_MAP:
            if cmd.find(k) == 0:
                handler = getattr(self, 'prefix_%s' % self.sanitize(k), None)
                handler(cmd[len(k)+1:])
                return
        handler = getattr(self, 'do_%s' % self.sanitize(cmd), None)
        if handler:
            handler()
        else:
            droid.makeToast('Bad command: %s' % cmd)
            self.say("I'm sorry, but I don't know how to do %s." % cmd)
    def prefix_find(self, cmd):
        self.xbmc_send('GUI.ActivateWindow', keep_alive=True, window='home')
        self.xbmc_send('Input.Up', keep_alive=True)
        self.xbmc_send('Input.Select', keep_alive=True)
        time.sleep(2)
        self.xbmc_send('Input.SendText', text=cmd, done=True)
    def prefix_enter_text(self, cmd):
        self.xbmc_send('Input.SendText', text=cmd, done=True)
    def prefix_play(self, cmd):
        if cmd == 'hit music':
            self.xbmc_send('Player.Open', item={'file':'http://7639.live.streamtheworld.com:80/977_HITSAAC_SC'})
        elif cmd == 'country music':
            self.xbmc_send('Player.Open', item={'file':'http://7599.live.streamtheworld.com:80/977_COUNTRYAAC_SC'})
        else:
            fname = False
            try:
                fname = videodb.video_path(cmd)
            except:
                self.say('This service requires that Kevin has his computer on.')
                self.xbmc_notification("Kevin's Voice Control", "Kevin's computer cannot be contacted.")
            if fname == False:
                self.xbmc_notification('Video not found', cmd)
            else:
                self.xbmc_send('Player.Open', item={'file':'smb://SYS1/Videos/Music/%s' % fname})
    def do_show_me_the_weather(self):
        self.xbmc_send('GUI.ActivateWindow', window='weather')
    def do_go_home(self):
        self.xbmc_send('GUI.ActivateWindow', window='home')
    def do_show_my_favorites(self):
        self.xbmc_send('GUI.ActivateWindow', window='favourites')
    def do_show_music_videos(self):
        self.xbmc_send('GUI.ActivateWindow', window='videolibrary', parameters=['smb://SYS1/Videos/Music/'])
    def do_power_off(self):
        self.xbmc_send('System.Shutdown')
    def do_open_menu(self):
        self.xbmc_send('Input.ContextMenu')
    def do_stop(self):
        self.xbmc_send('Player.Stop')
    def do_open_youtube(self):
        self.xbmc_send('Addons.ExecuteAddon', addonid='plugin.video.bestofyoutube_com')
    def prefix_tell_kevin(self, text):
        try:
            notify.notification('Message from tablet', text)
        except:
            self.say("Why don't you go tell him yourself?")

VoiceActions().run()
