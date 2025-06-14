import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from pymongo import MongoClient
from pymongo.database import Database

class DataStore:
    """Clase base para el almacenamiento de datos"""
    
    def __init__(self):
        self.using_mongodb = False
    
    def find_one(self, collection: str, query: dict) -> Optional[Dict[str, Any]]:
        raise NotImplementedError
    
    def insert_one(self, collection: str, document: dict) -> None:
        raise NotImplementedError
    
    def find(self, collection: str, query: dict = None) -> List[Dict[str, Any]]:
        raise NotImplementedError


class MongoDataStore(DataStore):
    """Implementación de DataStore usando MongoDB"""
    
    def __init__(self, mongo_uri: str, db_name: str):
        super().__init__()
        self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[db_name]
        self.using_mongodb = True
        
        # Crear colecciones necesarias si no existen
        for collection in ['server_settings', 'preguntas', 'logs']:
            if collection not in self.db.list_collection_names():
                self.db.create_collection(collection)
    
    def find_one(self, collection: str, query: dict) -> Optional[Dict[str, Any]]:
        return self.db[collection].find_one(query)
    
    def insert_one(self, collection: str, document: dict) -> None:
        return self.db[collection].insert_one(document)
    
    def find(self, collection: str, query: dict = None) -> List[Dict[str, Any]]:
        if query is None:
            query = {}
        return list(self.db[collection].find(query))


class FileDataStore(DataStore):
    """Implementación de DataStore usando archivos JSON"""
    
    def __init__(self, data_dir: str = 'data'):
        super().__init__()
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.using_mongodb = False
    
    def _get_collection_path(self, collection: str) -> Path:
        return self.data_dir / f"{collection}.json"
    
    def _load_collection(self, collection: str) -> Dict[str, Any]:
        path = self._get_collection_path(collection)
        if not path.exists():
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_collection(self, collection: str, data: Dict[str, Any]) -> None:
        path = self._get_collection_path(collection)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def find_one(self, collection: str, query: dict) -> Optional[Dict[str, Any]]:
        if not query:
            return None
            
        data = self._load_collection(collection)
        for doc in data.values():
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None
    
    def insert_one(self, collection: str, document: dict) -> None:
        from bson import ObjectId
        
        data = self._load_collection(collection)
        doc_id = str(ObjectId())
        document['_id'] = doc_id
        data[doc_id] = document
        self._save_collection(collection, data)
        return {'inserted_id': doc_id}
    
    def find(self, collection: str, query: dict = None) -> List[Dict[str, Any]]:
        if query is None:
            query = {}
            
        data = self._load_collection(collection)
        results = []
        for doc in data.values():
            if all(doc.get(k) == v for k, v in query.items()):
                results.append(doc)
        return results


def safe_print(*args, **kwargs):
    """Función segura para imprimir en la consola de Windows"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Si falla, intentar con una codificación que funcione en Windows
        import sys
        text = ' '.join(str(arg) for arg in args)
        sys.stdout.buffer.write((text + '\n').encode('utf-8', errors='replace'))
        sys.stdout.flush()

def get_datastore() -> DataStore:
    """Obtiene el almacenamiento de datos configurado"""
    from dotenv import load_dotenv
    load_dotenv()
    
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    db_name = os.getenv('DB_NAME', 'discord_bot')
    
    # Primero intentar con MongoDB si está configurado
    if mongo_uri and mongo_uri != 'mongodb://localhost:27017/':
        try:
            safe_print("Intentando conectar a MongoDB...")
            store = MongoDataStore(mongo_uri, db_name)
            safe_print("Conectado a MongoDB (Almacenamiento Principal)")
            return store
        except Exception as e:
            safe_print(f"No se pudo conectar a MongoDB: {str(e)}")
            safe_print("Usando almacenamiento local en archivos")
    else:
        safe_print("MongoDB no configurado. Usando almacenamiento local en archivos")
    
    # Si falla o no está configurado, usar almacenamiento local
    return FileDataStore()

# Inicializar el almacenamiento
datastore = get_datastore()
