import os
from langchain.llms import LlamaCpp
from llama_index import (
    GPTVectorStoreIndex,
    GPTVectorStoreIndex,
    GPTListIndex,
    ServiceContext,
    ResponseSynthesizer,
    LangchainEmbedding
)
#from langchain.text_splitter import CharacterTextSplitter
#from llama_index.node_parser import SimpleNodeParser

from langchain.embeddings import HuggingFaceEmbeddings

from llama_index import download_loader, StorageContext, load_index_from_storage
from llama_index import (
    Document,
    LLMPredictor,
    PromptHelper
)
from llama_index.indices.postprocessor import SimilarityPostprocessor
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.storage.index_store import SimpleIndexStore
from llama_index.storage.docstore import SimpleDocumentStore
from llama_index.storage.storage_context import SimpleVectorStore

from googlesearch import search as google_search

from utils import *

import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, required=True)
args = parser.parse_args()
model_path = args.model


def query_llm(index, prompt, service_context, retriever_mode='embedding', response_mode='tree_summarize'):
    response_synthesizer = ResponseSynthesizer.from_args(
        service_context=service_context,
        node_postprocessors=[
            SimilarityPostprocessor(similarity_cutoff=0.7)
        ]
    )
    retriever = index.as_retriever(retriever_mode=retriever_mode, service_context=service_context)
    query_engine = RetrieverQueryEngine.from_args(retriever, response_synthesizer=response_synthesizer, response_mode=response_mode,  service_context=service_context)
    return query_engine.query(prompt)


def get_documents(file_src):
    documents = []
    logging.debug("Loading documents...")
    print(f"file_src: {file_src}")
    for file in file_src:
        if type(file) == str:
            print(f"file: {file}")
            if "http" in file:
                logging.debug("Loading web page...")
                BeautifulSoupWebReader = download_loader("BeautifulSoupWebReader")
                loader = BeautifulSoupWebReader()
                documents += loader.load_data([file])
        else:
            logging.debug(f"file: {file.name}")
            if os.path.splitext(file.name)[1] == ".pdf":
                logging.debug("Loading PDF...")
                CJKPDFReader = download_loader("CJKPDFReader")
                loader = CJKPDFReader()
                documents += loader.load_data(file=file.name)
            elif os.path.splitext(file.name)[1] == ".epub":
                logging.debug("Loading EPUB...")
                EpubReader = download_loader("EpubReader")
                loader = EpubReader()
                documents += loader.load_data(file=file.name)
            else:
                logging.debug("Loading text file...")
                with open(file.name, "r", encoding="utf-8") as f:
                    text = add_space(f.read())
                    documents += [Document(text)]
    return documents


def construct_index(
    file_src,
    index_name,
    index_type,
    max_input_size=4096,
    num_outputs=512,
    max_chunk_overlap=20,
    chunk_size_limit=None,
    embedding_limit=None,
    separator=" ",
    num_children=10,
    max_keywords_per_chunk=10
):
    chunk_size_limit = None if chunk_size_limit == 0 else chunk_size_limit
    embedding_limit = None if embedding_limit == 0 else embedding_limit
    separator = " " if separator == "" else separator

    llm = LlamaCpp(model_path=model_path,
        n_ctx=2048, 
        use_mlock=True,
        n_parts=-1, 
        temperature=0.7, 
        top_p=0.40,
        last_n_tokens_size=200,
        n_threads=4,
        f16_kv=True,
        max_tokens=400
    )
    llm_predictor = LLMPredictor(
        llm=llm
    )
    prompt_helper = PromptHelper(
        max_input_size,
        num_outputs,
        max_chunk_overlap,
        embedding_limit,
        chunk_size_limit,
        separator=separator,
    )
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
    documents = get_documents(file_src)

    try:
        if index_type == "_GPTVectorStoreIndex":
            index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)
        else:
            index = GPTListIndex.from_documents(documents, service_context=service_context)
        index.storage_context.persist(persist_dir="./index")
    except Exception as e:
        print(e)
        return None

    
    newlist = refresh_json_list(plain=True)
    return gr.Dropdown.update(choices=newlist, value=index_name)


def chat_ai(
    index_select,
    question,
    prompt_tmpl,
    refine_tmpl,
    sim_k,
    chat_tone,
    context,
    chatbot,
    search_mode=[],
):
    if index_select == "search" and search_mode==[]:
        chatbot.append((question, "❗search"))
        return context, chatbot

    logging.info(f"Question: {question}")

    temprature = 2 if chat_tone == 0 else 1 if chat_tone == 1 else 0.5
    if search_mode:
        index_select = search_construct(question, search_mode, index_select)
    logging.debug(f"Index: {index_select}")
    response = ask_ai(
        index_select,
        question,
        prompt_tmpl,
        refine_tmpl,
        sim_k,
        temprature,
        context
    )
    print(response)

    if response is None:
        response = llm._call(question)
    response = parse_text(response)

    context.append({"role": "user", "content": question})
    context.append({"role": "assistant", "content": response})
    chatbot.append((question, response))

    return context, chatbot


def ask_ai(
    index_select,
    question,
    prompt_tmpl,
    refine_tmpl,
    sim_k=1,
    temprature=0,
    prefix_messages=[]
):
    logging.debug("Querying index...")
    prompt_helper = PromptHelper(
        4096,
        512,
        20
    )
    llm = LlamaCpp(model_path=model_path,
        n_ctx=500, 
        use_mlock=True,
        n_parts=-1, 
        temperature=temprature, 
        top_p=0.40,
        last_n_tokens_size=400,
        n_threads=4,
        f16_kv=True,
        max_tokens=400
    )
    embeddings = HuggingFaceEmbeddings(model_kwargs={"device": "mps"})
    embed_model = LangchainEmbedding(embeddings)
    llm_predictor = LLMPredictor(
        llm=llm
    )
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, embed_model=embed_model, prompt_helper=prompt_helper)
    # node_parser = SimpleNodeParser(text_splitter=CharacterTextSplitter(chunk_size=1000))
    #qa_prompt = QuestionAnswerPrompt(prompt_tmpl)
    #rf_prompt = RefinePrompt(refine_tmpl)
    response = None  # Initialize response variable to avoid UnboundLocalError
    logging.debug("Using GPTVectorStoreIndex")
    storage_context = StorageContext.from_defaults(
        docstore=SimpleDocumentStore.from_persist_dir(persist_dir="./index"),
        vector_store=SimpleVectorStore.from_persist_dir(persist_dir="./index"),
        index_store=SimpleIndexStore.from_persist_dir(persist_dir="./index"),
    )
    index = load_index_from_storage(service_context=service_context, storage_context=storage_context)
    response = query_llm(index, question, service_context)

    if response is not None:
        logging.info(f"Response: {response}")
        ret_text = response.response
        ret_text += "\n----------\n"
        nodes = []
        for index, node in enumerate(response.source_nodes):
            nodes.append(f"[{index+1}] {node.source_text}")
        ret_text += "\n\n".join(nodes)
        return ret_text
    else:
        logging.debug("No response found, returning None")
        return None


def search_construct(question, search_mode, index_select):
    print(f"You asked: {question}")
    llm = LlamaCpp(model_path=model_path,
        n_ctx=500, 
        use_mlock=True,
        n_parts=-1, 
        temperature=0.5, 
        top_p=0.40,
        last_n_tokens_size=400,
        n_threads=4,
        f16_kv=True,
        max_tokens=400
    )
    chat = llm
    search_terms = (
        chat.generate(
            [
                f"Please extract search terms from the user’s question. The search terms is a concise sentence, which will be searched on Google to obtain relevant information to answer the user’s question, too generalized search terms doesn’t help. Please provide no more than two search terms. Please provide the most relevant search terms only, the search terms should directly correspond to the user’s question. Please separate different search items with commas, with no quote marks. The user’s question is: {question}"
            ]
        )
        .generations[0][0]
        .text.strip()
    )
    search_terms = search_terms.replace('"', "")
    search_terms = search_terms.replace(".", "")
    links = []
    for keywords in search_terms.split(","):
        keywords = keywords.strip()
        for search_engine in search_mode:
            if "Google" in search_engine:
                print(f"Googling: {keywords}")
                search_iter = google_search(keywords, num_results=5)
                links += [next(search_iter) for _ in range(10)]
            if "Manual" in search_engine:
                print(f"Searching manually: {keywords}")
                print("Please input links manually. (Enter 'q' to quit.)")
                while True:
                    link = input("Enter link：\n")
                    if link == "q":
                        break
                    else:
                        links.append(link)
    links = list(set(links))
    if len(links) == 0:
        return index_select
    print("Extracting data from links...")
    print("\n".join(links))
    search_index_name = " ".join(search_terms.split(","))
    construct_index(links, search_index_name, "GPTVectorStoreIndex")
    print(f"Index {search_index_name} constructed.")
    return search_index_name + "_GPTVectorStoreIndex"
