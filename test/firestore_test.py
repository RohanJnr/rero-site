import asyncio

import firebase_admin
from firebase_admin import credentials, firestore, firestore_async



cred = credentials.Certificate("ieee-ras-rero-firebase-adminsdk.json")
app = firebase_admin.initialize_app(cred)


def sync_version():

    db = firestore.client(app)

    docs = db.collection("submissions").stream()

    # doc = doc_ref.get()

    for doc in docs:
        print(f"{doc.id} => {doc.to_dict()}")



    update_time, obj_ref = db.collection("submissions").add({"message": "hi"})
    print(f"Added document with id {obj_ref.id}")


async def async_version():
    print("executing async function.")
    db = firestore_async.client(app)
    collection = db.collection("submissions")

    doc_ref = collection.document("KXLxdfF2KuhC8Vi09usZ")
    from google.cloud.firestore_v1.async_document import AsyncDocumentReference
    

    doc = await doc_ref.get()
    print(f"{doc.id} => {doc.to_dict()}")

    # async for doc in collection.stream():
    #     print(f"{doc.id} => {doc.to_dict()}")



    # update_time, obj_ref = await db.collection("submissions").add({"message": "this is async"})
    # print(f"Added document with id {obj_ref.id}")


asyncio.run(async_version())