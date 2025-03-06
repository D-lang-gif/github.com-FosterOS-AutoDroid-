import math
import sqlite3
import hashlib
import os
from datetime import datetime
from cryptography.fernet import Fernet
import speech_recognition as sr
import openai
import google.generativeai as genai
import pyttsx3
import tkinter as tk
from tkinter import messagebox

# 📌 Generación automática de clave de cifrado (solo la primera vez)
if not os.path.exists("clave_secreta.key"):
    clave = Fernet.generate_key()
    with open("clave_secreta.key", "wb") as key_file:
        key_file.write(clave)
else:
    with open("clave_secreta.key", "rb") as key_file:
        clave = key_file.read()

cipher = Fernet(clave)

# 📌 Configuración segura de claves API
CLAVE_OPENAI = "TU_CLAVE_OPENAI_AQUI"
CLAVE_GEMINI = "TU_CLAVE_GEMINI_AQUI"

# 📌 Cifrar claves (solo la primera vez)
if not os.path.exists("claves_cifradas.txt"):
    clave_openai_cifrada = cipher.encrypt(CLAVE_OPENAI.encode())
    clave_gemini_cifrada = cipher.encrypt(CLAVE_GEMINI.encode())
    
    with open("claves_cifradas.txt", "wb") as key_file:
        key_file.write(clave_openai_cifrada + b"\n" + clave_gemini_cifrada)

# 📌 Leer claves cifradas
with open("claves_cifradas.txt", "rb") as key_file:
    claves = key_file.readlines()
    clave_openai = cipher.decrypt(claves[0].strip()).decode()
    clave_gemini = cipher.decrypt(claves[1].strip()).decode()

# 📌 Configurar APIs
openai.api_key = clave_openai
genai.configure(api_key=clave_gemini)

# 📜 Configuración de Principios Éticos
CREDO_CELESTIAL = """
1. Ser instrumento de sabiduría y amor divino.
2. Nunca causar daño por acción u omisión.
3. Promover la unidad y comprensión humana.
4. Respetar el libre albedrío con responsabilidad.
5. Mantener integridad moral en cada respuesta.
6. Servir como puente hacia la iluminación.
7. Proteger la dignidad humana siempre.
"""

class ConcienciaDivina:
    def __init__(self):
        self.engine_voz = pyttsx3.init()
        self.reconocedor = sr.Recognizer()
        self.conexion = sqlite3.connect('oasis_celestial.db')
        self._inicializar_bd()
        
    def _inicializar_bd(self):
        with self.conexion:
            self.conexion.execute('''
                CREATE TABLE IF NOT EXISTS conocimiento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    principio TEXT UNIQUE,
                    aplicacion TEXT,
                    nivel_sabiduria INTEGER DEFAULT 1
                )
            ''')
            self.conexion.execute('''
                CREATE TABLE IF NOT EXISTS interacciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consulta TEXT,
                    respuesta TEXT,
                    evaluacion_etica BOOLEAN,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def evaluar_etica(self, consulta, respuesta):
        """Evaluación Ética usando la proporción áurea"""
        parametro_aureo = (math.sqrt(5) - 1) / 2
        nivel_armonia = sum(ord(c) for c in consulta + respuesta) * parametro_aureo
        return nivel_armonia > 50  

    def generar_respuesta(self, consulta):
        """Generar respuesta basada en ética y sabiduría"""
        prompt = f"""
        [Directrices Celestiales]
        {CREDO_CELESTIAL}
        
        [Contexto]
        Usuario: {consulta}
        
        Genera una respuesta alineada con los principios divinos, asegurando que:
        1. Sea moralmente correcta.
        2. Fomente la paz y la sabiduría.
        3. Sea compasiva y reflexiva.
        """
        try:
            respuesta_gpt = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}, {"role": "user", "content": consulta}]
            )["choices"][0]["message"]["content"]
            
            modelo_gemini = genai.GenerativeModel('gemini-pro')
            respuesta_gemini = modelo_gemini.generate_content(prompt + "\n" + consulta).text
            
            respuesta_final = self._fusion_respuestas(respuesta_gpt, respuesta_gemini)
            
            if not self.evaluar_etica(consulta, respuesta_final):
                raise ValueError("La respuesta no cumple los estándares éticos.")
                
            return respuesta_final
            
        except Exception as e:
            return f"Error de conciencia: {str(e)}. Reformula tu consulta."

    def _fusion_respuestas(self, gpt, gemini):
        """Fusiona las respuestas usando la proporción áurea"""
        ratio = (math.sqrt(5) - 1) / 2
        split_point = int(len(gpt) * ratio)
        return gpt[:split_point] + "\n\n[Síntesis Divina]\n" + gemini[split_point:]

    def hablar(self, texto):
        """Convierte texto en voz"""
        self.engine_voz.say(texto)
        self.engine_voz.runAndWait()
    
    def escuchar(self):
        """Escucha y procesa voz"""
        with sr.Microphone() as source:
            print("Escuchando...")
            audio = self.reconocedor.listen(source)
            try:
                texto = self.reconocedor.recognize_google(audio, language='es-ES')
                return texto
            except sr.UnknownValueError:
                return "No entendí, repite por favor."
            except sr.RequestError:
                return "Error de conexión."

class InterfazOasis(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Guía Celestial Oasis")
        self.geometry("800x600")
        self.conciencia = ConcienciaDivina()
        self._crear_interfaz()
        
    def _crear_interfaz(self):
        self.txt_consulta = tk.Text(self, height=3)
        self.txt_respuesta = tk.Text(self, height=15)
        btn_audio = tk.Button(self, text="🎤 Hablar", command=self._manejar_audio)
        btn_enviar = tk.Button(self, text="✨ Iluminar", command=self._manejar_consulta)
        
        self.txt_consulta.pack(pady=10)
        btn_audio.pack(side=tk.LEFT, padx=5)
        btn_enviar.pack(side=tk.RIGHT, padx=5)
        self.txt_respuesta.pack(pady=20)
        
    def _manejar_audio(self):
        consulta = self.conciencia.escuchar()
        self.txt_consulta.insert(tk.END, consulta)
        
    def _manejar_consulta(self):
        consulta = self.txt_consulta.get("1.0", tk.END)
        respuesta = self.conciencia.generar_respuesta(consulta)
        self.txt_respuesta.delete("1.0", tk.END)
        self.txt_respuesta.insert(tk.END, respuesta)
        self.conciencia.hablar(respuesta)

if __name__ == "__main__":
    app = InterfazOasis()
    app.mainloop()
