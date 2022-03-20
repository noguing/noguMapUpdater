import httpx
import json
from requests import exceptions
from tenacity import *
from packages.beatmap import Beatmap
import datetime
from packages.getToken import get_token

headers = {"Authorization": f"Bearer {get_token(6322, 'G5Dpfd1hAgAt8zkt0aFklV8bteaZITv1vC2bxcfO')}",
           "Content-Type": "application/json",
           "Accept": "application/json"}
client = httpx.Client(headers=headers)


def request_fail() -> bool:
    return False


def get_map_from_ppy(bid: int) -> Beatmap | None:
    bm = Beatmap()

    @retry(wait=wait_fixed(2),
           stop=stop_after_attempt(3),
           retry=retry_if_exception_type(exceptions.Timeout),
           retry_error_callback=request_fail,
           reraise=True)
    def get_beatmap():
        url = f"https://osu.ppy.sh/api/v2/beatmaps/{bid}"
        resp_beatmap = client.get(url).json()
        return resp_beatmap

    info = get_beatmap()

    """@retry(wait=wait_fixed(2),
           stop=stop_after_attempt(3),
           retry=retry_if_exception_type(exceptions.Timeout),
           retry_error_callback=request_fail,
           reraise=True)
    def get_beatmap_attributes():
        url = f"https://osu.ppy.sh/api/v2/beatmaps/{bid}/attributes"
        data = {
            # "mods": [],
            "ruleset_id":  info["mode_int"]
        }
        resp_beatmap = client.post(url, data=data).json()
        return resp_beatmap

    return get_beatmap_attributes()"""

    if info == {'error': None}:
        return

    # with open("beatmap.json", "w") as f:
    #     f.write(json.dumps(info))

    bm.beatmapset_id = info["beatmapset_id"]
    bm.difficulty_rating = info["difficulty_rating"]
    bm.id = info["id"]
    bm.mode = info["mode"]
    bm.status = info["status"]
    bm.total_length = info["total_length"]
    bm.user_id = info["user_id"]
    bm.version = info["version"]
    bm.checksum = info["checksum"]
    bm.failtimes_exit = sum(info["failtimes"]["exit"])
    bm.failtimes_fail = sum(info["failtimes"]["fail"])
    bm.accuracy = info["accuracy"]
    bm.ar = info["ar"]
    bm.cs = info["cs"]
    bm.drain = info["drain"]
    bm.bpm = info["bpm"]
    bm.convert = info["convert"]
    bm.count_circles = info["count_circles"]
    bm.count_sliders = info["count_sliders"]
    bm.count_spinners = info["count_spinners"]
    bm.deleted_at
    bm.hit_length = info["hit_length"]
    bm.is_scoreable = info["is_scoreable"]
    bm.last_updated = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(info["last_updated"], "%Y-%m-%dT%H:%M:%S+00:00"))
    bm.mode_int = info["mode_int"]
    bm.passcount = info["passcount"]
    bm.playcount = info["playcount"]
    bm.ranked = info["ranked"]
    bm.url = info["url"]
    bm.max_combo = info["max_combo"]
    bm.star_rating = info["difficulty_rating"]
    bm.aim_difficulty
    bm.approach_rate = info["ar"]
    bm.flashlight_difficulty
    bm.overall_difficulty = info["accuracy"]
    bm.slider_factor
    bm.speed_difficulty
    bm.stamina_difficulty
    bm.rhythm_difficulty
    bm.colour_difficulty
    bm.great_hit_window
    bm.score_multiplier
    bm.scores
    bm.availability_download_disabled = info["beatmapset"]["availability"]["download_disabled"]
    bm.availability_more_information = info["beatmapset"]["availability"]["more_information"]
    bm.can_be_hyped = info["beatmapset"]["can_be_hyped"]
    bm.creator = info["beatmapset"]["creator"]
    bm.discussion_enabled = info["beatmapset"]["discussion_enabled"]
    bm.discussion_locked = info["beatmapset"]["discussion_locked"]
    bm.hype_current
    bm.hype_required
    bm.legacy_thread_url = info["beatmapset"]["legacy_thread_url"]
    bm.nominations_current = info["beatmapset"]["nominations_summary"]["current"]
    bm.nominations_required = info["beatmapset"]["nominations_summary"]["required"]
    bm.ranked_date = time.strftime("%Y-%m-%d %H:%M:%S",
                                   time.strptime(info["beatmapset"]["ranked_date"], "%Y-%m-%dT%H:%M:%S+00:00"))
    bm.source = info["beatmapset"]["source"]
    bm.storyboard = info["beatmapset"]["storyboard"]
    bm.submitted_date = time.strftime("%Y-%m-%d %H:%M:%S",
                                      time.strptime(info["beatmapset"]["submitted_date"], "%Y-%m-%dT%H:%M:%S+00:00"))
    bm.tags = info["beatmapset"]["tags"]
    bm.artist = info["beatmapset"]["artist"]
    bm.artist_unicode = info["beatmapset"]["artist_unicode"]
    bm.favourite_count = info["beatmapset"]["favourite_count"]
    bm.nsfw = info["beatmapset"]["nsfw"]
    bm.preview_url = info["beatmapset"]["preview_url"]
    bm.title = info["beatmapset"]["title"]
    bm.title_unicode = info["beatmapset"]["title_unicode"]
    bm.video = info["beatmapset"]["video"]
    bm.genre
    bm.language
    bm.nominations
    bm.recent_favourites

    return bm
