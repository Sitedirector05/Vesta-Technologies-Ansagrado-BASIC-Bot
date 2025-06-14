from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
from pymongo import MongoClient
from pymongo.database import Database

class ProvisionalDataStore:
    """Almacenamiento de datos provisional cuando MongoDB no está disponible"""
    
    def __init__(self):
        self.data = {}
        self.using_mongodb = False
        self.data_file = 'provisional_data.json'
        self._load_data()
    
    def _load_data(self):
        """Cargar datos desde el archivo si existe"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"Error al cargar datos provisionales: {e}")
                self.data = {}
    
    def _save_data(self):
        """Guardar datos en el archivo"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Error al guardar datos provisionales: {e}")
    
    def find_one(self, collection: str, query: dict = None) -> Optional[Dict]:
        """Busca un documento en la colección especificada"""
        if collection not in self.data:
            self.data[collection] = []
            return None
        
        if not query:
            return self.data[collection][0] if self.data[collection] else None
        
        for doc in self.data[collection]:
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None
    
    def insert_one(self, collection: str, document: dict) -> Dict:
        """Inserta un documento en la colección especificada"""
        if collection not in self.data:
            self.data[collection] = []
        
        # Añadir timestamp si no existe
        if 'created_at' not in document:
            document['created_at'] = datetime.now(timezone.utc).isoformat()
        
        self.data[collection].append(document)
        self._save_data()
        return {'inserted_id': len(self.data[collection]) - 1}
    
    def find(self, collection: str, query: dict = None) -> List[Dict]:
        """Busca múltiples documentos en la colección especificada"""
        if collection not in self.data:
            self.data[collection] = []
            return []
        
        if not query:
            return self.data[collection].copy()
        
        return [doc for doc in self.data[collection] 
                if all(doc.get(k) == v for k, v in query.items())]
    
    def sync_with_mongodb(self, mongo_db: Database) -> bool:
        """Sincroniza los datos con MongoDB cuando esté disponible"""
        try:
            for collection_name, documents in self.data.items():
                if not documents:
                    continue
                    
                mongo_collection = mongo_db[collection_name]
                
                # Insertar documentos que no existan en MongoDB
                for doc in documents:
                    query = {'_id': doc.get('_id')} if '_id' in doc else doc
                    mongo_collection.update_one(
                        query,
                        {'$set': doc},
                        upsert=True
                    )
            
            # Limpiar datos locales después de sincronizar
            self.data = {}
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
            
            self.using_mongodb = True
            return True
            
        except Exception as e:
            print(f"Error al sincronizar con MongoDB: {e}")
            return False


def setup_datastore(mongodb_uri: str, db_name: str):
    """Configura el almacenamiento, intentando conectar a MongoDB primero"""
    # Primero intentar conectar a MongoDB
    try:
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client[db_name]
        
        # Crear colecciones necesarias si no existen
        for collection in ['logs', 'preguntas']:
            if collection not in db.list_collection_names():
                db.create_collection(collection)
        
        print("✅ Conectado a MongoDB (Almacenamiento Principal)")
        return db, True
        
    except Exception as e:
        print(f"❌ No se pudo conectar a MongoDB: {e}")
        print("Iniciando con almacenamiento provisional...")
        
        # Si falla, usar almacenamiento provisional
        store = ProvisionalDataStore()
        
        # Crear un wrapper para mantener la compatibilidad con la API de PyMongo
        class DBWrapper:
            def __init__(self, store):
                self.store = store
                self.command = lambda *_, **__: {}
                
            def __getattr__(self, name):
                return CollectionWrapper(name, self.store)
                
            def __getitem__(self, name):
                return CollectionWrapper(name, self.store)
        
        class CollectionWrapper:
            def __init__(self, name, store):
                self.name = name
                self.store = store
                
            def find_one(self, query=None, **kwargs):
                return self.store.find_one(self.name, query or {})
                
            def insert_one(self, document, **kwargs):
                return self.store.insert_one(self.name, document)
                
            def find(self, query=None, **kwargs):
                return self.store.find(self.name, query or {})
                
            def update_one(self, filter, update, **kwargs):
                # Implementación básica para update_one
                doc = self.store.find_one(self.name, filter)
                if doc and '$set' in update:
                    doc.update(update['$set'])
                    return {'matched_count': 1, 'modified_count': 1}
                return {'matched_count': 0, 'modified_count': 0}
        
        return DBWrapper(store), False
