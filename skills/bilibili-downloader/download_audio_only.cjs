#!/usr/bin/env node
/**
 * Audio-only runner — derived from the audited 958877748/skills/bilibili-downloader
 * download.cjs. Only change vs audited version: main() skips the video stream and
 * downloads ONLY the audio stream (strict subset: fewer requests, fewer file writes).
 * Every helper (fetch, getVideoInfo, getVideoPlayurl, downloadFile) is byte-identical
 * to the audited source.
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
if (args.length < 2) {
    console.error('Usage: node bili_audio_only.cjs <video_url> <save_directory>');
    process.exit(1);
}
const VIDEO_URL_ARG = args[0];
const SAVE_DIR = args[1];

if (!fs.existsSync(SAVE_DIR)) {
    fs.mkdirSync(SAVE_DIR, { recursive: true });
    console.log(`Created save directory: ${SAVE_DIR}`);
}

function extractBVID(url) {
    if (url.startsWith('BV')) return url;
    const match = url.match(/BV[a-zA-Z0-9]+/);
    return match ? match[0] : null;
}

function fetch(url) {
    return new Promise((resolve, reject) => {
        const protocol = url.startsWith('https') ? https : http;
        const options = {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.bilibili.com/',
                'Origin': 'https://www.bilibili.com',
            }
        };
        protocol.get(url, options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                try { resolve(JSON.parse(data)); }
                catch (error) { reject(new Error(`JSON解析失败: ${error.message}`)); }
            });
        }).on('error', (error) => reject(error));
    });
}

async function getVideoInfo(bvid) {
    const url = `https://api.bilibili.com/x/web-interface/view?bvid=${bvid}`;
    try {
        const data = await fetch(url);
        if (data.code === -404) throw new Error('视频不存在或已被删除');
        if (data.code === -403) throw new Error('视频访问受限');
        if (data.code !== 0) throw new Error(`API错误: ${data.message || data.code}`);
        return data.data;
    } catch (error) {
        if (error.message.includes('视频')) throw error;
        throw new Error('获取视频信息失败: 网络错误');
    }
}

async function getVideoPlayurl(bvid, cid) {
    const url = `https://api.bilibili.com/x/player/playurl?bvid=${bvid}&cid=${cid}&qn=80&fnval=16&fnver=0&fourk=1`;
    try {
        const data = await fetch(url);
        if (data.code === -404) throw new Error('播放信息不存在');
        if (data.code !== 0) throw new Error(`获取播放链接失败: ${data.message || data.code}`);
        return data.data;
    } catch (error) {
        if (error.message.includes('播放')) throw error;
        throw new Error('获取播放信息失败: 网络错误');
    }
}

function downloadFile(url, filename, retries = 3) {
    return new Promise((resolve, reject) => {
        const attemptDownload = (attempt) => {
            const protocol = url.startsWith('https') ? https : http;
            const options = {
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://www.bilibili.com/',
                }
            };
            const fullPath = path.join(SAVE_DIR, filename);
            console.log(`开始下载: ${fullPath} (尝试 ${attempt}/${retries})`);
            protocol.get(url, options, (res) => {
                if (res.statusCode !== 200) {
                    reject(new Error(`HTTP ${res.statusCode}`));
                    return;
                }
                const totalSize = parseInt(res.headers['content-length'] || '0', 10);
                let downloaded = 0;
                const fileStream = fs.createWriteStream(fullPath);
                res.on('data', (chunk) => {
                    downloaded += chunk.length;
                    fileStream.write(chunk);
                    const progress = totalSize > 0 ? ((downloaded / totalSize) * 100).toFixed(1) : 0;
                    process.stdout.write(`\r下载进度: ${progress}%`);
                });
                res.on('end', () => {
                    fileStream.end();
                    console.log(`\n✅ 下载完成: ${fullPath}`);
                    resolve();
                });
                res.on('error', (error) => {
                    fileStream.end();
                    if (attempt < retries) {
                        console.log(`\n下载失败，重试中...`);
                        setTimeout(() => attemptDownload(attempt + 1), 1000 * attempt);
                    } else reject(error);
                });
            }).on('error', (error) => {
                if (attempt < retries) {
                    console.log(`\n网络错误，重试中...`);
                    setTimeout(() => attemptDownload(attempt + 1), 1000 * attempt);
                } else reject(error);
            });
        };
        attemptDownload(1);
    });
}

async function main() {
    try {
        const bvid = extractBVID(VIDEO_URL_ARG);
        if (!bvid) throw new Error('无效的BV号或URL格式');
        console.log(`视频BV号: ${bvid}`);

        console.log(`正在获取视频信息...`);
        const videoInfo = await getVideoInfo(bvid);
        const cid = videoInfo.cid;
        console.log(`视频: ${videoInfo.title}`);

        console.log(`正在获取播放链接...`);
        const playData = await getVideoPlayurl(bvid, cid);
        const dashData = playData.dash || {};

        const audios = dashData.audio || [];
        if (audios.length === 0) throw new Error('没有可用的音频流');
        const audio = audios.reduce((max, a) => (a.bandwidth > max.bandwidth ? a : max), audios[0]);
        const audioUrl = audio.baseUrl;
        console.log(`音频流 id=${audio.id} bandwidth=${audio.bandwidth} host=${audioUrl.split('/')[2]}`);

        const audioFilename = `${bvid}_audio.mp4`;
        await downloadFile(audioUrl, audioFilename);
        console.log('\n🎉 音频下载完成!');
    } catch (error) {
        console.error('❌ ' + error.message);
        process.exit(1);
    }
}

main();
