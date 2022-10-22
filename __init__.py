import base64
import io
from typing import List
from services.log import logger
from PIL import Image
from nonebot import on_command
from utils.depends import ImageList, GetConfig, PlaintText
from .data_source import get_result
from utils.http_utils import AsyncHttpx
from utils.message_builder import image as image
import ujson as json
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
)

__zx_plugin_name__ = "清晰术"
__plugin_usage__ = """
usage：
    清晰术[双/三四]重吟唱 [强力/中等/弱/不变/原]术式 [图片]
""".strip()
__plugin_des__ = "清晰术（又名图片超分术"
__plugin_cmd__ = ["清晰术[双/三四]重吟唱 [强力/中等/弱/不变/原]术式"]
__plugin_version__ = 0.1
__plugin_author__ = "hoshino 清晰术（hibikier改"
__plugin_settings__ = {
    "level": 5,
    "cmd": ["清晰术"],
}
__plugin_cd_limit__ = {}
__plugin_configs__ = {
    "API": {
        "value": None,
        "help": "参考 https://www.yuque.com/docs/share/bc837020-0261-4891-8da6-79979ece68c2#cf786ac0",
    },
}

thumbSize = (768, 768)

matcher = on_command("清晰术", priority=5, block=True)


@matcher.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
    text: str = PlaintText(),
    img_list: List[str] = ImageList("你没有需要清晰术的图片！"),
    api: str = GetConfig(config="API"),
):
    try:
        img = img_list[0]
        image_ = Image.open(io.BytesIO((await AsyncHttpx.get(img, timeout=20)).content))
        image_ = image_.convert("RGB")
        ix = image_.size[0]
        iy = image_.size[1]
        image_.thumbnail(thumbSize, resample=Image.ANTIALIAS)
        image_data = io.BytesIO()
        image_.save(image_data, format="JPEG")
        img = image_data.getvalue()
        i_b64 = "data:image/jpeg;base64," + base64.b64encode(img).decode()
        scale = 2
        con = "conservative"
        if "双重吟唱" in text:
            scale = 2
        elif "三重吟唱" in text and ix * iy < 400000:
            scale = 3
        elif "四重吟唱" in text and ix * iy < 400000:
            scale = 4
        if "强力术式" in text:
            con = "denoise3x"
        elif "中等术式" in text:
            con = "no-denoise"
            if scale == 2:
                con = "denoise2x"
        elif "弱术术式" in text:
            con = "no-denoise"
            if scale == 2:
                con = "denoise1x"
        elif "不变术式" in text:
            con = "no-denoise"
        elif "原术式" in text:
            con = "conservative"
        model_name = f"up{scale}x-latest-{con}.pth"
        await matcher.send(
            f"鸣大钟一次，推动杠杆，启动活塞和泵；鸣大钟两次，按下按钮，"
            f"发动机点火，点燃涡轮，注入生命；鸣大钟三次，齐声歌唱，赞美万机之神！大清晰术{con}{scale}重唱！",
            at_sender=True,
        )
        json_ = {"data": [i_b64, model_name, 2]}
        if result := await get_result(json_, api=api):  # 然后进行超分辨率重建
            a = json.loads(result)
            a = "base64://" + a["data"][0].split("base64,")[1]
            await matcher.send(f"{scale}重唱{con}分支大清晰术！" + image(b64=a), at_sender=True)
        else:
            await matcher.finish("清晰术失败", at_sender=True)
    except Exception as e:
        logger.error(f"超分发生错误 {type(e)}：{e}")
        await matcher.finish("清晰术失败", at_sender=True)
