import asyncio
import json
import chromadb
from loguru import logger
from typing import Optional
from app.core.config import ChromaSettings

chroma_settings = ChromaSettings()

class ChromaService:
    def __init__(self, collection_name: str = None):
        self.host = chroma_settings.chroma_network_name
        self.port = chroma_settings.chroma_port
        self.collection_name = collection_name or chroma_settings.chroma_collection_name
        try:
            if self.host and self.port:
                self.client = chromadb.HttpClient(host=self.host, port=self.port)
            else:
                self.client = chromadb.PersistentClient()
            self.collection = self.client.get_or_create_collection(self.collection_name)
        except Exception as e:
            logger.exception(f"Failed to initialize Chroma client/collection: {e}")
            raise

    async def save_document(self, document_id: str, data: dict) -> str:
        loop = asyncio.get_event_loop()
        payload = json.dumps(data, ensure_ascii=False)
        await loop.run_in_executor(
            None,
            lambda: self.collection.add(
                ids=[document_id],
                documents=[payload]
            )
        )
        return document_id

    async def get_document(self, document_id: str) -> Optional[dict]:
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(
            None,
            lambda: self.collection.get(ids=[document_id])
        )
        docs = res.get("documents", [])
        if docs and docs[0]:
            try:
                return json.loads(docs[0])
            except Exception as e:
                logger.warning(f"Failed to parse JSON: {e}, raw: {docs[0]}")
                return {"raw": docs[0]}
        return None
        

    async def delete_document(self, document_id: str) -> str:
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                self.collection.delete,
                [document_id]
            )
            return document_id
        except Exception as e:
            logger.exception(f"Chroma delete_document error for id={document_id}: {e}")
            raise

    async def update_document(self, document_id: str, data: dict) -> bool:
        loop = asyncio.get_event_loop()
        try:
            payload = json.dumps(data, ensure_ascii=False)
            await loop.run_in_executor(None, self.collection.delete, [document_id])
            await loop.run_in_executor(
                None,
                lambda: self.collection.add(
                    ids=[document_id],
                    documents=[payload]
                )
            )
            return True
        except Exception as e:
            logger.exception(f"Chroma update_document error for id={document_id}: {e}")
            raise