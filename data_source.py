from typing import Optional
from services.log import logger
import aiohttp


async def get_result(json_data: dict, *, api: str) -> Optional[str]:
    """
    来构造请求并获取返回的重建后的图像

    Args:
        json_data (dict): 对图片编码后的数据
        api: api
    Returns:
        str: 返回的json格式数据
    """
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json",
        "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": "session-space-cookie=ae33b52c9c088416db57b4cb0201d953",
        "Referer": api,
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api, headers=headers, json=json_data, timeout=360
            ) as resp:
                return await resp.text()
    except Exception as e:
        logger.info(f"超分发生了错误 {type(e)}：{e}")
    return None
