import openai
from dotenv import load_dotenv, find_dotenv
from pynput import keyboard
import sounddevice as sd
import wave
import os
import numpy as np
import whisper
from langchain_openai import OpenAI, ChatOpenAI
from queue import Queue
import io
import soundfile as sf
import threading
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import pandas as pd
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory  # Importando a memória de conversa
from utils.normalize_dataframe import normalize_date


load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('TOKEN_OPENAI')
client = openai.Client()


class AgentTalkingCarga:
    def __init__(self, model, dataframe, whisper_size="small", voice: bool = False):
        self.is_recording = False
        self.audio_data = []
        self.samplerate = 44100
        self.channels = 1
        self.dtype = 'int16'
        self.dataframe = dataframe
        self.whisper = whisper.load_model(whisper_size)
        self.llm = ChatOpenAI(model=model, max_tokens=100)

        # Inicializando a memória de conversa
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        self.llm_queue = Queue()
        self.create_agent()
        self.voice = voice

    def start_or_stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.save_and_transcribe()
            self.audio_data = []
        else:
            print("Pergunta: ")
            self.audio_data = []
            self.is_recording = True

    def create_agent(self):
        agent_prompt_prefix = """
             Você é um assistente amigável.
                Se a resposta incluir o nome de um navio, retorne primeiramente o nome do navio.
                Se houver um valor numérico associado, formate-o no padrão brasileiro, onde os milhares são separados por pontos e as casas decimais por vírgula.
                Exemplo de formatação para valores: 22,976,277.58 deve ser formatado como 22.976.277,58.
                Use a unidade de medida "tonelada" quando se referir à quantidade de movimentação.
                
                Exemplos:
                1. Qual a quantidade de movimentação?
                Resposta: 568 toneladas
                2. Qual a quantidade de movimentação de carga?
                Resposta: 568 toneladas
        """

        df = normalize_date(self.dataframe)
        self.agent = create_pandas_dataframe_agent(
            self.llm,
            df,
            prefix=agent_prompt_prefix,
            verbose=True,
            agent_type='openai-tools',
            allow_dangerous_code=True 
        )

    def save_and_transcribe(self):
        print("Analisando .")
        if "temp.wav" in os.listdir(): os.remove("temp.wav")
        wav_file = wave.open("test.wav", 'wb')
        wav_file.setnchannels(self.channels)
        wav_file.setsampwidth(2)  # Corrigido para usar a largura de amostra para int16 diretamente
        wav_file.setframerate(self.samplerate)
        wav_file.writeframes(np.array(self.audio_data, dtype=self.dtype))
        wav_file.close()

        # Gravando a voz do usuário
        result = self.whisper.transcribe("test.wav", fp16=False)
        print("Usuário:", result["text"])

        # Atualizando o histórico da memória com a transcrição da voz
        self.memory.save_context({"input": result["text"]}, {"output": ""})

        # Resposta da LLM
        response = self.agent.invoke(result["text"])

        # Atualizando o histórico da memória com a resposta do agente
        self.memory.save_context({"input": result["text"]}, {"output": response["output"]})

        print("AI:", response["output"])
        self.llm_queue.put(response["output"])

    # Voz da LLM
    def convert_and_play(self):
        tts_text = ''
        while True:
            tts_text += self.llm_queue.get()

            if '.' in tts_text or '?' in tts_text or '!' in tts_text:
                print(tts_text)

                spoken_response = client.audio.speech.create(model="tts-1",voice='alloy', response_format="opus",input=tts_text)

                buffer = io.BytesIO()
                for chunk in spoken_response.iter_bytes(chunk_size=4096):
                    buffer.write(chunk)
                buffer.seek(0)

                with sf.SoundFile(buffer, 'r') as sound_file:
                    data = sound_file.read(dtype='int16')
                    sd.play(data, sound_file.samplerate)
                    sd.wait()
                tts_text = ''

    def _run(self):
        if self.voice:
            # Executando voz da IA em paralelo 
            t1 = threading.Thread(target=self.convert_and_play) 
            t1.start()

        def callback(indata, frame_count, time_info, status):
            if self.is_recording:
                self.audio_data.extend(indata.copy())

        with sd.InputStream(samplerate=self.samplerate, 
                            channels=self.channels, 
                            dtype=self.dtype , 
                            callback=callback):
            def on_activate():
                self.start_or_stop_recording()

            def for_canonical(f):
                return lambda k: f(l.canonical(k))

            hotkey = keyboard.HotKey(
                keyboard.HotKey.parse('<alt>'),
                on_activate)
            with keyboard.Listener(
                    on_press=for_canonical(hotkey.press),
                    on_release=for_canonical(hotkey.release)) as l:
                l.join()

    def run(self):
        if self.voice:
            # Executando voz da IA em paralelo 
            t1 = threading.Thread(target=self.convert_and_play) 
            t1.start()

        def callback(indata, frame_count, time_info, status):
            if self.is_recording:
                self.audio_data.extend(indata.copy())

        # Configuração do stream de áudio
        with sd.InputStream(samplerate=self.samplerate, 
                            channels=self.channels, 
                            dtype=self.dtype , 
                            callback=callback):
            # Função para ser chamada ao pressionar 'Alt'
            def on_activate():
                self.start_or_stop_recording()

            # Função que lida com a tecla 'ESC' para sair
            def on_press(key):
                if key == keyboard.Key.esc:
                    print("ESC pressionado! Código interrompido.")
                    return False  # Interrompe o Listener e o programa

                if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                    on_activate()

            # Inicializa o Listener para detectar as teclas
            with keyboard.Listener(on_press=on_press) as listener:
                listener.join()