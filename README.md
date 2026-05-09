# YT-downloader v1.3

YouTube動画を**広告無し**でダウンロードできる(有能)Webアプリケーションです。

## 機能

- YouTubeなどの動画のダウンロード（4K(!?) / 1080p / 720p）
- MP3形式での音声抽出（320kbps）

## 必要なもの

- Python 3.8以上
- ffmpeg

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/dntrsan/yt-downloader.git
cd yt-downloader
```

### 2. ffmpegのインストール

**Windows:**
```bash
winget install Gyan.FFmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

### 3. Pythonパッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. 起動

```bash
python app.py
```

ブラウザで http://localhost:5000 にアクセスしてください。

## 使い方

1. YouTubeのURLを入力
2. 画質・形式を選択（4K / 1080p / 720p / MP3）
3. 「ダウンロード開始」をクリック
4. 完了後「ファイルを保存」からダウンロード
5. うれしい

YouTube以外も対応しているサービスがありますが、動作未確認です。

## X / Twitter の動画について

X はログインしていない状態だと動画情報を返さないことがあります。その場合、`yt-dlp` 側で次のようなエラーになります。

- `No video could be found in this tweet`
- `Some metadata is missing without authentication`
- `Unsupported URL`

ログインが必要な投稿を取得する場合は、Cookieファイルを用意して、次のどちらかでアプリに渡してください。

```bash
# プロジェクト直下に配置する場合
cookies.txt
```

```bash
# 任意の場所を指定する場合
set YTDLP_COOKIEFILE=C:\path\to\cookies.txt
python app.py
```

`cookies.txt` は次のどちらの形式でも使えます。

```text
# Netscape形式
# Netscape HTTP Cookie File
...
```

```text
# ブラウザのリクエストヘッダーからコピーした形式
Cookie: auth_token=...; ct0=...; ...
```

リクエストヘッダーからコピーする場合は、`Cookie:` 行だけを貼り付けてください。`User-Agent:` や `Accept:` など他のヘッダーは不要です。

先に `yt-dlp` 単体で取れるか確認すると原因を切り分けやすいです。

```bash
python -m yt_dlp --cookies cookies.txt "https://x.com/ユーザー名/status/投稿ID"
```

作成: どんたろぬす

先生およびREADME: Claude Opus4.7・GPT-5.5
