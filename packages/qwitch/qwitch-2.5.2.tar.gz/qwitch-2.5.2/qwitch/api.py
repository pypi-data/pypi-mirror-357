import requests
import json
import subprocess
import re
import sys
import os
from streamlink.options import Options
from streamlink.session import Streamlink
from . import config

CLIENT_ID = "s3e3q8l6ub08tf7ka9tg2myvetf5cf"

if sys.stdin.isatty() and not os.environ.get('QWITCH_SERVER', ''):
    C = {
        'purple': '\033[95m',
        'red': '\033[91m',
        'bold': '\033[1m',
        'esc': '\033[0m'
    }
else:
    C = {
        'purple': '',
        'red': '',
        'bold': '',
        'esc': ''
    }


class TwitchAPI:

    last_data = []
    last_cursor = ""

    def __init__(self, token: str) -> None:
        with open(
            config.home_dir + "/qwitch/config.json", "r", encoding="utf-8"
        ) as cache:
            cache_json = json.loads(cache.read())
            config.debug_log("Config read:", cache_json)

        self.user_id = cache_json[0]["user_id"]
        self.token = token
        self.headers = {"Client-Id": CLIENT_ID, "Authorization": "Bearer " + token}

    def get(self, url: str, nmbr_items: int = 20) -> bool:
        self.last_cursor = ""

        if nmbr_items > 20:
            url += "&first=" + str(nmbr_items)

        res_get = requests.get(url=url, headers=self.headers)

        config.debug_log(
            "From URL:", url, "with token:", self.token, "API returned:", res_get
        )

        if res_get.status_code == 401:
            print(
                "Your access token may have expired. Please authenticate again and try again."
            )
            config.auth_api()
            exit()

        res_get = res_get.json()

        try:
            if not res_get["data"]:
                return False
            self.last_data = res_get["data"]
            try:
                self.last_cursor = res_get["pagination"]["cursor"]
            except:
                pass
            return True
        except:
            return False

    def get_next_page(self, url: str) -> bool:
        if not self.last_cursor:
            return False

        url += "&first=99&after=" + self.last_cursor
        res_get = requests.get(url=url, headers=self.headers)

        config.debug_log(
            "From URL:", url, "with token:", self.token, "API returned:", res_get
        )

        if res_get.status_code == 401:
            print(
                "Your access token may have expired. Please authenticate again and try again."
            )
            config.auth_api()
            exit()

        res_get = res_get.json()

        try:
            if not res_get["data"]:
                return False
            self.last_data += res_get["data"]
            if res_get["pagination"]:
                self.last_cursor = res_get["pagination"]["cursor"]
                return True
            self.last_cursor = ""
            return False
        except:
            return False

    ##
    # get_livestreams()
    #
    # Gets and prints followed channels currently streaming
    #
    # @param token string auth token gathered from authenticating user
    #
    # @return nothing
    ##
    def get_livestreams(self) -> None:
        url = "https://api.twitch.tv/helix/channels/followed?user_id=" + self.user_id
        if not self.get(url=url, nmbr_items=100):
            return

        while True:
            if not self.get_next_page(url=url):
                break

        follows = self.last_data
        url = "https://api.twitch.tv/helix/streams?type=live"
        i = 0
        max_idx = len(follows)

        print(
            "Here are the current livestreams you follow:\n(The channel name you will need is in red)\n"
        )

        while i < max_idx:
            j = 0

            while j < 100 and i + j < max_idx:
                url += "&user_id=" + follows[i + j]["broadcaster_id"]
                j += 1

            if not self.get(url=url):
                print(f"{C['red']}{C['bold']}No one you follow is currently streaming.{C['esc']}")
                return

            for video in self.last_data:
                print(f"{C['purple']}Streamer:{C['esc']}      {video["user_name"]} ({C['red']}{C['bold']}{video["user_login"]}{C['esc']})")
                print(f"{C['purple']}Title:{C['esc']}         {video["title"]}")
                print(f"{C['purple']}Game/Category:{C['esc']} {video["game_name"]}")
                print("\n-------------------------------------------------------------------\n")

            i += j + 1

    ##
    # get_follows()
    #
    # Gets and prints followed channels
    #
    # @param token string auth token gathered from authenticating user
    #
    # @return nothing
    ##
    def get_follows(self) -> None:
        url = "https://api.twitch.tv/helix/channels/followed?user_id=" + self.user_id
        if not self.get(url=url, nmbr_items=100):
            return

        while True:
            if not self.get_next_page(url=url):
                break

        print(
            "Here are the channels you follow:\n(The channel name you will need is in red)\n"
        )

        for video in self.last_data:
            print(f"{C['purple']}Channel Display Name:{C['esc']}        {video["broadcaster_name"]}")
            print(f"{C['purple']}Channel Name:{C['esc']}                {C['red']}{C['bold']}{video["broadcaster_login"]}{C['esc']}")
            date = video["followed_at"].replace("T", " ").replace("Z", "")
            print(f"{C['purple']}Followed on:{C['esc']}                 {date}")
            print("-------------------------------")

    ##
    # get_channel_id()
    #
    # Gets the twitch channel ID for the given channel name
    #
    # @param token string auth token gathered from authenticating user
    # @param channel string channel name for which to get the channel ID
    #
    # @return integer the retrieved channel ID
    #
    # @remark this will raise a runtime error if the channel ID was not in the server's response
    ##
    def get_channel_id(self, channel: str) -> str:
        url = "https://api.twitch.tv/helix/users?login=" + channel
        if not self.get(url=url):
            raise RuntimeError

        try:
            return self.last_data[0]["id"]
        except:
            raise RuntimeError

    def get_vod(self, channel_id: str, keyword: str = "") -> str:
        url = (
            "https://api.twitch.tv/helix/videos?user_id=" + channel_id + "&type=archive"
        )
        if not self.get(url=url, nmbr_items=100):
            exit()

        if keyword == "":
            print(f"{C['purple']}Selected video:{C['esc']} {self.last_data[0]["title"]}")
            if os.environ.get('QWITCH_SERVER', ''):
                return self.last_data[0]["url"]

            resp = input("Play this video ? [y/N] ")
            if resp.lower() != "y":
                exit()
            return self.last_data[0]["url"]

        break_next = False

        while True:
            for vod in self.last_data:
                match = vod["title"].lower().find(keyword.lower())
                if match != -1:
                    print(f"{C['purple']}Selected video:{C['esc']} {vod["title"]}")
                    if os.environ.get('QWITCH_SERVER', ''):
                        return vod["url"]

                    resp = input("Play this video ? [y/N] ")
                    if resp.lower() != "y":
                        exit()
                    return vod["url"]

            resp = input("Next page ? [y/N] ")
            if resp.lower() != "y":
                exit()

            self.last_data = []
            if break_next:
                exit()
            break_next = not self.get_next_page(url=url)

    ##
    # print_vod_list()
    #
    # Gets and prints the 100 latest VODs of the channel
    #
    # @param token string auth token gathered from authenticating user
    # @param channel_id integer channel ID for which to get the VOD list
    #
    # @return string URL of the video that was chosen to be played
    #         none otherwise
    ##
    def print_vod_list(self, channel_id: str) -> str | None:
        url = (
            "https://api.twitch.tv/helix/videos?user_id=" + channel_id + "&type=archive"
        )
        if not self.get(url=url, nmbr_items=100):
            return None

        print("Here are the latest videos (most recent first):\n")

        break_next = False

        while True:
            for video in self.last_data:
                print(f"{C['purple']}Title:{C['esc']}        {video["title"]}")
                date = video["published_at"].replace("T", " ").replace("Z", "")
                print(f"{C['purple']}Published on:{C['esc']} {date}")
                print(f"{C['purple']}Duration:{C['esc']}     {video["duration"]}")
                print(f"{C['purple']}URL:{C['esc']}          {video["url"]}")
                print(f"{C['purple']}Video ID:{C['esc']}     {video["id"]}")

                if os.environ.get('QWITCH_SERVER', ''):
                    continue

                resp = input("\nPlay this video? [y/N] ")
                if str(resp).lower() == "y":
                    url = video["url"].replace("https://www.", "")
                    return url
                print("-------------------------------")

            if os.environ.get('QWITCH_SERVER', ''):
                exit()

            resp = input("Next page ? [y/N] ")
            if resp.lower() != "y":
                exit()

            self.last_data = []

            if break_next:
                exit()
            break_next = not self.get_next_page(url=url)


##
# exec_streamlink()
#
# Uses Streamlink to get the video stream link and launches Quicktime with that link
#
# @param url string url of the twitch video/livestream to play
# @param streamlink_config dict containing streamlink config properties (e.g. the auth-token)
# @param quality string video quality at which to play the video
#
# @return nothing
##
def exec_streamlink(url, streamlink_config, quality=None):
    session = Streamlink()
    options = Options()

    for key in streamlink_config:
        if key == "default-stream":
            continue
        if re.match("^twitch-", key):
            option_key = key.replace("twitch-", "")
            try:
                option_value = [streamlink_config[key].split("=")]
            except:
                option_value = streamlink_config[key]
            options.set(option_key, option_value)
        else:
            session.set_option(key=key, value=streamlink_config[key])

    if "default-stream" in streamlink_config and not quality:
        quality = streamlink_config["default-stream"]
    elif not ("default-stream" in streamlink_config) and not quality:
        quality = "best"

    try:
        streamurl = session.streams(url, options)[quality].url
        if os.environ.get('QWITCH_SERVER', ''):
            print(streamurl)
            return

        cmd_str = 'open -a "quicktime player" ' + streamurl + ";"
        subprocess.run(cmd_str, shell=True)
    except:
        print(
            "An error occured with Streamlink.\n",
            "You may not be subscribed to the twitch channel you are trying to access.",
            "Alternatively, check that you are still logged into your account on twitch.com",
            "If not, get a new auth-token and update it by running:",
            "    qwitch -t",
            sep="\n",
        )
