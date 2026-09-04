import cv2, os, json, subprocess, asyncio, edge_tts

os.makedirs('output/scenes', exist_ok=True)
os.makedirs('output/audio', exist_ok=True)

videos = []

print("Creating scene videos...")
for i, f in enumerate(sorted(os.listdir('output/keyframes'))):
    if f.endswith('.png'):
        img = cv2.imread(f'output/keyframes/{f}')
        if img is not None:
            h, w = img.shape[:2]
            out = f'output/scenes/scene_{i+1:02d}.mp4'
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            vw = cv2.VideoWriter(out, fourcc, 24, (1920, 1080))
            for j in range(24*60):
                t = j / (24*60)
                ease = t*t*(3-2*t)
                zoom = 1.0 + 0.12*ease
                nw = int(w/zoom); nh = int(h/zoom)
                x1 = max(0, int((w-nw)/2)+int(5*ease))
                y1 = max(0, int((h-nh)/2)-int(8*ease))
                vw.write(cv2.resize(img[y1:y1+nh,x1:x1+nw], (1920,1080), interpolation=cv2.INTER_LANCZOS4))
            vw.release()
            videos.append(out)
            print(f'  OK scene_{i+1:02d}')

dialogs = [
    ('linmo', 'zh-CN-YunxiNeural', '这把剑还没打好，师父说剑要有魂，魂在气中。'),
    ('voice', 'zh-CN-YunyangNeural', '墨影剑认主，凡人，你可愿承担它的命运？'),
    ('xuemojun', 'zh-CN-YunhaoNeural', '墨影剑终于出现了，小娃娃把剑交出来饶你不死。'),
    ('suwaner', 'zh-CN-XiaoyiNeural', '你们这些邪魔外道竟敢追杀无辜之人今日便让你见识见识武当剑法。'),
    ('suwaner', 'zh-CN-XiaoyiNeural', '你是什么人为何持有墨影剑'),
    ('linmo', 'zh-CN-YunxiNeural', '我也不知道它就自己出现在我手里的。'),
    ('old_beggar', 'zh-CN-YunyangNeural', '小子你手里那把剑可是烫手山芋啊继续逃避还是站出来。'),
    ('linmo', 'zh-CN-YunxiNeural', '我明白了墨影不是用来控制的是用来守护的。'),
    ('linmo', 'zh-CN-YunxiNeural', '我不是要赢你我是要终结这一切。'),
    ('linmo', 'zh-CN-YunxiNeural', '我只是做了该做的接下来我们继续守护这片江湖。'),
]

print("Creating dialog videos...")
for i, (char, voice, text) in enumerate(dialogs):
    audio = f'output/audio/dlg_{i+1:02d}.mp3'
    video = f'output/scenes/dialog_{i+1:02d}.mp4'
    
    if not os.path.exists(audio):
        asyncio.run(edge_tts.Communicate(text, voice).save(audio))
        print(f'  OK audio {i+1}')
    
    dur = 5.0
    try:
        r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','json',audio], capture_output=True, text=True)
        dur = float(json.loads(r.stdout)['format']['duration'])
    except: pass
    
    char_img = f'output/characters/{char}.png' if char != 'voice' else 'output/characters/linmo.png'
    if os.path.exists(char_img) and not os.path.exists(video):
        img = cv2.imread(char_img)
        if img is not None:
            h, w = img.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            vw = cv2.VideoWriter(video, fourcc, 24, (1920, 1080))
            for j in range(int(24*dur)):
                t = j/(24*dur)
                ease = t*t*(3-2*t)
                zoom = 1.0 + 0.12*ease
                nw = int(w/zoom); nh = int(h/zoom)
                x1 = max(0, int((w-nw)/2)+int(5*ease))
                y1 = max(0, int((h-nh)/2)-int(8*ease))
                vw.write(cv2.resize(img[y1:y1+nh,x1:x1+nw], (1920,1080), interpolation=cv2.INTER_LANCZOS4))
            vw.release()
            
            final = video.replace('.mp4', '_f.mp4')
            subprocess.run(['ffmpeg','-y','-i',video,'-i',audio,'-c:v','copy','-c:a','aac','-shortest',final], capture_output=True)
            if os.path.exists(final):
                os.replace(final, video)
                videos.append(video)
                print(f'  OK dialog_{i+1}')

with open('output/videos.json', 'w') as f:
    json.dump({'videos': videos}, f)
print(f"\nTotal: {len(videos)} videos")
