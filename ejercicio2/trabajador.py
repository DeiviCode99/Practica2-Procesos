import socket
import pickle
import struct
import zlib
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
import sys
import time


B_GLOBAL = None
HILOS_GLOBAL = 1


def recibir_datos(sock):
    encabezado = recibir_exacto(sock, 8)

    if not encabezado:
        return None

    tamano = struct.unpack("!Q", encabezado)[0]

    datos = recibir_exacto(sock, tamano)

    datos = zlib.decompress(datos)

    return pickle.loads(datos)


def recibir_exacto(sock, cantidad):
    datos = b""

    while len(datos) < cantidad:
        paquete = sock.recv(cantidad - len(datos))

        if not paquete:
            return None

        datos += paquete

    return datos


def enviar_datos(sock, objeto):
    datos = pickle.dumps(objeto, protocol=pickle.HIGHEST_PROTOCOL)

    datos = zlib.compress(datos)

    sock.sendall(struct.pack("!Q", len(datos)))

    sock.sendall(datos)


def calcular_fila(datos):
    indice, fila_a = datos

    n = len(B_GLOBAL)

    fila_c = [0] * n

    for j in range(n):

        suma = 0

        for k in range(n):

            suma += fila_a[k] * B_GLOBAL[k][j]

        fila_c[j] = suma

    return indice, fila_c


def calcular_bloque(bloque):
    with ThreadPoolExecutor(max_workers=HILOS_GLOBAL) as executor:

        resultado = list(
            executor.map(calcular_fila, bloque)
        )

    return resultado


def dividir_lista(lista, partes):

    if partes <= 0:
        partes = 1

    partes = min(partes, len(lista))

    if partes == 0:
        return []

    base = len(lista) // partes

    resto = len(lista) % partes

    bloques = []

    inicio = 0

    for i in range(partes):

        cantidad = base

        if i < resto:
            cantidad += 1

        fin = inicio + cantidad

        bloques.append(lista[inicio:fin])

        inicio = fin

    return bloques


def calcular_paralelo(filas, B, procesos, hilos):

    global B_GLOBAL
    global HILOS_GLOBAL

    B_GLOBAL = B

    HILOS_GLOBAL = hilos

    if not filas:
        return []

    procesos = min(procesos, len(filas))

    bloques = dividir_lista(filas, procesos)

    contexto = mp.get_context("fork")

    with contexto.Pool(processes=procesos) as pool:

        resultados = pool.map(
            calcular_bloque,
            bloques
        )

    final = []

    for bloque in resultados:

        final.extend(bloque)

    return final


def main():

    if len(sys.argv) != 3:

        print(
            "Uso: python3 trabajador.py IP PUERTO"
        )

        print(
            "Ejemplo:"
        )

        print(
            "python3 trabajador.py 0.0.0.0 5000"
        )

        return


    ip = sys.argv[1]

    puerto = int(sys.argv[2])


    servidor = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    servidor.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    servidor.bind(
        (ip, puerto)
    )

    servidor.listen(5)


    print("--------------------------------")
    print("PC TRABAJADOR")
    print("--------------------------------")

    print(
        f"Escuchando en {ip}:{puerto}"
    )

    print(
        "Esperando tareas..."
    )


    while True:

        conexion, direccion = servidor.accept()

        print(
            "\nConexión recibida desde:",
            direccion
        )

        try:

            datos = recibir_datos(conexion)

            filas = datos["filas"]

            B = datos["B"]

            procesos = datos["procesos"]

            hilos = datos["hilos"]


            print(
                "Filas recibidas:",
                len(filas)
            )

            print(
                "Procesos:",
                procesos
            )

            print(
                "Hilos por proceso:",
                hilos
            )


            inicio = time.perf_counter()


            resultado = calcular_paralelo(
                filas,
                B,
                procesos,
                hilos
            )


            fin = time.perf_counter()


            respuesta = {

                "filas": resultado,

                "tiempo": fin - inicio

            }


            enviar_datos(
                conexion,
                respuesta
            )


            print(
                f"Cálculo terminado en "
                f"{fin - inicio:.6f} segundos"
            )


        except Exception as e:

            print(
                "Error:",
                e
            )


        finally:

            conexion.close()


if __name__ == "__main__":

    mp.freeze_support()

    main()
