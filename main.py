import sys
import gradio as gr

from llm import *
from utils import *
from presets import *
from overwrites import *

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

PromptHelper.compact_text_chunks = compact_text_chunks

with gr.Blocks(css="") as demo:
    with gr.Box():
        gr.Markdown("<h1 style='font-size: 48px; text-align: center;'>📚  LLaMa Difu  📓</h1>")
        gr.Markdown("<h3 style='text-align: center;'>LLaMa Do It For U 🦙</h3>")
        
    chat_context = gr.State([])
    new_google_chat_context = gr.State([])

    with gr.Row():
        with gr.Column(scale=3):
            with gr.Box():
                gr.Markdown("**Indicies**")
                with gr.Row():
                    with gr.Column(scale=12):
                        index_select = gr.Dropdown(choices=refresh_json_list(plain=True), value="index_select", show_label=False, multiselect=False).style(container=False)
                    with gr.Column(min_width=30, scale=1):
                        index_refresh_btn = gr.Button("🔄").style()


    with gr.Tab("Search"):
        with gr.Row():
            with gr.Column(scale=1):
                chat_tone = gr.Radio(["smart", "concise", "creative"], label="chat_tone", type="index", value="concise")
            with gr.Column(scale=3):
                search_options_checkbox = gr.CheckboxGroup(label="APIs", choices=["📚 Google", "Manual"])
        chatbot = gr.Chatbot()
        with gr.Row():
            with gr.Column(min_width=50, scale=1):
                chat_empty_btn = gr.Button("🧹", variant="secondary")
            with gr.Column(scale=12):
                chat_input = gr.Textbox(show_label=False, placeholder="Enter text...").style(container=False)
            with gr.Column(min_width=50, scale=1):
                chat_submit_btn = gr.Button("🚀", variant="primary")


    with gr.Tab("Setting"):
        with gr.Row():
            sim_k = gr.Slider(1, 10, 3, step=1, label="similarity_topk", interactive=True, show_label=True)
            tempurature = gr.Slider(0, 2, 0.5, step=0.1, label="tempurature", interactive=True, show_label=True)
        with gr.Row():
            with gr.Column():
                tmpl_select = gr.Radio(list(prompt_tmpl_dict.keys()), value="Default", label="Prompt", interactive=True)
                prompt_tmpl = gr.Textbox(value=prompt_tmpl_dict["Default"] ,lines=10, max_lines=40 ,show_label=False)
            with gr.Column():
                refine_select = gr.Radio(list(refine_tmpl_dict.keys()), value="Default", label="Refine", interactive=True)
                refine_tmpl = gr.Textbox(value=refine_tmpl_dict["Default"] ,lines=10, max_lines=40 ,show_label=False)


    with gr.Tab("Upload"):
        with gr.Row():
            with gr.Column():
                index_type = gr.Dropdown(choices=["GPTListIndex", "GPTVectorStoreIndex"], label="index_type", value="GPTVectorStoreIndex")
                upload_file = gr.Files(label="upload_file .txt, .pdf, .epub)")
                new_index_name = gr.Textbox(placeholder="new_index_name: ", show_label=False).style(container=False)
                construct_btn = gr.Button("⚒️ Index", variant="primary")
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        max_input_size = gr.Slider(256, 4096, 4096, step=1, label="max_input_size", interactive=True, show_label=True)
                        num_outputs = gr.Slider(256, 4096, 512, step=1, label="num_outputs", interactive=True, show_label=True)
                    with gr.Row():
                        max_chunk_overlap = gr.Slider(0, 100, 20, step=1, label="max_chunk_overlap", interactive=True, show_label=True)
                        chunk_size_limit = gr.Slider(0, 4096, 0, step=1, label="chunk_size_limit", interactive=True, show_label=True)
                    with gr.Row():
                        embedding_limit = gr.Slider(0, 100, 0, step=1, label="embedding_limit", interactive=True, show_label=True)
                        separator = gr.Textbox(show_label=False, label="separator", placeholder=",", value="", interactive=True)
                    with gr.Row():
                        num_children = gr.Slider(2, 100, 10, step=1, label="num_children", interactive=False, show_label=True)
                        max_keywords_per_chunk = gr.Slider(1, 100, 10, step=1, label="max_keywords_per_chunk", interactive=False, show_label=True)


    index_refresh_btn.click(refresh_json_list, None, [index_select])

    chat_input.submit(chat_ai, [index_select, chat_input, prompt_tmpl, refine_tmpl, sim_k, chat_tone, chat_context, chatbot, search_options_checkbox], [chat_context, chatbot])
    chat_input.submit(reset_textbox, [], [chat_input])
    chat_submit_btn.click(chat_ai, [index_select, chat_input, prompt_tmpl, refine_tmpl, sim_k, chat_tone, chat_context, chatbot, search_options_checkbox], [chat_context, chatbot])
    chat_submit_btn.click(reset_textbox, [], [chat_input])
    chat_empty_btn.click(lambda: ([], []), None, [chat_context, chatbot])

    tmpl_select.change(change_prompt_tmpl, [tmpl_select], [prompt_tmpl])
    refine_select.change(change_refine_tmpl, [refine_select], [refine_tmpl])

    index_type.change(lock_params, [index_type], [num_children, max_keywords_per_chunk])
    construct_btn.click(construct_index, [upload_file, new_index_name, index_type, max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit, embedding_limit, separator, num_children], [index_select])


if __name__ == "__main__":
    demo.title = "LLaMa Do It For U"
    demo.queue().launch()
