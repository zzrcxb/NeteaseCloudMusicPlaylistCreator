import sqlite3
import json
# import codecs
import os

cx = sqlite3.connect(os.path.join(os.path.expanduser('~')+"/AppData/Local/Netease/CloudMusic/Library/webdb.dat"))
cx.row_factory = sqlite3.Row

def getPlaylist():
    cu = cx.cursor()
    cu.execute("select * from web_playlist")
    playlists = []
    for item in cu.fetchall():
        playlist = (item["pid"],getPlaylistNameFromJson(item["playlist"]))
        playlists.append(playlist)
    playlists = list(map(lambda x: (x[0], x[1].decode('GBK', 'ignore')), playlists))

    print('Listing playlists:')
    print('========= START ==========')

    for i, _ in enumerate(playlists):
        print(i, _[1])
        if i % 10 == 0 and i > 0:
            input('Press enter to continue')

    print('========== END ===========')

    try:
        index = int(input('Choose playlist you wanna export:'))
        playlist = playlists[index]
    except (IndexError, ValueError):
        print('Invalid input, exiting...')
        exit(1)
    return playlist



def getPlayListMusic(pid):
    cu = cx.cursor()
    cu.execute("select * from web_playlist_track where pid=?",[pid])
    musics = []
    for item in cu.fetchall():
        musics.append(item["tid"]);
    return musics

def getOfflineMusicDetail(tid):
    cu=cx.cursor()
    cu.execute("select * from web_offline_track where track_id=?",[tid])
    music = cu.fetchone()
    if music is None:
        return None
    detail = (getMusicNameFromJson(music["detail"]), music["relative_path"])
    return detail

def writePlaylistToFile(pid, playlistName):
    file = open(os.path.join(playlistName + ".m3u"), "w", encoding='utf-8')
    count = 0
    try:
        file.writelines("#EXTM3U")
        musicIds = getPlayListMusic(pid)
        for tid in musicIds:
            if tid is not None:
                detail = getOfflineMusicDetail(tid)
                if detail is not None:
                    count = count + 1
                    file.writelines(u"\n#EXTINF:" + detail[0] + u"\n" + detail[1])
    except Exception as e:
        raise
    else:
        pass
    finally:
        file.close()
        if count <= 0:
            os.remove(playlistName + ".m3u")

def getPlaylistNameFromJson(jsonStr):
    playlistDetail = json.loads(jsonStr)
    return playlistDetail["name"].encode("GBK", 'ignore');

def getMusicNameFromJson(jsonStr):
    musicDetail = json.loads(jsonStr)
    return musicDetail["name"];

def main():
    pid, name = getPlaylist()
    writePlaylistToFile(pid, name)

if __name__ == '__main__':
    main()