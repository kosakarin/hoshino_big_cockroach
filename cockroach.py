import base64, os, random
from PIL import Image
from hoshino import Service
from hoshino.typing import CQEvent
from io import BytesIO

sv = Service('飞天大蟑螂', bundle='cockroach', help_='''
随机生成大量大蟑螂图片
'''.strip())

base_path = './hoshino/modules/bigzhanglang/bg.png'
cockroach_path = './hoshino/modules/bigzhanglang/cockroach_1.png'     

def get_random_position(i, num):
    if random.randint(1, 2) == 1:
        row = 540 - random.randint(1, min(500, i * (500 // num) + 250))
        
    else:
        row = 540 + random.randint(1, min(500, i * (500 // num) + 250))
        
    if random.randint(1, 2) == 1:
        col = 540 - random.randint(1, min(500, i * (500 // num) + 250))
    else:
        col = 540 + random.randint(1, min(500, i * (500 // num) + 250))
    return row, col

@sv.on_prefix(('飞天大蟑螂'))  #后面跟数字可以指定最多多少只                              
async def random_cockroach(bot, ev):  
    args = ev.message.extract_plain_text().strip().split()
    if len(args) == 0:
        num = random.randint(1, 100)
    else:
        try:
            num = random.randint(1, int(args[0])) if int(args[0]) < 114514 else random.randint(1, 100)
        except:
            num = random.randint(1, 100)

    base = Image.open(base_path)
    base = base.resize((1080, 1080), Image.ANTIALIAS)    #加载底图
    f = Image.open(cockroach_path)
    f = f.resize((160, 160), Image.ANTIALIAS)      #加载icon
    for i in range(0,num):
        f = f.rotate(random.randint(1, 12) * 30) 
        row, col = get_random_position(i, num)
        base.paste(f, (row, col), f) 

    buf = BytesIO()
    base.save(buf, format='PNG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    msg = f'''[CQ:image,file={base64_str}]'''
    await bot.send(ev, msg)
