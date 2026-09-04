import subprocess, os, json

with open('output/videos.json') as f:
    videos = json.load(f)['videos']

print(f'Synthesizing {len(videos)} videos...')

with open('output/list.txt', 'w') as f:
    for v in videos:
        f.write(f"file '{v}'\n")

r = subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i','output/list.txt','-c','copy','-movflags','+faststart','ink-shadow-sword-complete.mp4'],
    capture_output=True, text=True, timeout=600)

if os.path.exists('ink-shadow-sword-complete.mp4'):
    size = os.path.getsize('ink-shadow-sword-complete.mp4') / (1024*1024)
    print(f'SUCCESS: ink-shadow-sword-complete.mp4 ({size:.1f} MB)')
else:
    print(f'FAILED: {r.stderr[:200]}')
    exit(1)
