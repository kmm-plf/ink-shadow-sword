"""
墨影剑魂 - 完整电影生成脚本
在GitHub Codespace中运行，利用GPU生成高质量动画
"""
import os, json, subprocess, time, asyncio
import urllib.request
import ssl
import edge_tts

PROJECT_ROOT = "/workspaces/ink-shadow-sword"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
VIDEOS_DIR = os.path.join(OUTPUT_DIR, "scenes")
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
CHARACTERS_DIR = os.path.join(OUTPUT_DIR, "characters")
KEYFRAMES_DIR = os.path.join(OUTPUT_DIR, "keyframes")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(CHARACTERS_DIR, exist_ok=True)
os.makedirs(KEYFRAMES_DIR, exist_ok=True)

# Agnes Image API配置
AGNES_API_KEY = "agn-41788e52f6ea4f9cb82b1e63bb47e9e3"
AGNES_BASE_URL = "https://api.agnes-ai.space/v1"

# 角色定义
CHARACTERS = {
    "linmo": {
        "name": "林墨",
        "prompt": "Chinese ink wash painting style, young swordsman Lin Mo, 20 years old, wearing cyan traditional Chinese robe, hair tied in topknot, determined eyes, holding ancient black sword with ink-like patterns flowing on blade, martial arts pose, dynamic composition, traditional Chinese art meets anime aesthetic, highly detailed, masterpiece",
        "voice": "zh-CN-YunxiNeural"
    },
    "suwaner": {
        "name": "苏婉儿", 
        "prompt": "Chinese ink wash painting style, elegant female swordswoman Su Waner, 18 years old, wearing pure white flowing robes, long black hair in elegant updo, cold beautiful face, holding slender jade sword, fairy-like aura, standing on mountain peak with clouds, wuxia fantasy, highly detailed, masterpiece",
        "voice": "zh-CN-XiaoyiNeural"
    },
    "xuemojun": {
        "name": "血手魔君",
        "prompt": "Chinese ink wash painting style, demonic villain Blood Hand Demon Lord, 50 years old, wearing black dark robes with red accents, menacing red face with sharp features, holding blood-red broadsword, evil glowing red eyes, dark energy swirling around, wuxia horror, highly detailed, masterpiece",
        "voice": "zh-CN-YunhaoNeural"
    },
    "old_beggar": {
        "name": "老乞丐",
        "prompt": "Chinese ink wash painting style, mysterious old beggar, 60 years old, wearing tattered brown robes, holding wine gourd, appearing crazy but with hidden wisdom in eyes, sitting under ancient pine tree, zen atmosphere, traditional Chinese painting style, highly detailed, masterpiece",
        "voice": "zh-CN-YunyangNeural"
    }
}

# 场景定义
SCENES = [
    {"name": "小镇清晨", "prompt": "Chinese ink wash painting style, quiet ancient Chinese town at dawn, morning mist, bluestone paths, distant green mountains, peaceful atmosphere, traditional Chinese architecture, highly detailed", "duration": 60},
    {"name": "铁匠铺", "prompt": "Chinese ink wash painting style, blacksmith workshop interior, forge fire burning bright, sparks flying, young man forging sword, sweat dripping, warm lighting, traditional Chinese workshop, highly detailed", "duration": 45},
    {"name": "墨影剑出世", "prompt": "Chinese ink wash painting style, ancient black sword emerging from ground, ink-like patterns flowing on blade surface, mystical energy, dark purple aura, dramatic lighting, highly detailed", "duration": 30},
    {"name": "追逐战", "prompt": "Chinese ink wash painting style, dramatic chase scene, young swordsman running through narrow alleys, dark figures pursuing, dynamic motion blur, tension, highly detailed", "duration": 60},
    {"name": "苏婉儿战斗", "prompt": "Chinese ink wash painting style, beautiful female warrior in white fighting multiple enemies, sword light like rainbow, petals floating, elegant combat, highly detailed", "duration": 60},
    {"name": "密林相遇", "prompt": "Chinese ink wash painting style, moonlit forest, white-clad woman discovering hidden figure in cave, moonbeams through leaves, mysterious atmosphere, highly detailed", "duration": 45},
    {"name": "武当山", "prompt": "Chinese ink wash painting style, Mount Wudang, clouds swirling around ancient temple, ethereal atmosphere, spiritual energy, traditional Chinese landscape painting, highly detailed", "duration": 60},
    {"name": "老乞丐现身", "prompt": "Chinese ink wash painting style, mysterious old beggar drinking wine under ancient tree, appearing sloppy but with wise eyes, zen atmosphere, traditional Chinese painting, highly detailed", "duration": 45},
    {"name": "剑圣对决", "prompt": "Chinese ink wash painting style, epic sword duel between young swordsman and old master, ink energy waves colliding, mountains shifting, dramatic composition, highly detailed", "duration": 60},
    {"name": "血手魔君来袭", "prompt": "Chinese ink wash painting style, dark clouds gathering over Mount Wudang, demonic army approaching, red sky, terrifying atmosphere, highly detailed", "duration": 45},
    {"name": "大规模战斗", "prompt": "Chinese ink wash painting style, massive battle scene, multiple martial artists fighting demons, sword beams everywhere, epic composition, highly detailed", "duration": 60},
    {"name": "墨影千重", "prompt": "Chinese ink wash painting style, spectacular special move, thousand layers of black ink energy swirling, overwhelming power, epic scale, highly detailed", "duration": 45},
    {"name": "最终对决", "prompt": "Chinese ink wash painting style, final duel between hero and demon lord, black and red energy clashing, heavens splitting, epic confrontation, highly detailed", "duration": 60},
    {"name": "封印完成", "prompt": "Chinese ink wash painting style, magical seal activated, golden light exploding from ground, demons being sealed, triumphant moment, highly detailed", "duration": 45},
    {"name": "和平重现", "prompt": "Chinese ink wash painting style, peaceful ancient Chinese town restored, sunlight breaking through clouds, people smiling, harmony restored, highly detailed", "duration": 45},
    {"name": "结局", "prompt": "Chinese ink wash painting style, young heroes standing on mountain peak overlooking Jianghu, ink scroll unfurling, epic ending, highly detailed", "duration": 60},
]

# 对话定义
DIALOGUES = [
    {"char": "linmo", "text": "这把剑还没打好，师父说剑要有魂，魂在气中。", "voice": "zh-CN-YunxiNeural"},
    {"char": "voice", "text": "墨影剑认主，凡人，你可愿承担它的命运？", "voice": "zh-CN-YunyangNeural"},
    {"char": "xuemojun", "text": "墨影剑终于出现了，小娃娃把剑交出来饶你不死。", "voice": "zh-CN-YunhaoNeural"},
    {"char": "suwaner", "text": "你们这些邪魔外道竟敢追杀无辜之人今日便让你见识见识武当剑法。", "voice": "zh-CN-XiaoyiNeural"},
    {"char": "suwaner", "text": "你是什么人为何持有墨影剑", "voice": "zh-CN-XiaoyiNeural"},
    {"char": "linmo", "text": "我也不知道它就自己出现在我手里的。", "voice": "zh-CN-YunxiNeural"},
    {"char": "old_beggar", "text": "小子你手里那把剑可是烫手山芋啊继续逃避还是站出来。", "voice": "zh-CN-YunyangNeural"},
    {"char": "linmo", "text": "我明白了墨影不是用来控制的是用来守护的。", "voice": "zh-CN-YunxiNeural"},
    {"char": "linmo", "text": "我不是要赢你我是要终结这一切。", "voice": "zh-CN-YunxiNeural"},
    {"char": "linmo", "text": "我只是做了该做的接下来我们继续守护这片江湖。", "voice": "zh-CN-YunxiNeural"},
]

def call_agnes_api(prompt, output_path):
    """调用Agnes AI图片生成API"""
    payload = json.dumps({
        "prompt": prompt,
        "size": "1920x1080",
        "quality": "hd",
        "style": "china_ink"
    }).encode()
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(
        f"{AGNES_BASE_URL}/images/generations",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AGNES_API_KEY}"
        },
        method="POST"
    )
    
    resp = urllib.request.urlopen(req, context=ctx, timeout=120)
    result = json.loads(resp.read())
    
    if "data" in result and len(result["data"]) > 0:
        img_url = result["data"][0]["url"]
        img_data = urllib.request.urlopen(img_url, context=ctx).read()
        with open(output_path, "wb") as f:
            f.write(img_data)
        return True
    return False

def generate_audio(text, output_path, voice):
    """生成TTS音频"""
    communicate = edge_tts.Communicate(text, voice)
    asyncio.run(communicate.save(output_path))

def get_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "json", path], capture_output=True, text=True)
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except:
        return 5.0

def image_to_video(img_path, output_path, duration):
    """使用OpenCV将图片转为视频(Ken Burns效果)"""
    import cv2
    import numpy as np
    
    img = cv2.imread(img_path)
    if img is None:
        return False
    
    h, w = img.shape[:2]
    total_frames = int(24 * duration)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 24, (1920, 1080))
    
    for i in range(total_frames):
        t = i / total_frames
        ease = t * t * (3 - 2 * t)
        zoom = 1.0 + 0.12 * ease
        new_w = int(w / zoom)
        new_h = int(h / zoom)
        x1 = max(0, int((w - new_w) / 2) + int(5 * ease))
        y1 = max(0, int((h - new_h) / 2) - int(8 * ease))
        cropped = img[y1:y1+new_h, x1:x1+new_w]
        resized = cv2.resize(cropped, (1920, 1080), interpolation=cv2.INTER_LANCZOS4)
        out.write(resized)
    
    out.release()
    return os.path.exists(output_path) and os.path.getsize(output_path) > 100000

def main():
    print("=== 墨影剑魂 - 电影生成 ===
")
    
    all_videos = []
    
    # 1. 生成角色图片
    print("🎭 生成角色图片...")
    for char_id, char_info in CHARACTERS.items():
        output_path = os.path.join(CHARACTERS_DIR, f"{char_id}.png")
        if not os.path.exists(output_path):
            if call_agnes_api(char_info["prompt"], output_path):
                print(f"  ✓ {char_info['name']}")
            else:
                print(f"  ✗ {char_info['name']}")
    
    # 2. 生成场景图片
    print("\n🖼️ 生成场景图片...")
    for i, scene in enumerate(SCENES):
        output_path = os.path.join(KEYFRAMES_DIR, f"scene_{i+1:02d}_{scene["name"]}.png")
        if not os.path.exists(output_path):
            if call_agnes_api(scene["prompt"], output_path):
                print(f"  ✓ {scene["name"]}")
            else:
                print(f"  ✗ {scene["name"]}")
        time.sleep(1)  # 避免API限流
    
    # 3. 生成场景视频
    print("\n🎬 生成场景视频...")
    for i, scene in enumerate(SCENES):
        img_path = os.path.join(KEYFRAMES_DIR, f"scene_{i+1:02d}_{scene["name"]}.png")
        output_path = os.path.join(VIDEOS_DIR, f"scene_{i+1:02d}.mp4")
        if os.path.exists(img_path) and not os.path.exists(output_path):
            if image_to_video(img_path, output_path, scene["duration"]):
                all_videos.append(output_path)
                print(f"  ✓ {scene["name"]} ({scene["duration"]}s)")
    
    # 4. 生成对话音频和视频
    print("\n🎤 生成对话片段...")
    for i, dlg in enumerate(DIALOGUES):
        char_img = os.path.join(CHARACTERS_DIR, f"{dlg['char']}.png")
        if dlg['char'] == 'voice':
            char_img = os.path.join(CHARACTERS_DIR, "linmo.png")
        output_path = os.path.join(VIDEOS_DIR, f"dialog_{i+1:02d}.mp4")
        audio_path = os.path.join(AUDIO_DIR, f"dlg_{i+1:02d}.mp3")
        
        if os.path.exists(char_img) and not os.path.exists(audio_path):
            try:
                generate_audio(dlg["text"], audio_path, dlg["voice"])
                dur = get_duration(audio_path)
                if image_to_video(char_img, output_path, dur):
                    all_videos.append(output_path)
                    print(f"  ✓ dialog {i+1:02d} ({dur:.0f}s)")
            except Exception as e:
                print(f"  ✗ dialog {i+1:02d}: {e}")
    
    # 5. 合成最终电影
    print("\n🎞️ 合成最终电影...")
    final_output = os.path.join(OUTPUT_DIR, "ink-shadow-sword-complete.mp4")
    
    if all_videos:
        list_file = os.path.join(OUTPUT_DIR, "concat_list.txt")
        with open(list_file, "w") as f:
            for v in all_videos:
                f.write(f"file \'{v}\'\n")
        
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
               "-c", "copy", "-movflags", "+faststart", final_output]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if r.returncode == 0 and os.path.exists(final_output):
            size_mb = os.path.getsize(final_output) / (1024*1024)
            dur = get_duration(final_output)
            print(f"\n{'='*50}")
            print(f"✅ 电影生成完成!")
            print(f"📁 {final_output}")
            print(f"💾 {size_mb:.1f} MB")
            print(f"⏱️  {dur:.0f}秒 ({dur/60:.1f}分钟)")
            print(f"🎞️  {len(all_videos)} 个片段")
            print(f"{'='*50}")
            
            # 复制到根目录
            subprocess.run(["cp", final_output, os.path.join(PROJECT_ROOT, "ink-shadow-sword-complete.mp4")])
        else:
            print(f"❌ 合成失败: {r.stderr[:200]}")
    else:
        print("❌ 没有可合成的视频")

if __name__ == "__main__":
    main()
