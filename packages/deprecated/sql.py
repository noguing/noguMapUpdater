from packages.configreader import config_reader
import pymysql
from pymysql.converters import escape_string
from packages.deprecated.beatmap import Beatmap


def add_osu_beatmap(beatmap: Beatmap):
    config = config_reader("mysql")
    db = pymysql.connect(host=config["host"],
                         user=config["user"],
                         password=config["password"],
                         database=config["database"])

    cursor = db.cursor()

    sql = (f"INSERT INTO osubeatmaps (\n"
           f"beatmapset_id,\n"
           f"difficulty_rating,\n"
           f"id,\n"
           f"mode,\n"
           f"status,\n"
           f"total_length,\n"
           f"user_id,\n"
           f"version,\n"
           f"checksum,\n"
           f"failtimes_exit,\n"
           f"failtimes_fail,\n"
           f"accuracy,\n"
           f"ar,\n"
           f"cs,\n"
           f"drain,\n"
           f"bpm,\n"
           f"`convert`,\n"
           f"count_circles,\n"
           f"count_sliders,\n"
           f"count_spinners,\n"
           f"hit_length,\n"
           f"is_scoreable,\n"
           f"last_updated,\n"
           f"mode_int,\n"
           f"passcount,\n"
           f"playcount,\n"
           f"ranked,\n"
           f"url,\n"
           f"max_combo,\n"
           f"star_rating,\n"
           f"aim_difficulty,\n"
           f"approach_rate,\n"
           f"flashlight_difficulty,\n"
           f"overall_difficulty,\n"
           f"slider_factor,\n"
           f"speed_difficulty,\n"
           f"stamina_difficulty,\n"
           f"rhythm_difficulty,\n"
           f"colour_difficulty,\n"
           f"great_hit_window,\n"
           f"score_multiplier,\n"
           f"availability_download_disabled,\n"
           f"availability_more_information,\n"
           f"can_be_hyped,\n"
           f"creator,\n"
           f"discussion_enabled,\n"
           f"discussion_locked,\n"
           f"legacy_thread_url,\n"
           f"nominations_current,\n"
           f"nominations_required,\n"
           f"ranked_date,\n"
           f"source,\n"
           f"storyboard,\n"
           f"submitted_date,\n"
           f"tags,\n"
           f"artist,\n"
           f"artist_unicode,\n"
           f"favourite_count,\n"
           f"nsfw,\n"
           f"preview_url,\n"
           f"title,\n"
           f"title_unicode,\n"
           f"video,\n"
           f"genre,\n"
           f"language\n"
           f")\n"
           f"VALUES\n"
           f"(\n"
           f"{beatmap.beatmapset_id},\n"
           f"{beatmap.difficulty_rating},\n"
           f"{beatmap.id},\n"
           f"\"{beatmap.mode}\",\n"
           f"{beatmap.status},\n"
           f"{beatmap.total_length},\n"
           f"{beatmap.user_id},\n"
           f"\"{escape_string(beatmap.version)}\",\n"
           f"\"{beatmap.checksum}\",\n"
           f"{beatmap.failtimes_exit},\n"
           f"{beatmap.failtimes_fail},\n"
           f"{beatmap.accuracy},\n"
           f"{beatmap.ar},\n"
           f"{beatmap.cs},\n"
           f"{beatmap.drain},\n"
           f"{beatmap.bpm},\n"
           f"{beatmap.convert},\n"
           f"{beatmap.count_circles},\n"
           f"{beatmap.count_sliders},\n"
           f"{beatmap.count_spinners},\n"
           f"{beatmap.hit_length},\n"
           f"{beatmap.is_scoreable},\n"
           f"\"{beatmap.last_updated}\",\n"
           f"{beatmap.mode_int},\n"
           f"{beatmap.passcount},\n"
           f"{beatmap.playcount},\n"
           f"{beatmap.ranked},\n"
           f"\"{beatmap.url}\",\n"
           f"{beatmap.max_combo},\n"
           f"{beatmap.star_rating},\n"
           f"{beatmap.aim_difficulty},\n"
           f"{beatmap.approach_rate},\n"
           f"{beatmap.flashlight_difficulty},\n"
           f"{beatmap.overall_difficulty},\n"
           f"{beatmap.slider_factor},\n"
           f"{beatmap.speed_difficulty},\n"
           f"{beatmap.stamina_difficulty},\n"
           f"{beatmap.rhythm_difficulty},\n"
           f"{beatmap.colour_difficulty},\n"
           f"{beatmap.great_hit_window},\n"
           f"{beatmap.score_multiplier},\n"
           f"{beatmap.availability_download_disabled},\n"
           f"\"{beatmap.availability_more_information}\",\n"
           f"{beatmap.can_be_hyped},\n"
           f"\"{escape_string(beatmap.creator)}\",\n"
           f"{beatmap.discussion_enabled},\n"
           f"{beatmap.discussion_locked},\n"
           f"\"{beatmap.legacy_thread_url}\",\n"
           f"{beatmap.nominations_current},\n"
           f"{beatmap.nominations_required},\n"
           f"\"{beatmap.ranked_date}\",\n"
           f"\"{beatmap.source}\",\n"
           f"{beatmap.storyboard},\n"
           f"\"{beatmap.submitted_date}\",\n"
           f"\"{escape_string(beatmap.tags)}\",\n"
           f"\"{escape_string(beatmap.artist)}\",\n"
           f"\"{escape_string(beatmap.artist_unicode)}\",\n"
           f"{beatmap.favourite_count},\n"
           f"{beatmap.nsfw},\n"
           f"\"{beatmap.preview_url}\",\n"
           f"\"{escape_string(beatmap.title)}\",\n"
           f"\"{escape_string(beatmap.title_unicode)}\",\n"
           f"{beatmap.video},\n"
           f"\"{beatmap.genre}\",\n"
           f"\"{beatmap.language}\");")

    print(sql)
    cursor.execute(sql)
    db.commit()

    db.close()