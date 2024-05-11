import socket
import threading

class ServidorChat:

    lista_clientes = []
    ultimo_mensaje_recibido = ""

    def __init__(self):
        self.socket_servidor = None
        self.crear_servidor_escucha()

    # Escuchar conexiones entrantes
    def crear_servidor_escucha(self):
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        puerto_local = 9857

        # Esto te permitirá reiniciar inmediatamente un servidor TCP
        self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Esto hace que el servidor escuche las solicitudes de otras computadoras en la red
        self.socket_servidor.bind(("", puerto_local))

        print("Escuchando mensajes entrantes...")
        self.socket_servidor.listen(5)  # Escuchar conexiones entrantes / máximo 5 clientes
        self.recibir_mensajes_en_nuevo_hilo()

    # Función para recibir nuevos mensajes
    def recibir_mensajes(self, so):
        while True:
            buffer_entrante = so.recv(256)  # Inicializar el buffer
            if not buffer_entrante:
                break
            self.ultimo_mensaje_recibido = buffer_entrante.decode('utf-8')
            self.transmitir_a_todos_clientes(so)  # Enviar a todos los clientes
        so.close()

    # Transmitir el mensaje a todos los clientes
    def transmitir_a_todos_clientes(self, socket_remitente):
        for cliente in self.lista_clientes:
            socket, (ip, puerto) = cliente
            if socket is not socket_remitente:
                socket.sendall(self.ultimo_mensaje_recibido.encode('utf-8'))

    def recibir_mensajes_en_nuevo_hilo(self):
        while True:
            cliente = so, (ip, puerto) = self.socket_servidor.accept()
            self.agregar_a_lista_clientes(cliente)
            print('Conectado a ', ip, ':', str(puerto))
            t = threading.Thread(target=self.recibir_mensajes, args=(so,))
            t.start()

    # Agregar un nuevo cliente
    def agregar_a_lista_clientes(self, cliente):
        if cliente not in self.lista_clientes:
            self.lista_clientes.append(cliente)

if __name__ == "__main__":
    ServidorChat()