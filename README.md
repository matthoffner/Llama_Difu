# Llama_difu

Prototype to chat, search and upload documents in one place to demonstrate `llama-index`, `llama.cpp`, `langchain`

Modified example of https://github.com/MZhao-ouo/Llama_difu using no Open API keys and a local llama.

[![LICENSE](https://img.shields.io/github/license/MZhao-ouo/Llama_difu)](https://github.com/MZhao-ouo/Llama_difu/blob/main/LICENSE)
[![Web-UI](https://img.shields.io/badge/WebUI-Gradio-fb7d1a?style=flat)](https://gradio.app/)
[![base](https://img.shields.io/badge/Base-Llama_index-cdc4d6?style=flat&logo=github)](https://github.com/jerryjliu/gpt_index)

---

为 [Llama_index](https://github.com/jerryjliu/gpt_index) (gpt_index)做了个便于使用的图形界面。可以让ChatGPT访问自定义的内容，甚至是数据库！

![演示视频](https://user-images.githubusercontent.com/70903329/225239555-a29fa01b-e7ba-4041-bbce-187ac3f7d333.gif)


```bash
pip install -r requirements.txt
```

```bash
python main.py --model "ggml-model.bin"
```