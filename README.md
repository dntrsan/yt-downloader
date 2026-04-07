# YT-Downloader

YouTube動画をダウンロードできるWebアプリケーションです。

## 機能

- YouTube動画のダウンロード（4K / 1080p / 720p）
- MP3形式での音声抽出（320kbps）
- リアルタイム進捗表示
- 和風デザイン

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

**Linux (Ubuntu/Debian):**
```bash
sudo apt install ffmpeg
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

## developed by dontaro

*This README was written by claudeくん*
