import base64, os, random, asyncio
from PIL import Image
from hoshino import Service
from hoshino.typing import CQEvent
from io import BytesIO


sv = Service('随机唐可可', bundle='randomtkk', help_='''
随机唐可可[简单]/[普通]/[困难]/[地狱]/[自定义数量]
'''.strip())
#一些设置
base_path = os.path.join(os.path.dirname(__file__), 'bg.png')  
tkk_path = os.path.join(os.path.dirname(__file__), 'icon/tangkuku.png')   
mark_path = os.path.join(os.path.dirname(__file__), 'icon/mark.png')
icon_path = os.path.join(os.path.dirname(__file__), 'icon/)
ez_num = 10    #简单难度
nr_num = 20    #普通难度
hd_num = 30    #困难难度
ex_num = 40    #地狱难度数量
max_num = 80   #最大数量 超过默认使用ez
waittime = 30  #答案等待时间       
def get_random_position_tkk(num):
    col = random.randint(1, num)
    row = random.randint(1, num)
    return col, row

@sv.on_prefix(('随机唐可可'))                              
async def random_tkk(bot, ev):  
    args = ev.message.extract_plain_text().strip().split()
    if len(args) == 0:
        num = ez_num
    elif args[0] == '简单':
        num = ez_num
    elif args[0] == '普通':
        num = nr_num
    elif args[0] == '困难':
        num = hd_num
    elif args[0] == '地狱':
        num = ex_num
    else:
        try:
            num = int(args[0]) if int(args[0]) <= max_num else ez_num #数量太多运算量过大
            if num < 3:
                num = ez_num #太少没意思
        except:
            num = ez_num
    temp = 0
    col , row = get_random_position_tkk(num)
    base = Image.open(base_path)
    base = base.resize((64 * num, 64 * num), Image.ANTIALIAS)    #加载底图
    tkk = Image.open(tkk_path)
    tkk = tkk.resize((64, 64), Image.ANTIALIAS)      #加载icon
    for r in range(0,num):
        for c in range(0,num):
            if r == row - 1 and c == col - 1:
                base.paste(tkk, (r * 64, c * 64))
                temp += 1
            else:
                icon = Image.open(icon_path + str(random.randint(1, 22)) + '.png')
                icon = icon.resize((64,64), Image.ANTIALIAS)
                base.paste(icon, (r * 64, c * 64))
    buf = BytesIO()
    base.save(buf, format='PNG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    msg = f'''[CQ:image,file={base64_str}]'''
    await bot.send(ev, msg)
    await bot.send(ev, f'将在{waittime}s后公布答案')
    
    await asyncio.sleep(waittime)
    mark = Image.open(mark_path)
    base.paste(mark,((row - 1) * 64, (col - 1) * 64), mark)
    buf = BytesIO()
    base.save(buf, format='PNG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'

    msg = f'''[CQ:image,file={base64_str}]'''
    await bot.send(ev, msg)
