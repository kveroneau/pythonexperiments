#  Control XBMC using the Android voice control system and Python!
#  You can see a live demonstration of this on my YouTube:
#  https://www.youtube.com/watch?v=4zpTPrysNoo
#  https://www.youtube.com/watch?v=3N0j84TKYfs
#
#  In order to use this software, you will need to install the scripting layer for Android on your device:
#  https://code.google.com/p/android-scripting/
#
import android, time, xmlrpclib, socket, json, urllib

droid = android.Android()

videodb = xmlrpclib.ServerProxy('http://sys1.home.lan:7070/RPC2')
notify = xmlrpclib.ServerProxy('https://sys1.home.lan:5199/RPC2')

class VoiceActions(object):
    PREFIX_MAP = (
        'find',
        'text',
        'play',
        'tell kevin',
        'search movies for',
        'search tv shows for',
    )
    def __init__(self):
        self._xbmc_sock = None
        self._xbmc_id = 0
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
        self._xbmc_id +=1
        data = {"jsonrpc": "2.0", "method": method, "id":self._xbmc_id}
        if params:
            data.update({'params':params})
        if kwargs != {}:
            data.update({'params':kwargs})
        self._xbmc_sock.send(json.dumps(data))
        if not keep_alive:
            self._xbmc_sock.close()
            self._xbmc_sock = None
        else:
            resp = json.loads(self._xbmc_sock.recv(512))
            print resp
            return resp['result']
        return
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
    def prefix_text(self, cmd):
        self.xbmc_send('Input.SendText', text=cmd, done=True)
    def prefix_play(self, cmd):
        if cmd == 'hit music':
            self.xbmc_send('Player.Open', item={'file':'http://7639.live.streamtheworld.com:80/977_HITSAAC_SC'})
        elif cmd == 'country music':
            self.xbmc_send('Player.Open', item={'file':'http://7599.live.streamtheworld.com:80/977_COUNTRYAAC_SC'})
        elif cmd == 'random song':
            try:
                fname = videodb.random_song()
            except:
                self.say('This service requires that Kevin has his computer on.')
                self.xbmc_notification("Kevin's Voice Control", "Kevin's computer cannot be contacted.")
                return
            self.xbmc_send('Player.Open', item={'file':'smb://SYS1/Videos/Music/%s' % fname})
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
    def do_open_test_tube(self):
        self.xbmc_send('GUI.ActivateWindow', window='videolibrary', parameters=['plugin://plugin.video.testtube/?mode=1&name=Most%20Recent&slug=None&url=http%3a%2f%2ftesttube.com%2fapi%2fgetEpisodes.json%3fapi_key%3db0f696ff343bea53db564b4f54d47f19889abeaf%26grouping%3dlatest'])
    def do_open_cnet(self):
        self.xbmc_send('GUI.ActivateWindow', window='videolibrary', parameters=['plugin://plugin.video.cnet.podcasts/?mode=category&name=Latest%20Videos&url=http%3a%2f%2ffeeds2.feedburner.com%2fcnet%2fallhdpodcast'])
    def do_open_daily_fix(self):
        self.xbmc_send('GUI.ActivateWindow', window='videolibrary', parameters=['plugin://plugin.video.ign_com/?mode=listVideos&url=http%3a%2f%2fwww.ign.com%2fvideos%2fseries%2fign-daily-fix'])
    def do_open_revision3(self):
        self.xbmc_send('GUI.ActivateWindow', window='videolibrary', parameters=['plugin://plugin.video.revision3/?mode=1&name=Most%20Recent&slug=None&url=http%3a%2f%2frevision3.com%2fapi%2fgetEpisodes.json%3fapi_key%3db0f696ff343bea53db564b4f54d47f19889abeaf%26grouping%3dlatest'])
    def do_search_youtube(self):
        self.xbmc_send('GUI.ActivateWindow', window='videolibrary', parameters=['plugin://plugin.video.youtube/?folder=true&login=false&path=/root/search&store=searches'])
    def prefix_search_movies_for(self, query):
        self.xbmc_send('GUI.ActivateWindow', window='videolibrary', parameters=['plugin://plugin.video.projectfreetv/?mode=search&section=movies&name=%s' % urllib.quote(query)])
    def prefix_search_tv_shows_for(self, query):
        self.xbmc_send('GUI.ActivateWindow', window='videolibrary', parameters=['plugin://plugin.video.projectfreetv/?mode=search&section=shows&name=%s' % urllib.quote(query)])
    def prefix_tell_kevin(self, text):
        try:
            notify.notification('Message from tablet', text)
        except:
            self.say("Why don't you go tell him yourself?")

VoiceActions().run()
