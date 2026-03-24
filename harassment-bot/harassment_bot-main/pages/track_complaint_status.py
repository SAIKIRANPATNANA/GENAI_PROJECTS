import streamlit as st
import pymongo 
from pymongo.mongo_client import MongoClient
from gridfs import GridFS
import pandas as pd
import numpy as np
import time
from bson.objectid import ObjectId

st.title("Track Complaint Status")
uri = "mongodb+srv://saikiranpatnana:mayya143@saikiran.bdu0jbl.mongodb.net/?retryWrites=true&w=majority&appName=saikiran"
client=MongoClient(uri)
db=client.test
collection = db['harassment_register']
fs = GridFS(db)

status_mapping = {0: "📑 REPORTED", 1: "⏳ REVIEWED", 2: "✅ RESOLVED"}

# User Input
token = st.text_input("Please Enter Your Registered Token Number:")

if token:
    # Fetch the complaint record
    for record in collection.find():
        print(record.get('token'))
        if record.get('token') == int(token):
            status = record.get('status')
            st.success(f"Your Complaint is {status_mapping[status]}")

