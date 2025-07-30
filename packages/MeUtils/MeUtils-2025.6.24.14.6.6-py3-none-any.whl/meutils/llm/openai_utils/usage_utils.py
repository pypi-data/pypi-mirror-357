#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : usage_utils
# @Time         : 2025/6/24 08:53
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
"""
1. 同步任务（流 非流）
    - 按次
    - 按量
2. 异步任务
    - 按次
    - 按量
"""

from meutils.pipe import *
from meutils.llm.clients import AsyncOpenAI
from meutils.apis.utils import make_request

base_url = "https://api.chatfire.cn"


async def create_usage_for_async_task(model: str = "usage-async"):
    # 计费
    _ = await make_request(
        base_url=base_url,
        path=f"/flux/v1/{model}",
        payload={
            "id": "123456",
            "completion_tokens": 100,
            "total_tokens": 200
        }
        # "/flux/v1/get_result",
    )

    return _


async def get_async_task(id: str = "123456", status: str = "FAILURE"):
    # 计费
    _ = await make_request(
        base_url=base_url,
        path=f"/flux/v1/get_result?id={id}&status={status}",

        method="GET"
    )

    return _


async def create_usage_for_tokens(model: str = "usage-chat", mode: Literal['chat', 'image'] = 'chat'):
    client = AsyncOpenAI()  # 外部任务
    if mode == "image":  # todo: 参数进不去 要不通过 prompt
        _ = await client.images.generate(
            model=model,
            prompt="ChatfireAPI",
            n=10,
            size="1024x1024",
            extra_body={
                "extra_fields": {
                    "input_tokens": 1,
                    "input_tokens_details": {
                        "image_tokens": 0,
                        "text_tokens": 1
                    },
                    "output_tokens": 1,
                    "total_tokens": 2
                }
            }
        )
    else:
        _ = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "ChatfireAPI"}
            ],
            metadata={
                "prompt_tokens": 100,
                "completion_tokens": 100,
                "total_tokens": 200
            }
        )
    return _


if __name__ == '__main__':
    # arun(create_usage_for_tokens())
    arun(create_usage_for_tokens(mode='image'))

    # arun(create_usage_for_async_task())

    # arun(get_async_task('xx'))
