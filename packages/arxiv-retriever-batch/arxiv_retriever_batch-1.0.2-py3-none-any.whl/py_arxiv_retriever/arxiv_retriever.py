import os
from .axirv_loader import ArxivLoader
from typing import Any, Literal
from langchain_core.documents import Document
from pyaws_s3 import S3Client
from langchain_community.document_loaders import PyPDFLoader

PathType = Literal["fs", "s3"]

class ArxivRetriever(ArxivLoader):
    
    path_type: PathType = "fs"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.path_type = kwargs.get("path_type", self.path_type)
    
    def _get_documents_from_path(self) -> list[Document]:
        """
        Loads documents from a specified path based on the file format.
        Args:
        - path (str): The path to the document file.
        """
        
        if self.path is None:
            raise ValueError("Path is not set. Please provide a valid path.")
        
        loader = PyPDFLoader(self.path)
        return loader.load()
    
    def _process_documents_s3(self, **kwargs) -> list[Document]:
        """
        Processes documents from S3 by downloading them to a local path and loading them.
        
        Args:
        - prefix (str): The S3 prefix to filter files.
        - limit (int): The maximum number of files to download.
        - path_download (str): The local path where files will be downloaded.
        
        Returns:
        - list[Document]: A list of Document objects loaded from the downloaded files.
        """
        
        if self.path is None:
            raise ValueError("Path is not set. Please provide a valid path.")
        
        if not all([self.aws_access_key_id, self.aws_secret_access_key, self.bucket_name, self.region_name]):
            raise ValueError("Missing AWS credentials or bucket information for S3 access.")
            
        prefix = kwargs.get("prefix", self.prefix)    
            
        if prefix is None:
            raise ValueError("Prefix is not set. Please provide a valid prefix for S3 files.")
        
        documents : list[Document] = []
        
        s3_client = S3Client(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            bucket_name=self.bucket_name,
            region_name=self.region_name
        )
        list_files : list[str] = s3_client.list_files(prefix)
        list_files.sort()
        
        limit = kwargs.get("limit", 0)
        
        # limit the number of files to download
        if limit > 0:
            list_files = list_files[:limit]
            
        # create a temporary local directory to store downloaded files
        for file in list_files:
            # esegui il download del file nella cartella temporanea locale
            local_file = f"{self.path}/{os.path.basename(file)}"
            
            if local_file is None:
                raise ValueError("Local file path is not set. Please provide a valid local file path.")
            
            if not os.path.exists(local_file):
                s3_client.download(file, local_path=local_file)
            
            loader = PyPDFLoader(local_file)
            documents.extend(loader.load())
            
        # process the downloaded files
        return documents
    
    def _process_documents_fs(self, **kwargs) -> list[Document]:
        """
        Processes documents from the local filesystem by loading them from a specified path.
        
        Args:
        - path (str): The local path where files are located.
        
        Returns:
        - list[Document]: A list of Document objects loaded from the specified path.
        """
        
        if self.path is None:
            raise ValueError("Path is not set. Please provide a valid path.")
        
        pdf_files = [f for f in os.listdir(self.path) if f.lower().endswith(".pdf")]
        documents: list[Document] = []
        for pdf_file in pdf_files:
            file_path = os.path.join(self.path, pdf_file)
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
        return documents
    
    def process(self, **kwargs: Any) -> list[Document]:    
        """
        Processes a PDF document by loading it, splitting it into chunks, embedding them, and building a knowledge graph.
        
        Args:
            - pdf_path (str): The path to the PDF file to be processed.
            - path (str): The local path where files are located (if path_type is "fs").
            - path_type (str): The type of path, either "fs" for local filesystem or "s3" for AWS S3.
            - prefix (str): The S3 prefix to filter files (if path_type is "s3").
            - limit (int): The maximum number of files to download (if path_type is "s3").
            - path_download (str): The local path where files will be downloaded (if path_type is "s3").
        
        Returns:
        - None
        """
        try:
            path_type : PathType = kwargs.get("path_type", self.path_type)
            
            if path_type == "s3":
                return self._process_documents_s3(**kwargs)
            elif path_type == "fs":
                return self._process_documents_fs(**kwargs)
            
            return []
        except Exception as e:
            raise e
