import os
import tempfile
from sqlalchemy.orm import Session
from llama_index.core import SimpleDirectoryReader, Document as LlamaDocument
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.web import SimpleWebPageReader
from app.models.document import Document
from app.services.vector_store import VectorStoreGateway
from app.config.settings import settings
from app.constants.app_constants import DocumentStatus, DocumentType
from app.constants.messages import (
    INGESTION_COMPLETE,
    INGESTION_FAILED,
    URL_FETCH_FAILED,
)


class DocumentIndexer:

    def __init__(self, db: Session):
        self.db = db
        self.splitter = SentenceSplitter(
            chunk_size=settings.default_chunk_size,
            chunk_overlap=settings.default_chunk_overlap,
        )

    def _chunk_documents(self, documents: list[LlamaDocument]) -> list[str]:
        nodes = self.splitter.get_nodes_from_documents(documents)
        return [node.get_content() for node in nodes]

    def _store_chunks(self, chunks: list[str], metadata: dict) -> None:
        metadatas = [dict(metadata) for _ in chunks]
        store = VectorStoreGateway.get_store()
        store.add(chunks, metadatas)

    def _save_document_record(
        self,
        name: str,
        source: str,
        document_type: str,
        chunk_count: int,
        status: str,
    ) -> Document:
        doc = Document(
            name=name,
            source=source,
            document_type=document_type,
            chunk_count=chunk_count,
            status=status,
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def ingest_pdf(self, file_bytes: bytes, name: str) -> Document:
        try:
            with tempfile.NamedTemporaryFile(
                suffix=".pdf", delete=False
            ) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name

            documents = SimpleDirectoryReader(
                input_files=[tmp_path]
            ).load_data()
            chunks = self._chunk_documents(documents)
            self._store_chunks(chunks, {"source": name, "type": DocumentType.PDF})
            os.unlink(tmp_path)

            return self._save_document_record(
                name=name,
                source=name,
                document_type=DocumentType.PDF,
                chunk_count=len(chunks),
                status=DocumentStatus.INGESTED,
            )
        except Exception as e:
            return self._save_document_record(
                name=name,
                source=name,
                document_type=DocumentType.PDF,
                chunk_count=0,
                status=DocumentStatus.FAILED,
            )

    def ingest_text(self, text: str, name: str) -> Document:
        try:
            documents = [LlamaDocument(text=text)]
            chunks = self._chunk_documents(documents)
            self._store_chunks(chunks, {"source": name, "type": DocumentType.TEXT})

            return self._save_document_record(
                name=name,
                source=name,
                document_type=DocumentType.TEXT,
                chunk_count=len(chunks),
                status=DocumentStatus.INGESTED,
            )
        except Exception:
            return self._save_document_record(
                name=name,
                source=name,
                document_type=DocumentType.TEXT,
                chunk_count=0,
                status=DocumentStatus.FAILED,
            )

    def ingest_url(self, url: str, name: str) -> Document:
        try:
            documents = SimpleWebPageReader(html_to_text=True).load_data([url])
            chunks = self._chunk_documents(documents)
            self._store_chunks(chunks, {"source": url, "type": DocumentType.URL})

            return self._save_document_record(
                name=name,
                source=url,
                document_type=DocumentType.URL,
                chunk_count=len(chunks),
                status=DocumentStatus.INGESTED,
            )
        except Exception:
            return self._save_document_record(
                name=name,
                source=url,
                document_type=DocumentType.URL,
                chunk_count=0,
                status=DocumentStatus.FAILED,
            )

    def list_documents(self) -> list[Document]:
        return self.db.query(Document).all()