import os
import wave
import whisper
import numpy as np
from pynput import keyboard
import sounddevice as sd #classe que ornece funcionalidades para manipulação de áudio



class Voice:
    def __init__(self):
        self.is_recoding = False
        self.channels = 2
        self.samplerate = 44100
        self.dtype = 'int16'
        self.audio_data = [],
        self.whisper =  whisper.load_model("base")
        
        
    def run(self):
        #configurações de audio
        def callback(indata, frame_count, time_info, status):
            if self.is_recoding: #verifica se a gravação foi inicializada
              self.audio_data.extend(indata.copy()) #Armazenamento dos Dados de Áudio adicionando uma cópia dos dados de áudio de entrada (indata.copy) ao final de uma lista .
        
        with sd.InputStream( #brir um stream de entrada de áudio,
            samplerate=self.samplerate, # número de amostras de áudio por segundo.
            channels=self.channels, #número de canais de áudio. 1 indica áudio mono (um único canal) e 2 indica áudio estéreo (dois canais)
            dtype=self.dtype, #especifica o tipo de dado das amostras de áudio, como float32 ou int16
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
     
    #metodo que salva o audio         
    def __save_audio(self):
        print("salvando audio")  
        if "temp.wav" in os.listdir():#verifica se há
            os.remove("temp.wav") #remove o arquivo de audio
            
        #gravando audio em um arquivo .wav   
        wav_file = wave.open("test.wav", 'wb') #criando arquivo de audio
        wav_file.setnchannels(self.channels) #Define o número de canais do áudio
        wav_file.setsampwidth(2) #Define a largura das amostras de áudio em bytes. Aqui, 2 significa que cada amostra ocupa 2 bytes (16 bits), 
        wav_file.setframerate(self.samplerate) #Define a taxa de amostragem do áudio (em Hz),
        wav_file.writeframes(np.array(self.audio_data, dtype=self.dtype)) #Escreve os dados de áudio no arquivo .wav
        wav_file.close() #Fecha o arquivo, garantindo que todas as informações foram salvas corretamente no disco.
        
        #convertendo audio para texto
        result = self.whisper.transcribe("test.wav", fp16=False)
        print(f'Usuário {result["text"]}')
        return result["text"]
    
    
    #Metódo que reconhece a tecla que foi pressionado no teclado
    def __activate_key(self):
        def on_activate():
            self.__start_recoding_voice() #incia a gravação da voz ao pessionar a te

        def for_canonical(f):
            return lambda k: f(l.canonical(k))

        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<alt>'), on_activate)
        
        with keyboard.Listener(
                on_press=for_canonical(hotkey.press),
                on_release=for_canonical(hotkey.release)) as l:
            l.join()
                
        
    