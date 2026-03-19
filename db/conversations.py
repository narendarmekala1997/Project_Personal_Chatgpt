import uuid
from datetime import datetime,timezone
from typing import Optional,Dict,Any

from pymongo import DESCENDING
from db.mongo import get_collection

conversations = get_collection('conversations')
conversations.create_index([("last_interacted",DESCENDING)])

#******HELPERS*********
def now_utc():
    return datetime.now(timezone.utc)
def create_new_conversation_id()->str:
    return str(uuid.uuid4())

#***core services******
def create_new_conversation(title:Optional[str]=None,role:Optional[str]=None,content:Optional[str]=None)->str:
    convo_id = create_new_conversation_id()
    ts = now_utc()
    doc = {
        "_id": convo_id,
        "title": title or "Untitled Conversation",
        "messages":[],
        "last_interacted": ts
    }
    if role and content:
        doc["messages"].append({
            "role":role,
            "content":content,
            "ts":ts
        })
    conversations.insert_one(doc)
    return convo_id
def add_message(convo_id:str, role:str, content:str) -> bool:
    ts = now_utc()
    result = conversations.update_one(
        {"_id": convo_id},
        {
            "$push":{"messages":{
                "role":role,
                "content":content,
                "ts":ts
            }},
            "$set":{"last_interacted":ts}
        }
    )
    return result.matched_count == 1
def get_conversation(convo_id:str) -> Optional[Dict[str, Any]]:
    ts = now_utc()
    doc = conversations.find_one_and_update(
        {"_id": convo_id},
        {"$set":{"last_interacted":ts}},
        return_document=True
    )
    return doc
def get_all_conversations()-> Dict[str, str]:
   cursor = conversations.find({},{"title":1}).sort("last_interacted",DESCENDING)
   return {doc["_id"]: doc["title"] for doc in cursor}

#---------Example Usage ------------------
# convo_id = create_new_conversation(title="Intro to Deep Learning",role="user",content="what is Deep Learning")
# add_message(convo_id,role="assistant",content="Answer to DL Query")
# print(get_conversation(convo_id))
# print("\n")
# print(get_all_conversations())




