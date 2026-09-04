import urllib.request, json, ssl, os, time

token = os.environ.get('AGNES_API_KEY', '')
if not token:
    print("ERROR: AGNES_API_KEY not set")
    exit(1)

headers = {'Authorization': f'Bearer {token}'}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def gen(prompt, path):
    payload = json.dumps({'prompt': prompt, 'size': '1920x1080', 'quality': 'hd'}).encode()
    req = urllib.request.Request('https://api.agnes-ai.space/v1/images/generations', 
        data=payload, headers={**headers, 'Content-Type': 'application/json'}, method='POST')
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=120)
        result = json.loads(resp.read())
        if result.get('data'):
            img = urllib.request.urlopen(result['data'][0]['url'], context=ctx).read()
            with open(path, 'wb') as f:
                f.write(img)
            return True
    except Exception as e:
        print(f'  Error: {e}')
    return False

os.makedirs('output/characters', exist_ok=True)
os.makedirs('output/keyframes', exist_ok=True)

chars = {
    'linmo': 'Chinese ink wash painting, young swordsman Lin Mo, 20yo, cyan robe, topknot hair, determined eyes, holding ancient black ink sword, martial arts pose, masterpiece, highly detailed, 8K',
    'suwaner': 'Chinese ink wash painting, elegant female swordswoman Su Waner, 18yo, pure white flowing robes, long black hair updo, cold beautiful face, jade sword, fairy-like aura, masterpiece, highly detailed, 8K',
    'xuemojun': 'Chinese ink wash painting, demonic villain Blood Hand Demon Lord, 50yo, black red-accented robes, menacing red face, blood-red broadsword, evil glowing red eyes, dark energy swirling, masterpiece, highly detailed, 8K',
    'old_beggar': 'Chinese ink wash painting, mysterious old beggar, 60yo, tattered brown robes, wine gourd, crazy appearance with wise eyes, under ancient pine tree, zen atmosphere, masterpiece, highly detailed, 8K'
}

scenes = [
    ('scene_01', 'Chinese ink wash painting, ancient Chinese town at dawn, morning mist, bluestone paths, distant green mountains, peaceful traditional architecture, golden light, masterpiece'),
    ('scene_02', 'Chinese ink wash painting, blacksmith workshop, forge fire bright orange sparks flying, young man forging sword, sweat dripping, warm atmospheric lighting, masterpiece'),
    ('scene_03', 'Chinese ink wash painting, ancient black sword emerging from cracked earth, ink patterns flowing on blade surface, mystical purple aura radiating, dramatic spotlight, masterpiece'),
    ('scene_04', 'Chinese ink wash painting, dramatic chase through narrow ancient alleyways, young swordsman running desperately, shadowy figures pursuing on horseback, motion blur, masterpiece'),
    ('scene_05', 'Chinese ink wash painting, beautiful female warrior in white fighting multiple enemies, jade sword rainbow light trails, petals swirling, elegant combat, masterpiece'),
    ('scene_06', 'Chinese ink wash painting, moonlit ancient forest, moonbeams through dense canopy, white-clad woman discovering figure in cave, ethereal blue silver tones, masterpiece'),
    ('scene_07', 'Chinese ink wash painting, Mount Wudang peaks piercing swirling clouds, ancient temple silhouettes, golden sunrise, spiritual ethereal atmosphere, masterpiece'),
    ('scene_08', 'Chinese ink wash painting, weathered old beggar drinking wine under ancient gnarled pine, white beard, wise eyes despite tattered robes, zen atmosphere, masterpiece'),
    ('scene_09', 'Chinese ink wash painting, epic sword duel young swordsman vs old master, massive waves black white ink energy colliding, mountains shifting, breathtaking composition, masterpiece'),
    ('scene_10', 'Chinese ink wash painting, ominous dark red black clouds over Mount Wudang, demonic army marching, Blood Hand Demon Lord on horseback leading charge, terrifying atmosphere, masterpiece'),
    ('scene_11', 'Chinese ink wash painting, massive battle scene dozens martial artists fighting demons, sword beams crisscrossing sky, explosions of energy, epic scale, masterpiece'),
    ('scene_12', 'Chinese ink wash painting, ultimate technique thousand layers black ink energy swirling like tsunami, purple lightning cracking sky, overwhelming power, spectacular visual, masterpiece'),
    ('scene_13', 'Chinese ink wash painting, final duel hero vs demon lord black ink vs red demonic energy, heavens splitting above, intense confrontation, epic composition, masterpiece'),
    ('scene_14', 'Chinese ink wash painting, magical golden seal erupting from ground where sword planted, brilliant light washing battlefield, demons sealed, triumphant awe-inspiring, masterpiece'),
    ('scene_15', 'Chinese ink wash painting, peaceful ancient town restored, golden sunlight through parting clouds, townspeople smiling, birds flying, harmony peace, warm hopeful atmosphere, masterpiece'),
    ('scene_16', 'Chinese ink wash painting, heroes on mountain peak sunset overlooking vast Jianghu, ink scroll unfurling beneath revealing story, epic poetic ending, masterpiece composition')
]

print("Generating characters...")
for cid, prompt in chars.items():
    if gen(prompt, f'output/characters/{cid}.png'):
        print(f'  OK {cid}')
    time.sleep(1)

print("Generating scenes...")
for sid, prompt in scenes:
    if gen(prompt, f'output/keyframes/{sid}.png'):
        print(f'  OK {sid}')
    time.sleep(1)

print(f"\nDone: {len(os.listdir('output/characters'))} chars, {len(os.listdir('output/keyframes'))} scenes")
