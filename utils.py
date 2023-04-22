import os
import gradio as gr
from zipfile import ZipFile
from presets import *

def save_index(index, index_name, exist_ok=False):
    file_path = f"./index/{index_name}.json"

    if not os.path.exists(file_path) or exist_ok:
        index.save_to_disk(file_path)
        print(f'Saved file "{file_path}".')
    else:
        i = 1
        while True:
            new_file_path = f'{os.path.splitext(file_path)[0]}_{i}{os.path.splitext(file_path)[1]}'
            if not os.path.exists(new_file_path):
                index.save_to_disk(new_file_path)
                print(f'Saved file "{new_file_path}".')
                break
            i += 1

def refresh_json_list(plain=False):
    json_list = []
    for root, dirs, files in os.walk("./index"):
        for file in files:
            if os.path.splitext(file)[1] == '.json':
                json_list.append(os.path.splitext(file)[0])
    if plain:
        return json_list
    return gr.Dropdown.update(choices=json_list)

def upload_file(file_obj):
    files = []
    with ZipFile(file_obj.name) as zfile:
        for zinfo in zfile.infolist():
            files.append(
                {
                    "name": zinfo.filename,
                }
            )
    return files

def reset_textbox():
    return gr.update(value='')

def change_prompt_tmpl(tmpl_select):
    new_tmpl = prompt_tmpl_dict[tmpl_select]
    return gr.update(value=new_tmpl)

def change_refine_tmpl(refine_select):
    new_tmpl = refine_tmpl_dict[refine_select]
    return gr.update(value=new_tmpl)

def lock_params(index_type):
    if index_type == "GPTSimpleVectorIndex" or index_type == "GPTListIndex":
        return gr.Slider.update(interactive=False, label="子节点数量（当前索引类型不可用）"), gr.Slider.update(interactive=False, label="每段关键词数量（当前索引类型不可用）")
    elif index_type == "GPTTreeIndex":
        return gr.Slider.update(interactive=True, label="子节点数量"), gr.Slider.update(interactive=False, label="每段关键词数量（当前索引类型不可用）")
    elif index_type == "GPTKeywordTableIndex":
        return gr.Slider.update(interactive=False, label="子节点数量（当前索引类型不可用）"), gr.Slider.update(interactive=True, label="每段关键词数量")

def add_space(text):
    punctuations = {'，': '， ', '。': '。 ', '？': '？ ', '！': '！ ', '：': '： ', '；': '； '}
    for cn_punc, en_punc in punctuations.items():
        text = text.replace(cn_punc, en_punc)
    return text

def parse_text(text):
    lines = text.split("\n")
    lines = [line for line in lines if line != ""]
    text = "".join(lines)
    return text
