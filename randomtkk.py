import base64, os, random, asyncio
from PIL import Image, ImageFont, ImageDraw
from hoshino import Service
from hoshino.typing import CQEvent
from io import BytesIO

#回复帮助的语句我没写 如果需要你可以手动加一下（）
sv = Service('随机唐可可', bundle='randomtkk', help_='''
随机唐可可[简单]/[普通]/[困难]/[地狱]/[自定义数量]
答案格式是 [答案是][列][空格][行] 例如：答案是114 514 or 答案是 114 514
'''.strip())
#一些设置
font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'icon/msyh.ttc'),16) 
tkk_path = os.path.join(os.path.dirname(__file__), 'icon/tangkuku.png')   
mark_path = os.path.join(os.path.dirname(__file__), 'icon/mark.png')
icon_path = os.path.join(os.path.dirname(__file__), 'icon/')
ez_num = 10    #简单难度
nr_num = 20    #普通难度
hd_num = 30    #困难难度
ex_num = 40    #地狱难度数量
max_num = 80   #最大数量 超过默认使用ez
waittime = 30  #num = 15时答案等待时间 最终等待时间公式为 waittime = int(waittime * min(2, (num / 15)))
coor_switch = True #坐标显示开关
guess_flag = [] #记忆群内是否猜出答案 是则为{'群号':1}，在为1时不会响应回答语句
now_playing = [] #防止多局游戏 在为1时不会相应创建游戏指令
daan = [] #记忆每个群的答案 答案格式为str([列][空格][横])（我也不知道为啥反了，懒得改了） 在一个群没有答案的时候会被置为'error'

def get_random_position_tkk(num):
    col = random.randint(1, num)
    row = random.randint(1, num)
    return col, row

def set_daan(gid, da):
    global daan
    for i in daan: 
        if str(gid) in i.keys():
            i[str(gid)] = da
            return
    else:
        daan.append({str(gid):da})
        return

def cheak_daan(gid, da):
    for i in daan:
        if str(gid) in i.keys():
            if i[str(gid)] == da:
                return 1
            else:
                return 0
    else:
        daan.append({str(gid):"error"}) #主要防止没有添加答案就来查答案导致报错
        return 0


def close_game(gid):
    print("now close")
    global now_playing #在now_playing中一定有这个gid
    for i in now_playing: #结束游戏
        if str(gid) in i.keys():
            i[str(gid)] = 0
            break
    global guess_flag
    for i in guess_flag: 
        if str(gid) in i.keys(): #游戏关闭时直接设置已猜出
            i[str(gid)] = 1
            return
    else:
        guess_flag.append({str(gid):1})
        return
        
def reset_flag(gid):
    global guess_flag
    for i in guess_flag:
        if str(gid) in i.keys():
            i[str(gid)] = 0
            return
    else:
        guess_flag.append({str(gid):0})
        return

def cheak_guess_flag(gid):  
    global guess_flag
    for i in guess_flag: 
        if str(gid) in i.keys():
            if i[str(gid)] == 1:
                return 1
            else:
                return 0
    else:
        return 0

def cheak_now_palying(gid): #检查时顺便设置正在游戏
    global now_playing
    for i in now_playing:
        if str(gid) in i.keys():
            if i[str(gid)] == 1:
                return 1
            else:
                i[str(gid)] = 1
                reset_flag(gid)
                return 0
    else:
        now_playing.append({str(gid):1})
        return 0

@sv.on_prefix(('随机唐可可'))                              
async def random_tkk(bot, ev):  
    gid = ev["group_id"]
    if cheak_now_palying(gid):
        return
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
    _waittime = int(waittime * min(2, (num / 15)))
    col , row = get_random_position_tkk(num)
    da = f'{row} {col}'
    set_daan(gid, da) #设置群答案
    base = Image.new("RGB",(64 * num, 64 * num))
    for r in range(0,num):
        for c in range(0,num):
            if r == row - 1 and c == col - 1:
                tkk = Image.open(tkk_path)
                tkk = tkk.resize((64, 64), Image.ANTIALIAS)      #加载icon
                if coor_switch:
                    draw = ImageDraw.Draw(tkk)
                    draw.text((20,40),f"({r+1},{c+1})",font=font,fill=(255, 0, 0, 0))
                base.paste(tkk, (r * 64, c * 64))
                temp += 1
            else:
                icon = Image.open(icon_path + str(random.randint(1, 22)) + '.png')
                icon = icon.resize((64,64), Image.ANTIALIAS)
                if coor_switch:
                    draw = ImageDraw.Draw(icon)
                    draw.text((20,40),f"({r+1},{c+1})",font=font,fill=(255, 0, 0, 0))
                base.paste(icon, (r * 64, c * 64))
    buf = BytesIO()
    base.save(buf, format='PNG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    msg = f'''[CQ:image,file={base64_str}]'''
    await bot.send(ev, msg)
    await bot.send(ev, f'将在{_waittime}s后公布答案')
    
    await asyncio.sleep(_waittime)
    if cheak_guess_flag(gid): #有人猜出，无需公布答案
        return
    mark = Image.open(mark_path)
    base.paste(mark,((row - 1) * 64, (col - 1) * 64), mark)
    buf = BytesIO()
    base.save(buf, format='PNG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'

    msg = f'''没人猜出啦，好可惜啊[CQ:image,file={base64_str}]'''
    close_game(gid)
    await bot.send(ev, msg)
    
@sv.on_prefix(('答案是'))  #答案格式是 [答案是][列][空格][行] 例如：答案是114 514 or 答案是 114 514 你也可以手动换下row和col的值来先说行再说列 
async def huida(bot, ev):
    gid = ev["group_id"]
    if cheak_guess_flag(gid): #先要没人猜出来过
        return
    args = ev.message.extract_plain_text().strip().split()
    if len(args) == 2:
        try:
            row = int(args[0])
            col = int(args[1])
            da = f'{row} {col}'
        except:
            return
        if cheak_daan(gid, da):
            close_game(gid)
            await bot.send(ev, "好厉害!", at_sender = True)
        else:
            return
    else:
        return
