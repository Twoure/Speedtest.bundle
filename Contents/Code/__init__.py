####################################################################################################
#                                                                                                  #
#                                   Speedtest (Plex Channel)                                       #
#                                                                                                  #
####################################################################################################

TITLE = 'Speedtest'
PREFIX = '/applications/speedtest'

ICON = 'icon-default.png'
ART = 'art-default.jpg'

import speedtest_plexwrapper as STPW
STW = STPW.SeedTestPlexWrapper(PREFIX)

####################################################################################################
def Start():
    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)

    PopupDirectoryObject.thumb = R(ICON)
    PopupDirectoryObject.art = R(ART)

    HTTP.CacheTime = 0

    Log('*' * 80)
    Log(u'* Platform.OS               = {0}'.format(Platform.OS))
    Log(u'* Platform.OSVersion        = {0}'.format(Platform.OSVersion))
    Log(u'* Platform.CPU              = {0}'.format(Platform.CPU))
    Log(u'* Platform.ServerVersion    = {0}'.format(Platform.ServerVersion))
    Log('*' * 80)


####################################################################################################
@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():

    Log(u'* Client.Product            = {0}'.format(Client.Product))
    Log(u'* Client.Platform           = {0}'.format(Client.Platform))
    Log(u'* Client.Version            = {0}'.format(Client.Version))
    Log('*' * 80)

    oc = ObjectContainer(title2="Speedtest", no_cache=True)
    STW.gui(oc=oc)
    return oc
