# llmada
一个方便使用各种LLM api的工具


## 常规操作
%cd ~/GitHub/llmada/src

from llmada.core import BianXieAdapter



bx = BianXieAdapter()

async for i in bx.aproduct_stream('详细介绍一下卡拉彼丘 - 空间 不是游戏'):
    print(i)


pytest -s tests/test_1.py