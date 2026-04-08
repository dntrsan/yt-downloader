# YT-downloader v1.2

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

作成: どんたろぬす

先生およびREADME: claude先生
