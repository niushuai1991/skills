# bilibili-downloader

Download audio (and video) streams from Bilibili videos.

## Files

| File | What it does |
|---|---|
| `SKILL.md` | Skill metadata and usage doc. |
| `download.cjs` | Downloads both `{bvid}_video.mp4` and `{bvid}_audio.mp4`. |
| `download_audio_only.cjs` | Downloads only the audio stream (`{bvid}_audio.mp4`) — saves bandwidth when you just want audio. |

## Usage

```bash
# Audio only (recommended for music):
node download_audio_only.cjs "https://www.bilibili.com/video/BVxxxxxxxx" ./out

# Video + audio:
node download.cjs "https://www.bilibili.com/video/BVxxxxxxxx" ./out
```

Output: `{BV}_audio.mp4` (and `{BV}_video.mp4` for the full download). Convert to MP3:

```bash
ffmpeg -i BVxxxxxxxx_audio.mp4 -vn -c:a libmp3lame -b:a 192k out.mp3
```

Requires: Node.js and `ffmpeg` for MP3 conversion.

## Notes

- **No login/cookie needed for public videos.** The script sends no cookie and works
  for public content out of the box.
- For **VIP/member-only** or **region/age-restricted** content this skill cannot help
  (it has no cookie support). Use a tool that sends `Cookie: SESSDATA=…`
  (e.g. `yt-dlp`, `BBDown`, `yutto`).
- The playurl call uses `qn=80&fnval=16` (DASH, up to 1080p). Without login the server
  may cap quality, but the audio stream (~173 kbps AAC) comes through fine.
