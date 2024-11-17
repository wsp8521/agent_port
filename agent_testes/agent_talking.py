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
        #self.create_agent()
        self.voice = voice

    def start_or_stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.save_and_transcribe()
            self.audio_data = []
        else:
            print("Pergunta (fale agora):")
            self.audio_data = []
            self.is_recording = True

    def create_agent(self):
        agent_prompt_prefix = """
             Você é um assistente amigável.
             Se a resposta incluir o nome de um navio, retorne primeiramente o nome do navio.
             Se houver um valor numérico associado, formate-o no padrão brasileiro, onde os milhares são separados por pontos e as casas decimais por vírgula.
             Use a unidade de medida "tonelada" quando se referir à quantidade de movimentação.
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
        print("Analisando...")
        if "temp.wav" in os.listdir():
            os.remove("temp.wav")
        wav_file = wave.open("test.wav", 'wb')
        wav_file.setnchannels(self.channels)
        wav_file.setsampwidth(2)
        wav_file.setframerate(self.samplerate)
        wav_file.writeframes(np.array(self.audio_data, dtype=self.dtype))
        wav_file.close()

        result = self.whisper.transcribe("test.wav", fp16=False)
        print("Usuário:", result["text"])

        # Atualizando o histórico da memória
        self.memory.save_context({"input": result["text"]}, {"output": ""})
        response = self.agent.invoke(result["text"])
        self.memory.save_context({"input": result["text"]}, {"output": response["output"]})

        print("AI:", response["output"])
        self.llm_queue.put(response["output"])

    def run_voice_mode(self):
        def callback(indata, frame_count, time_info, status):
            if self.is_recording:
                self.audio_data.extend(indata.copy())

        with sd.InputStream(samplerate=self.samplerate,
                            channels=self.channels,
                            dtype=self.dtype,
                            callback=callback):
            print("Pressione 'Alt' para gravar sua pergunta ou 'Esc' para sair.")
            def on_press(key):
                if key == keyboard.Key.esc:
                    print("ESC pressionado! Saindo do programa...")
                    os._exit(0)  # Encerra todo o programa
                if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                    self.start_or_stop_recording()

            with keyboard.Listener(on_press=on_press) as listener:
                listener.join()

    def run_text_mode(self):
        print("Digite sua pergunta abaixo (ou 'sair' para encerrar):")
        while True:
            user_input = input("Usuário: ")
            if user_input.lower() == "sair":
                print("Encerrando o programa...")
                os._exit(0)  # Encerra todo o programa
            # Atualizando a memória e processando a resposta
            self.memory.save_context({"input": user_input}, {"output": ""})
            response = self.agent.invoke(user_input)
            self.memory.save_context({"input": user_input}, {"output": response["output"]})
            print("AI:", response["output"])

    def run(self):
        while True:
            print("Escolha o modo de interação:")
            print("1. Digitar perguntas")
            print("2. Falar perguntas (usar microfone)")
            print("3. Sair")
            choice = input("Digite 1, 2 ou 3: ").strip()

            if choice == "1":
                self.run_text_mode()
            elif choice == "2":
                self.run_voice_mode()
            elif choice == "3":
                print("Encerrando o programa...")
                os._exit(0)  # Encerra todo o programa
            else:
                print("Escolha inválida. Tente novamente.")