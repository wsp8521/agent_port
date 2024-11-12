import os
from dotenv import load_dotenv
from pynput import keyboard
from langchain_openai import ChatOpenAI
import numpy
import sounddevice as sd #classe que ornece funcionalidades para manipulação de áudio



load_dotenv()

class MovCarg:
    def __init__(self, model):
        self.model =model
        self.is_recoding = False,
        self.audio_data = []
        
    
    
    def run(self):
        print("Gravando") 
        
         #configurações de audio
        def callback(indata, outdata, frames, time, status):
            if self.is_recording: #verifica se a gravação foi inicializada
              self.audio_data.extend(indata.copy) #Armazenamento dos Dados de Áudio adicionando uma cópia dos dados de áudio de entrada (indata.copy) ao final de uma lista .
        
        with sd.InputStream( #brir um stream de entrada de áudio,
            samplerate=44100, # número de amostras de áudio por segundo.
            channels=2, #número de canais de áudio. 1 indica áudio mono (um único canal) e 2 indica áudio estéreo (dois canais)
            dtype='int24', #especifica o tipo de dado das amostras de áudio, como float32 ou int16
            callback=callback, #é uma função que será chamada automaticamente cada vez que o stream receber novos dados de áudio.
            ):
            self.__activate_key()
        

    #metódo que responsável pela gravação da voz do usuário
    def __start_recoding_voice(self):
        if self.is_recoding:
            self.is_recoding = False
            self.__save_audio()
            self.audio_data = []
        else:
            print("Gravando")
            self.audio_data = []
            self.is_recoding = True
        
            
            
            
    def __save_audio(self):
        print("salvando audio")       
    
    #Metódo que reconhece a tecla que foi pressionado no teclado
    def __activate_key(self):
        def on_activate():
            self.__start_recod_voice() #incia a gravação da voz ao pessionar a te

        def for_canonical(f):
            return lambda k: f(l.canonical(k))

        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>'), on_activate)
        
        with keyboard.Listener(
                on_press=for_canonical(hotkey.press),
                on_release=for_canonical(hotkey.release)) as l:
            l.join()
                
        
    