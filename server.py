from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

import os
import zipfile
import tempfile
import random
import re


app = Flask(__name__)

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# ----------------------------
# 日本語文字を簡易的に分解
# ----------------------------

def make_moras(text):

    text = text.replace(
        " ",
        ""
    ).replace(
        "　",
        ""
    )

    result = []

    small = set(
        "ゃゅょぁぃぅぇぉ"
        "ャュョァィゥェォ"
    )

    for ch in text:

        if ch in "、。！？,.!?":

            continue

        if ch in small and result:

            result[-1] += ch

        else:

            result.append(ch)

    return result


# ----------------------------
# 簡易メロディ生成
# ----------------------------

def make_melody(count):

    scale = [
        60, 62, 64,
        65, 67, 69,
        71, 72
    ]

    notes = []

    for i in range(count):

        pitch = random.choice(
            scale
        )

        length = 480

        notes.append({
            "pitch": pitch,
            "length": length
        })

    return notes


# ----------------------------
# UST生成
# ----------------------------

def create_ust(moras, melody, bpm):

    lines = []

    lines.append(
        "[#SETTING]"
    )

    lines.append(
        "Tempo=%s" % bpm
    )

    lines.append(
        "ProjectName=AutoUTAU"
    )

    lines.append(
        "VoiceDir="
    )

    lines.append(
        "CacheDir="
    )

    lines.append(
        "Mode2=False"
    )

    lines.append("")

    for i, mora in enumerate(moras):

        note = melody[i]

        lines.append(
            "[#%04d]" % i
        )

        lines.append(
            "Length=%d"
            % note["length"]
        )

        lines.append(
            "Lyric=%s"
            % mora
        )

        lines.append(
            "NoteNum=%d"
            % note["pitch"]
        )

        lines.append(
            "Intensity=100"
        )

        lines.append(
            "Modulation=0"
        )

        lines.append(
            "PreUtterance="
        )

        lines.append(
            "VoiceOverlap="
        )

        lines.append("")

    lines.append(
        "[#TRACKEND]"
    )

    return "\n".join(lines)


# ----------------------------
# 音源ZIPを解析
# ----------------------------

def inspect_voicebank(zip_path):

    extract_dir = tempfile.mkdtemp(
        dir=UPLOAD_DIR
    )

    with zipfile.ZipFile(
        zip_path,
        "r"
    ) as z:

        z.extractall(
            extract_dir
        )


    oto_files = []

    wav_files = []

    for root, dirs, files in os.walk(
        extract_dir
    ):

        for file in files:

            lower = file.lower()

            if lower == "oto.ini":

                oto_files.append(
                    os.path.join(
                        root,
                        file
                    )
                )

            elif lower.endswith(".wav"):

                wav_files.append(
                    os.path.join(
                        root,
                        file
                    )
                )


    return {
        "directory": extract_dir,
        "oto": oto_files,
        "wav": wav_files
    }


# ----------------------------
# UST作成API
# ----------------------------

@app.route(
    "/api/create",
    methods=["POST"]
)
def create():

    lyrics_text = request.form.get(
        "lyrics",
        ""
    ).strip()


    if not lyrics_text:

        return (
            "歌詞がありません",
            400
        )


    voice_file = request.files.get(
        "voicebank"
    )


    bpm = random.randint(
        90,
        130
    )


    moras = make_moras(
        lyrics_text
    )


    if not moras:

        return (
            "歌詞を認識できませんでした",
            400
        )


    melody = make_melody(
        len(moras)
    )


    ust = create_ust(
        moras,
        melody,
        bpm
    )


    ust_name = (
        "song_" +
        str(random.randint(
            10000,
            99999
        )) +
        ".ust"
    )


    ust_path = os.path.join(
        UPLOAD_DIR,
        ust_name
    )


    with open(
        ust_path,
        "w",
        encoding="shift_jis",
        errors="replace"
    ) as f:

        f.write(ust)


    voicebank_name = "未選択"


    if voice_file:

        voicebank_name = (
            voice_file.filename
        )

        zip_path = os.path.join(
            UPLOAD_DIR,
            "voicebank.zip"
        )

        voice_file.save(
            zip_path
        )

        voice_info = inspect_voicebank(
            zip_path
        )

        print(
            "WAV:",
            len(voice_info["wav"])
        )

        print(
            "OTO:",
            len(voice_info["oto"])
        )


    return jsonify({

        "bpm": bpm,

        "notes": len(moras),

        "voicebank":
            voicebank_name,

        "ust":
            "/files/" +
            ust_name,

        # 現段階ではWAV合成エンジン未接続
        "wav": None

    })


@app.route(
    "/files/<path:name>"
)
def files(name):

    return send_from_directory(
        UPLOAD_DIR,
        name
    )


@app.route("/")
def index():

    return send_from_directory(
        ".",
        "index.html"
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080
    )
