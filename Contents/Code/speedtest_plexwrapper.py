#!/usr/bin/env python

"""
Speedtest Plex-Wrapper
    Used with modified speedtest-cli.py
    https://github.com/sivel/speedtest-cli

Twoure 01/09/2017
"""

import speedtest

class SeedTestPlexWrapper(object):
    def __init__(self, prefix):
        self.event = Thread.Event()
        self.st = speedtest.Speedtest()
        self.header = None
        self.message = None
        self.bits = {'0': '', '1': 'K', '2': 'M', '3': 'G', '4': 'T', '5': 'P', '6': 'E', '7': 'Z', '8': 'Y'}

        Route.Connect(prefix + '/stpw', self.action)
        Route.Connect(prefix + '/stpw/gui', self.gui, include_container=bool)
        Route.Connect(prefix + '/stpw/request', self.request)
        Route.Connect(prefix + '/stpw/photo/create', self.create_photo_object, include_container=bool)

    def create_photo_object(self, url, include_container=False):
        po = PhotoObject(
            key=Callback(self.create_photo_object, url=url, include_container=True),
            rating_key=url,
            source_title="SpeedTest",
            title=url.split('/')[-1],
            thumb=url,
            items=[
                MediaObject(parts=[
                    PartObject(key=url)
                    ])
                ]
            )
        if include_container:
            return ObjectContainer(objects=[po])
        return po

    def up_down_strings(self, u=False):
        index = 0
        if (self.st.results.download != 0) and (self.st.results.upload != 0):
            num = self.st.results.upload if u else self.st.results.download
        elif 'st' in Dict:
            num = Dict['st']['upload'] if u else Dict['st']['download']
        else:
            return "NA"

        while (num >= 1000):
            num = num/1000
            index += 1
        return "{0:.2f} {1}b/s".format(num, self.bits[str(index)])

    @property
    def download_str(self):
        return self.up_down_strings()

    @property
    def upload_str(self):
        return self.up_down_strings(True)

    def gui(self, oc=None, include_container=False):
        """st_gui menus"""
        if not oc:
            include_container = True
            oc = ObjectContainer(title2="Updating info...", no_cache=True)

        if (self.st.results.download != 0) and (self.st.results.upload != 0):
            date = self.st.results.timestamp
        elif 'st' in Dict:
            date = Dict['st']['timestamp']
        else:
            date = None

        if self.request(oc):
            if date:
                date = Datetime.ParseDate(date, "%Y-%m-%dT%H:%M:%S").replace(microsecond=0)
                oc.add(PopupDirectoryObject(
                    key=Callback(self.gui, oc=None),
                    title="D: {} | U: {} ({})".format(self.download_str, self.upload_str, date),
                    ))
                if 'thumb' in Dict['st']:
                    oc.add(self.create_photo_object(url=Dict['st']['thumb']))

            oc.add(PopupDirectoryObject(
                key=Callback(self.request, oc=oc, start=True, d=True, u=True),
                title="Default Speedtest",
                ))
            oc.add(PopupDirectoryObject(
                key=Callback(self.request, oc=oc, start=True, d=True),
                title="Download Only",
                ))
            oc.add(PopupDirectoryObject(
                key=Callback(self.request, oc=oc, start=True, u=True),
                title="Upload Only",
                ))

        if include_container:
            return oc

    def action(self, d, u):
        self.header = "Speedtest Running"
        self.message = "Retrieving best server..."

        # clear last results
        self.st.results.clear()

        # get best server
        self.st.get_best_server()
        Log("* Best Server = {}".format(self.st.results.server))

        # test download speed if requested
        if d:
            self.message = "Testing download speed..."
            self.st.download()
            Log("* Download = {} b/s".format(self.st.results.download))

        # test upload speed if requested
        if u:
            self.message = "Testing upload speed..."
            self.st.upload()
            Log("* Upload = {} b/s".format(self.st.results.upload))

        # get share URL thumb if possible
        thumb = None
        if (self.st.results.upload != 0) and (self.st.results.download != 0):
            self.message = "Retrieving share URL thumb..."
            thumb = self.st.results.share()
        if thumb and (thumb.split('/')[-1] == '0.png'):
            self.message = "No thumb for content..."
            thumb = None

        # get results as dict() and add thumb if exist
        res = self.st.results.dict()
        if thumb:
            res['thumb'] = thumb

        Log("* Speedtest resutls = {}".format(res))
        # put results into Dict, for use on next startup
        Dict['st'] = res
        Dict.Save()

        # reset threading event for next time :D
        self.event.set()
        self.header = None
        self.message = None
        return

    def request(self, oc=None, start=False, d=False, u=False):
        if start:
            if hasattr(self, 'que_thread') and self.que_thread.is_alive():
                Log("* Asked to start, but thread already running. Skipping until finished.")
            else:
                self.event.clear()
                Log("* Starting Speedtest Thread")
                self.que_thread = Thread.Create(self.action, d=d, u=u)
            return self.gui()
        elif hasattr(self, 'que_thread') and self.event.is_set():
            Log("* {}".format(self.que_thread))
            Log("* {}".format(self.que_thread.is_alive()))
            Log("* Speedtest Finished")
            return True
        elif hasattr(self, 'que_thread') and self.que_thread.is_alive():
            Log('* {}'.format(self.que_thread))
            Log('* Thread Status = {}'.format(self.que_thread.is_alive()))
            Log("* Speedtest running")
            if oc:
                oc.header = self.header
                oc.message = self.message
        elif hasattr(self, 'que_thread') and not self.que_thread.is_alive():
            Log('* {}'.format(self.que_thread))
            Log('* Thread Status = {}'.format(self.que_thread.is_alive()))
            Log.Critical("* SeedtestPlexWrapper unexpected Error.  Please contact Twoure with issue.")
        else:
            Log("* Skipping Speedtest")
            return True
        return False
