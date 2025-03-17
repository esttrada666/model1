# model1

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import whisper
import ollama
from gtts import gTTS
import os
import sounddevice as sd
import soundfile as sf
from playsound import playsound
import uuid
import asyncio
import logging

py installer

pyinstaller --onefile --name=AsistenteELISA --add-data "enter your route\whisper\assets" --add-data "enter your route\whisper;tiny.pt" --hidden-import=whisper --hidden-import=sounddevice --hidden-import=soundfile --hidden-import=playsound --icon=icono.ico nameofyourfile.py
