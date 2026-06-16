# bilibili-downloader (saved copy)

Download audio (and video) streams from Bilibili videos. Saved here on **2026-06-16**
for personal use. **This is third-party code — read the provenance + audit below
before trusting or running it.**

## Provenance

- **Source repo:** `github.com/958877748/skills` → path `skills/bilibili-downloader/`
- **Author:** `958877748` — a **numeric-username, anonymous third-party GitHub account**.
  Not official, not a known/trusted org. Treat accordingly.
- **Discovered via:** [skills.sh](https://skills.sh/958877748/skills/bilibili-downloader) (510 installs at time of save)
- **Raw URLs (correct path — note the nested `skills/` dir):**
  - `https://raw.githubusercontent.com/958877748/skills/main/skills/bilibili-downloader/download.cjs`
  - `https://raw.githubusercontent.com/958877748/skills/main/skills/bilibili-downloader/SKILL.md`
- **Not installed as an agent skill.** Copying external code into `~/.claude/skills/`
  is hard-blocked in this environment (Self-Modification + Untrusted-Code-Integration).
  This copy lives in a plain code dir and does **not** auto-execute.

## Audit (2026-06-16) — PASS

Reviewed `download.cjs` line-by-line. Findings:

| Check | Result |
|---|---|
| Dependencies | Node built-ins only: `https`, `http`, `fs`, `path`. No npm `require`. |
| Command execution | None. No `child_process`, `exec`, `spawn`, `execFile`, `eval`. |
| Network targets | Only `api.bilibili.com` (info + playurl) and Bilibili's media CDN URLs returned by that API. No third-party/telemetry/callback domains. |
| Credentials | Sends **no cookie**. Does not read env vars or files. Your Bilibili credentials cannot leak through it. |
| Path traversal | Filenames are `${bvid}_*.mp4`; bvid is regex-`BV[a-zA-Z0-9]+` — alphanumeric only. Safe. |

Re-verified after save: `grep` confirms only built-in `require()`s, no forbidden patterns,
only `api.bilibili.com` / `www.bilibili.com` (the latter as Referer/Origin header values).

## Files

| File | Lines | What it does |
|---|---|---|
| `SKILL.md` | 34 | Upstream skill metadata/usage doc (unmodified). |
| `download.cjs` | 256 | **Upstream original.** Downloads BOTH `{bvid}_video.mp4` and `{bvid}_audio.mp4`. |
| `download_audio_only.cjs` | 161 | **Derived variant** (written by the assistant). Same helpers, but `main()` downloads ONLY the audio stream — saves bandwidth when you just want audio. |

The audio-only variant is a strict subset of the audited original: fewer requests,
fewer file writes, identical helper functions.

## Usage

```bash
# Audio only (recommended for music):
node download_audio_only.cjs "https://www.bilibili.com/video/BVxxxxxxxx" ./out

# Video + audio (original):
node download.cjs "https://www.bilibili.com/video/BVxxxxxxxx" ./out
```

Output: `{BV}_audio.mp4` (and `{BV}_video.mp4` for the original). Convert to MP3:

```bash
ffmpeg -i BVxxxxxxxx_audio.mp4 -vn -c:a libmp3lame -b:a 192k out.mp3
```

Requires: Node.js (tested v24) and `ffmpeg` for MP3 conversion.

## Notes

- **No login/cookie needed for public videos.** The script sends no cookie. It works
  for public content out of the box.
- For **VIP/member-only** or **region/age-restricted** content this skill cannot help
  (it has no cookie support). You'd need a tool that sends `Cookie: SESSDATA=…`
  (e.g. `yt-dlp`, `BBDown`, `yutto`).
- The playurl call uses `qn=80&fnval=16` (DASH, up to 1080p). Without login the server
  may cap quality, but the audio stream (id=30280, ~173 kbps AAC) came through fine
  for the 6 videos tested.

## Integrity (sha256, as saved 2026-06-16)

```
fbaf33d9a2e0f5993178642120a07a6d02ec2e796fb053dcc4ee676db9c79384  download.cjs
068c54044f6f6345a2e573fdffea02dd2c4733af9c15280fed1cf650fd9b8c83  download_audio_only.cjs
89717856d74bc7f90f75e50f5adbfbfdfa4f02f6592e591f76f7b37908347833  SKILL.md
```

Verify before use: `sha256sum download.cjs download_audio_only.cjs SKILL.md`
