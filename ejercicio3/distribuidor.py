import socket
import pickle
import struct
import zlib
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
import threading
import sys
import time


B_GLOBAL = None
HILOS_GLOBAL = 1


def leer_matriz(nombre):

    matriz = []

    with open(nombre, "r") as archivo:

        for linea in archivo:

            fila = list(
                map(int, linea.split())
            )

            matriz.append(fila)

    return matriz


def guardar_matriz(nombre, matriz):

    with open(nombre, "w") as archivo:

        for fila in matriz:

            archivo.write(
                " ".join(map(str, fila))
                + "\n"
            )


def recibir_exacto(sock, cantidad):

    datos = b""

    while len(datos) < cantidad:

        paquete = sock.recv(
            cantidad - len(datos)
        )

        if not paquete:
            return None

        datos += paquete

    return datos


def enviar_datos(sock, objeto):

    datos = pickle.dumps(
        objeto,
        protocol=pickle.HIGHEST_PROTOCOL
    )

    datos = zlib.compress(datos)

    sock.sendall(
        struct.pack("!Q", len(datos))
    )

    sock.sendall(datos)


def recibir_datos(sock):

    encabezado = recibir_exacto(sock, 8)

    if not encabezado:
        return None

    tamano = struct.unpack(
        "!Q",
        encabezado
    )[0]

    datos = recibir_exacto(
        sock,
        tamano
    )

    datos = zlib.decompress(datos)

    return pickle.loads(datos)


def calcular_fila(datos):

    indice, fila_a = datos

    n = len(B_GLOBAL)

    fila_c = [0] * n


    for j in range(n):

        suma = 0

        for k in range(n):

            suma += (
                fila_a[k]
                * B_GLOBAL[k][j]
            )

        fila_c[j] = suma


    return indice, fila_c


def calcular_bloque(bloque):

    with ThreadPoolExecutor(
        max_workers=HILOS_GLOBAL
    ) as executor:

        resultado = list(
            executor.map(
                calcular_fila,
                bloque
            )
        )

    return resultado


def dividir_lista(lista, partes):

    if partes <= 0:

        partes = 1


    partes = min(
        partes,
        len(lista)
    )


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


        bloques.append(
            lista[inicio:fin]
        )


        inicio = fin


    return bloques


def calcular_local(
    filas,
    B,
    procesos,
    hilos
):

    global B_GLOBAL
    global HILOS_GLOBAL


    B_GLOBAL = B

    HILOS_GLOBAL = hilos


    if not filas:

        return []


    procesos = min(
        procesos,
        len(filas)
    )


    bloques = dividir_lista(
        filas,
        procesos
    )


    contexto = mp.get_context(
        "fork"
    )


    with contexto.Pool(
        processes=procesos
    ) as pool:

        resultados = pool.map(
            calcular_bloque,
            bloques
        )


    final = []


    for bloque in resultados:

        final.extend(bloque)


    return final


def enviar_trabajo(
    ip,
    puerto,
    filas,
    B,
    procesos,
    hilos,
    resultados_remotos,
    posicion
):

    print(
        f"Conectando con "
        f"{ip}:{puerto}"
    )


    cliente = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )


    try:

        cliente.connect(
            (ip, puerto)
        )


        mensaje = {

            "filas": filas,

            "B": B,

            "procesos": procesos,

            "hilos": hilos

        }


        enviar_datos(
            cliente,
            mensaje
        )


        respuesta = recibir_datos(
            cliente
        )


        resultados_remotos[posicion] = (
            respuesta["filas"]
        )


        print(
            f"\nPC {ip} terminó."
        )

        print(
            f"Tiempo interno remoto: "
            f"{respuesta['tiempo']:.6f} s"
        )


    except Exception as e:

        print(
            f"Error con {ip}:{puerto}:",
            e
        )


        resultados_remotos[posicion] = []


    finally:

        cliente.close()


def main():

    if len(sys.argv) < 7:

        print("Uso:")

        print(
            "python3 distribuidor.py "
            "A.txt B.txt C.txt "
            "PROCESOS HILOS "
            "IP:PUERTO"
        )

        print()

        print("Ejemplo:")

        print(
            "python3 distribuidor.py "
            "A.txt B.txt C.txt "
            "4 2 "
            "192.168.1.20:5000"
        )

        return


    archivoA = sys.argv[1]

    archivoB = sys.argv[2]

    archivoC = sys.argv[3]


    procesos = int(
        sys.argv[4]
    )

    hilos = int(
        sys.argv[5]
    )


    trabajadores = sys.argv[6:]


    print(
        "Cargando matrices..."
    )


    A = leer_matriz(
        archivoA
    )

    B = leer_matriz(
        archivoB
    )


    n = len(A)


    if (
        len(B) != n
        or any(len(fila) != n for fila in A)
        or any(len(fila) != n for fila in B)
    ):

        print(
            "Error: las matrices deben ser NxN"
        )

        return


    print(
        f"Matriz: {n} x {n}"
    )

    print(
        "Procesos por PC:",
        procesos
    )

    print(
        "Hilos por proceso:",
        hilos
    )


    cantidad_pcs = (
        len(trabajadores) + 1
    )


    filas = list(
        enumerate(A)
    )


    bloques = dividir_lista(
        filas,
        cantidad_pcs
    )


    resultados_remotos = [
        None
    ] * len(trabajadores)


    threads_red = []


    inicio_total = time.perf_counter()


    #
    # Mandar tareas a computadores remotos
    #

    for i, trabajador in enumerate(
        trabajadores
    ):

        ip, puerto = (
            trabajador.split(":")
        )


        hilo = threading.Thread(
            target=enviar_trabajo,
            args=(
                ip,
                int(puerto),
                bloques[i + 1],
                B,
                procesos,
                hilos,
                resultados_remotos,
                i
            )
        )


        hilo.start()

        threads_red.append(hilo)


    #
    # El coordinador calcula su propio bloque
    #

    print(
        "\nPC coordinador calculando",
        len(bloques[0]),
        "filas..."
    )


    inicio_local = time.perf_counter()


    resultado_local = calcular_local(
        bloques[0],
        B,
        procesos,
        hilos
    )


    fin_local = time.perf_counter()


    print(
        f"Tiempo local: "
        f"{fin_local - inicio_local:.6f} s"
    )


    #
    # Esperar computadores remotos
    #

    for hilo in threads_red:

        hilo.join()


    #
    # Consolidar resultados
    #

    resultados = []

    resultados.extend(
        resultado_local
    )


    for resultado in resultados_remotos:

        if resultado:

            resultados.extend(
                resultado
            )


    #
    # Ordenar nuevamente las filas
    #

    resultados.sort(
        key=lambda x: x[0]
    )


    C = [
        fila
        for indice, fila
        in resultados
    ]


    fin_total = time.perf_counter()


    if len(C) != n:

        print(
            "ERROR: faltan filas en "
            "el resultado."
        )

        print(
            "Esperadas:",
            n
        )

        print(
            "Obtenidas:",
            len(C)
        )

        return


    guardar_matriz(
        archivoC,
        C
    )


    print()

    print(
        "================================"
    )

    print(
        "RESULTADO"
    )

    print(
        "================================"
    )

    print(
        "Matriz guardada en:",
        archivoC
    )

    print(
        f"Tiempo distribuido total: "
        f"{fin_total - inicio_total:.6f} segundos"
    )

    print(
        "================================"
    )


if __name__ == "__main__":

    mp.freeze_support()

    main()
