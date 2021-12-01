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

game_info = {} #用于记录当前游戏状态，'now_playing'为是否正在游戏中，1为正在游戏，0为并未游戏
               #'daan'用于记录当前游戏的答案，记录格式为str('[列][空格][行]')，无答案时会被记录为error
               #'guess_flag'用于记录是否有人猜出答案，是为1，否为0，为1时触发'答案是'语句后会直接return，不做处理

def get_random_position_tkk(num):
    col = random.randint(1, num)
    row = random.randint(1, num)
    return col, row

def set_daan(gid, da):
    global game_info #设置答案时该gid一定存在，不需要不存在处理，不需要返回
    game_info[gid]['daan'] = da

def cheak_daan(gid, da):
    global game_info
    if gid not in game_info: #一时半会想不清楚会不会存在检查答案时该群不存在这种情况，反正先处理下
        game_info[gid] = {}
        game_info[gid]['now_playing'] = 0
        game_info[gid]['daan'] = 'error'
        game_info[gid]['guess_flag'] = 1
        return 0 #不存在该群，答案肯定不正确
    elif game_info[gid]['daan'] == da: #回答正确
        return 1 
    else:
        return 0 #回答错误

def close_game(gid):
    global game_info #关闭游戏时该gid一定存在，不需要不存在处理，不需要返回
    game_info[gid]['now_playing'] = 0
    game_info[gid]['guess_flag'] = 1
        
def cheak_guess_flag(gid):  
    global game_info
    if gid not in game_info: #没有这个gid说明是意外触发
        game_info[gid] = {}
        game_info[gid]['now_playing'] = 0
        game_info[gid]['daan'] = 'error'
        game_info[gid]['guess_flag'] = 1  #置1直接跳过回复程序防止报错
        return 1
    else: #else说明gid存在，直接返回对应值即可
        return game_info[gid]['guess_flag']

def cheak_now_palying(gid): #检查时顺便设置正在游戏
    global game_info
    if gid not in game_info:
        game_info[gid] = {}
        game_info[gid]['now_playing'] = 1
        game_info[gid]['daan'] = 'error'
        game_info[gid]['guess_flag'] = 0
        return 0 #设置为正在游戏中了但是实际并未开始游戏，返回0
    elif game_info[gid]['now_playing'] == 0:
        game_info[gid]['now_playing'] = 1
        game_info[gid]['guess_flag'] = 0 #开始游戏同时重置标志
        return 0 #同理
    else: #到这个else说明gid存在且已在游戏中，其实可以直接return 1
        return game_info[gid]['now_playing']

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
