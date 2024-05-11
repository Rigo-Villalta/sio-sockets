from tkinter import (
    Tk,
    Frame,
    Scrollbar,
    Label,
    END,
    Entry,
    Text,
    VERTICAL,
    Button,
    messagebox,
)  # importaciones de módulo Tkinter de Python para GUI

import socket
import threading


class InterfazGrafica:
    cliente_socket = None
    mensajes_recibidos = None

    def __init__(self, ventana_principal):
        self.raiz = ventana_principal
        self.area_transcripcion_chat = None
        self.widget_nombre = None
        self.widget_entrada_texto = None
        self.boton_unirse = None
        self.inicializar_socket()
        self.inicializar_gui()
        self.escuchar_mensajes_entrantes_en_hilo()

    def inicializar_socket(self):
        self.cliente_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )  # Inicializando socket con TCP e IPv4
        ip_remota = "49.13.31.130"  # Dirección IP
        puerto_remoto = 9857
        self.cliente_socket.connect(
            (ip_remota, puerto_remoto)
        )  # Conectar al servidor remoto

    def inicializar_gui(self):  # Inicializador de la interfaz de usuario
        self.raiz.title("Chat de Socket SIO")
        self.raiz.resizable(0, 0)
        self.mostrar_caja_chat()
        self.mostrar_seccion_nombre()
        self.mostrar_caja_entrada_chat()

    def escuchar_mensajes_entrantes_en_hilo(self):
        # Creamos hilos para que varios mensajes puedan ser escuchados
        hilo = threading.Thread(
            target=self.recibir_mensaje_desde_servidor, args=(self.cliente_socket,)
        )  # Crear un hilo para enviar y recibir al mismo tiempo
        hilo.start()

    # Función para recibir mensaje
    def recibir_mensaje_desde_servidor(self, so):
        while True:
            buffer = so.recv(256)
            if not buffer:
                break
            mensaje = buffer.decode("utf-8")

            if "joined" in mensaje:
                usuario = mensaje.split(":")[1]
                mensaje = usuario + " se ha unido"
                self.area_transcripcion_chat.insert("end", mensaje + "\n")
                self.area_transcripcion_chat.yview(END)
            else:
                self.area_transcripcion_chat.insert("end", mensaje + "\n")
                self.area_transcripcion_chat.yview(END)

        so.close()

    def mostrar_seccion_nombre(self):
        frame = Frame()
        Label(frame, text="Ingrese su nombre:", font=("Helvetica", 16)).pack(
            side="left", padx=10
        )
        self.widget_nombre = Entry(frame, width=50, borderwidth=2)
        self.widget_nombre.pack(side="left", anchor="e")
        self.boton_unirse = Button(
            frame, text="Unirse", width=10, command=self.al_unirse
        ).pack(side="left")
        frame.pack(side="top", anchor="nw")

    def mostrar_caja_chat(self):
        frame = Frame()
        Label(frame, text="Ventana de conversación:", font=("Serif", 12)).pack(
            side="top", anchor="w"
        )
        self.area_transcripcion_chat = Text(
            frame, width=60, height=10, font=("Serif", 12)
        )
        scrollbar = Scrollbar(
            frame, command=self.area_transcripcion_chat.yview, orient=VERTICAL
        )
        self.area_transcripcion_chat.config(yscrollcommand=scrollbar.set)
        self.area_transcripcion_chat.bind("<KeyPress>", lambda e: "break")
        self.area_transcripcion_chat.pack(side="left", padx=10)
        scrollbar.pack(side="right", fill="y")
        frame.pack(side="top")

    def mostrar_caja_entrada_chat(self):
        frame = Frame()
        Label(frame, text="Ingrese mensaje:", font=("Serif", 12)).pack(
            side="top", anchor="w"
        )
        self.widget_entrada_texto = Text(frame, width=60, height=3, font=("Serif", 12))
        self.widget_entrada_texto.pack(side="left", pady=15)
        self.widget_entrada_texto.bind("<Return>", self.al_presionar_tecla_enter)
        frame.pack(side="top")

    def al_unirse(self):
        if len(self.widget_nombre.get()) == 0:
            messagebox.showerror(
                "Ingrese su nombre", "Ingrese su nombre para enviar un mensaje"
            )
            return
        self.widget_nombre.config(state="disabled")
        self.cliente_socket.send(("joined:" + self.widget_nombre.get()).encode("utf-8"))

    def al_presionar_tecla_enter(self, evento):
        if len(self.widget_nombre.get()) == 0:
            messagebox.showerror(
                "Ingrese su nombre", "Ingrese su nombre para enviar un mensaje"
            )
            return
        self.enviar_chat()
        self.limpiar_texto()

    def limpiar_texto(self):
        self.widget_entrada_texto.delete(1.0, "end")

    def enviar_chat(self):
        nombre_remitente = self.widget_nombre.get().strip() + ": "
        datos = self.widget_entrada_texto.get(1.0, "end").strip()
        mensaje = (nombre_remitente + datos).encode("utf-8")
        self.area_transcripcion_chat.insert("end", mensaje.decode("utf-8") + "\n")
        self.area_transcripcion_chat.yview(END)
        self.cliente_socket.send(mensaje)
        self.widget_entrada_texto.delete(1.0, "end")
        return "break"

    def al_cerrar_ventana(self):
        if messagebox.askokcancel("Salir", "¿Desea salir del chat SIO?"):
            self.raiz.destroy()
            self.cliente_socket.close()
            exit(0)


# Función principal
if __name__ == "__main__":
    root = Tk()
    gui = InterfazGrafica(root)
    root.protocol("WM_DELETE_WINDOW", gui.al_cerrar_ventana)
    root.mainloop()
