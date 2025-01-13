from fastapi import FastAPI
from pydantic import BaseModel
from chatbot import ChatBot
import warnings
from fastapi.middleware.cors import CORSMiddleware
# Tắt các cảnh báo
warnings.filterwarnings("ignore")

a = ChatBot()
a.process_query('Hôn nhân là gì')
