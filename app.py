import os
import re
import shutil
import uuid
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import yt_dlp

app = Flask(__name__)
app.config["SECRET_KEY"] = "yt-downloader-secret"
socketio = SocketIO(app, cors_allowed_origins="*")

@app.after_request
def remove_server_header(response):
    response.headers["Server"] = "Server"
    response.headers.pop("X-Powered-By", None)
    return response

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

FFMPEG_PATH = shutil.which("ffmpeg")
FFMPEG_DIR = os.path.dirname(FFMPEG_PATH) if FFMPEG_PATH else None

downloads = {}


class ProgressHook:
    def __init__(self, task_id):
        self.task_id = task_id

    def __call__(self, d):
        if d["status"] == "downloading":
            percent_str = d.get("_percent_str", "0%").strip()
            speed = d.get("_speed_str", "N/A").strip()
            eta = d.get("_eta_str", "N/A").strip()
            downloaded = d.get("_downloaded_bytes_str", "N/A")
            total = d.get("_total_bytes_str", d.get("_total_bytes_estimate_str", "N/A"))

            try:
                percent = float(percent_str.replace("%", ""))
            except (ValueError, AttributeError):
                percent = 0

            socketio.emit("progress", {
                "task_id": self.task_id,
                "status": "downloading",
                "percent": percent,
                "speed": speed,
                "eta": eta,
                "downloaded": downloaded,
                "total": total,
                "detail": f"ダウンロード中... {percent_str} ({downloaded} / {total}) 速度: {speed} 残り: {eta}",
            })

        elif d["status"] == "finished":
            socketio.emit("progress", {
                "task_id": self.task_id,
                "status": "processing",
                "percent": 100,
                "detail": "変換処理中...",
            })

        elif d["status"] == "error":
            socketio.emit("progress", {
                "task_id": self.task_id,
                "status": "error",
                "detail": "エラーが発生しました",
            })


def postprocessor_hook(task_id):
    def hook(d):
        if d["status"] == "started":
            socketio.emit("progress", {
                "task_id": task_id,
                "status": "processing",
                "percent": 100,
                "detail": f"後処理中: {d.get('postprocessor', 'processing')}...",
            })
        elif d["status"] == "finished":
            socketio.emit("progress", {
                "task_id": task_id,
                "status": "processing",
                "percent": 100,
                "detail": "後処理完了",
            })
    return hook


def do_download(task_id, url, quality):
    try:
        socketio.emit("progress", {
            "task_id": task_id,
            "status": "starting",
            "percent": 0,
            "detail": "動画情報を取得中...",
        })

        outtmpl = os.path.join(DOWNLOAD_DIR, f"{task_id}_%(title)s.%(ext)s")

        common_opts = {
            "outtmpl": outtmpl,
            "progress_hooks": [ProgressHook(task_id)],
            "postprocessor_hooks": [postprocessor_hook(task_id)],
            "noplaylist": True,
        }
        if FFMPEG_DIR:
            common_opts["ffmpeg_location"] = FFMPEG_DIR

        if quality == "mp3":
            ydl_opts = {
                **common_opts,
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }],
            }
        else:
            height_map = {"4k": 2160, "1080p": 1080, "720p": 720}
            height = height_map.get(quality, 1080)

            ydl_opts = {
                **common_opts,
                "format": f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best",
                "merge_output_format": "mp4",
                "postprocessor_args": {
                    "merger": ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k"],
                },
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            socketio.emit("progress", {
                "task_id": task_id,
                "status": "extracting",
                "percent": 0,
                "detail": "動画情報を解析中...",
            })
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "Unknown")
            thumbnail = info.get("thumbnail", "")

            socketio.emit("progress", {
                "task_id": task_id,
                "status": "info",
                "percent": 0,
                "title": title,
                "thumbnail": thumbnail,
                "detail": f"「{title}」のダウンロードを開始します...",
            })

            ydl.download([url])

        downloaded_file = None
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(task_id):
                downloaded_file = f
                break

        if downloaded_file:
            downloads[task_id] = {
                "filename": downloaded_file,
                "title": title,
            }
            socketio.emit("progress", {
                "task_id": task_id,
                "status": "completed",
                "percent": 100,
                "filename": downloaded_file,
                "title": title,
                "detail": "ダウンロード完了！",
            })
        else:
            socketio.emit("progress", {
                "task_id": task_id,
                "status": "error",
                "detail": "ファイルが見つかりませんでした",
            })

    except Exception as e:
        error_msg = str(e)
        if "is not a valid URL" in error_msg:
            error_msg = "無効なURLです。正しいURLを入力してください。"
        elif "Video unavailable" in error_msg:
            error_msg = "この動画は利用できません。"
        elif "Private video" in error_msg:
            error_msg = "非公開動画のためダウンロードできません。"

        socketio.emit("progress", {
            "task_id": task_id,
            "status": "error",
            "detail": f"エラー: {error_msg}",
        })


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/download", methods=["POST"])
def start_download():
    data = request.get_json()
    url = data.get("url", "").strip()
    quality = data.get("quality", "1080p")

    if not url:
        return jsonify({"error": "URLを入力してください"}), 400

    if not re.match(r"https?://.+", url):
        return jsonify({"error": "有効なURLを入力してください"}), 400

    task_id = str(uuid.uuid4())[:8]
    thread = threading.Thread(target=do_download, args=(task_id, url, quality), daemon=True)
    thread.start()

    return jsonify({"task_id": task_id})


@app.route("/api/file/<filename>")
def download_file(filename):
    safe_filename = os.path.basename(filename)
    return send_from_directory(DOWNLOAD_DIR, safe_filename, as_attachment=True)


if __name__ == "__main__":
    print("=" * 50)
    print("  YT-downloader v1.2")
    print("  http://localhost:5000")
    print("=" * 50)
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
