import os

from langchain_core.documents import Document

from utils.logger_handler import logger
from utils.path_tools import get_abs_path
from langchain_chroma import Chroma
from utils.config_handler import chroma_conf
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.file_handler import pdf_loader,txt_loader,listdir_with_allowed_type,get_file_md5_hex

class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=get_abs_path(chroma_conf["persist_directory"]),
        )

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,
        )

    def get_retriever(self): # 向量检索器
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})

    def load_document(self):
        '''
        从数据文件夹内读取文件，转到向量数据库中，并且要用md5去重
        :return:
        '''

        def check_md5_hex(md5_for_check:str):
            if not os.path.exists(get_abs_path(chroma_conf["md5_hex_store"])):
                open(get_abs_path(chroma_conf["md5_hex_store"]), "w", encoding='utf-8').close()
                return False # md5没处理过
            with open(get_abs_path(chroma_conf["md5_hex_store"]), 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True # md5处理过

                return False

        def save_md5_hex(md5_for_check:str):
            with open(get_abs_path(chroma_conf["md5_hex_store"]), 'a', encoding='utf-8') as f:
                f.write(md5_for_check + "\n")

        def get_file_document(read_path:str):
            if read_path.endswith("txt"):
                return txt_loader(read_path)

            if read_path.endswith("pdf"):
                return pdf_loader(read_path)

            return []

        allowed_files_path:list[str] = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"],)
        )

        for path in allowed_files_path:

            # 获取文件md5
            md5_hex = get_file_md5_hex(path)
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]{path}内容已经存在于知识库内")
                continue

            try:
                documents : list[Document] = get_file_document(path)

                if not documents:
                    logger.warning(f"[加载知识库]{path}内没用有效文本内容，跳过")
                    continue

                split_document:list[Document] = self.spliter.split_documents(documents)

                if not split_document:
                    logger.warning(f"[加载知识库]{path}分片后没用有效文本内容，跳过")
                    continue
                # 内容存入向量库
                self.vector_store.add_documents(split_document)

                save_md5_hex(md5_hex)

                logger.info(f"[加载知识库]{path}内容加载成功")
            except Exception as e:
                # exc_info为ture 会记录详细的报错，否则仅记录报错本身
                logger.error(f"[加载知识库]{path}加载失败：{str(e)}",exc_info=True)
                continue


if __name__ == '__main__':
    vs = VectorStoreService()
    vs.load_document()
    retriever = vs.get_retriever()
    res = retriever.invoke("迷路")
    for r in res:
        print(r.page_content)
        print("-"*20)







