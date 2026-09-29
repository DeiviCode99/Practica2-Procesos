import sys
import time
import multiprocessing
from concurrent.futures import ThreadPoolExecutor


A_GLOBAL = None
B_GLOBAL = None
N_GLOBAL = 0


def leer_matriz(nombre_archivo):
    matriz = []

    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            if linea.strip():
                fila = list(map(int, linea.split()))
                matriz.append(fila)

    return matriz


def guardar_matriz(matriz, nombre_archivo):
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        for fila in matriz:
            archivo.write(" ".join(map(str, fila)) + "\n")


def validar_dimensiones(A, B):
    if not A or not B:
        return False

    n = len(A)

    if len(B) != n:
        return False

    for fila in A:
        if len(fila) != n:
            return False

    for fila in B:
        if len(fila) != n:
            return False

    return True


def inicializar_proceso(A, B):
    global A_GLOBAL, B_GLOBAL, N_GLOBAL

    A_GLOBAL = A
    B_GLOBAL = B
    N_GLOBAL = len(A)


def calcular_fila(i):
    fila_resultado = [0] * N_GLOBAL

    for j in range(N_GLOBAL):

        suma = 0

        for k in range(N_GLOBAL):
            suma += A_GLOBAL[i][k] * B_GLOBAL[k][j]

        fila_resultado[j] = suma

    return i, fila_resultado


def trabajo_proceso(datos):
    filas, numero_hilos = datos

    resultados = []

    if numero_hilos == 1:

        for fila in filas:
            resultados.append(calcular_fila(fila))

    else:

        with ThreadPoolExecutor(max_workers=numero_hilos) as executor:
            resultados = list(
                executor.map(calcular_fila, filas)
            )

    return resultados


def dividir_filas(n, numero_procesos):
    grupos = [[] for _ in range(numero_procesos)]

    for i in range(n):
        grupos[i % numero_procesos].append(i)

    return grupos


def multiplicar_paralelo(A, B, numero_procesos, numero_hilos):

    n = len(A)

    grupos = dividir_filas(n, numero_procesos)

    trabajos = []

    for grupo in grupos:
        if grupo:
            trabajos.append((grupo, numero_hilos))

    with multiprocessing.Pool(
        processes=numero_procesos,
        initializer=inicializar_proceso,
        initargs=(A, B)
    ) as pool:

        resultados_procesos = pool.map(
            trabajo_proceso,
            trabajos
        )

    C = [[0] * n for _ in range(n)]

    for resultado_proceso in resultados_procesos:

        for numero_fila, fila in resultado_proceso:
            C[numero_fila] = fila

    return C


def main():

    if len(sys.argv) != 6:

        print("Uso:")
        print(
            "python3 multiplicadorParalelo.py "
            "A.txt B.txt C.txt procesos hilos"
        )

        print("\nEjemplo:")
        print(
            "python3 multiplicadorParalelo.py "
            "A.txt B.txt C.txt 4 2"
        )

        return

    archivo_A = sys.argv[1]
    archivo_B = sys.argv[2]
    archivo_C = sys.argv[3]

    numero_procesos = int(sys.argv[4])
    numero_hilos = int(sys.argv[5])

    print("\n--- Multiplicación paralela de matrices ---")

    print(f"Procesos: {numero_procesos}")
    print(f"Hilos por proceso: {numero_hilos}")

    A = leer_matriz(archivo_A)
    B = leer_matriz(archivo_B)

    if not validar_dimensiones(A, B):

        print(
            "Error: las matrices deben ser "
            "cuadradas NxN y tener el mismo tamaño."
        )

        return

    n = len(A)

    print(f"Tamaño de las matrices: {n}x{n}")

    inicio = time.perf_counter()

    C = multiplicar_paralelo(
        A,
        B,
        numero_procesos,
        numero_hilos
    )

    fin = time.perf_counter()

    tiempo = fin - inicio

    guardar_matriz(C, archivo_C)

    print("\nMultiplicación terminada.")
    print(f"Tiempo: {tiempo:.6f} segundos")
    print(f"Resultado guardado en: {archivo_C}")

    print(
        f"Configuración utilizada: "
        f"P{numero_procesos}T{numero_hilos}"
    )


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
