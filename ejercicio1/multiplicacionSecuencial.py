import os
import sys
import time

def listar_archivos_txt():
    """Busca y devuelve una lista de archivos .txt en el directorio actual."""
    return [archivo for archivo in os.listdir('.') if archivo.endswith('.txt')]

def leer_matriz(nombre_archivo):
    """Lee un archivo .txt y lo convierte en una matriz (lista de listas)."""
    matriz = []
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                if linea.strip():
                    fila = [int(valor) for valor in linea.strip().split()]
                    matriz.append(fila)
        return matriz
    except Exception as e:
        print(f"Error al leer el archivo {nombre_archivo}: {e}")
        return None

def multiplicar_dos_matrices(A, B, tiempo_inicio):
    """Realiza la multiplicación iterando elemento por elemento con pausa y cronómetro acumulativo."""
    filas_A = len(A)
    columnas_A = len(A[0])
    filas_B = len(B)
    columnas_B = len(B[0])

    if columnas_A != filas_B:
        print(f"Error: No se pueden multiplicar. La matriz izquierda tiene {columnas_A} columnas y la matriz derecha tiene {filas_B} filas.")
        return None

    resultado = [[0 for _ in range(columnas_B)] for _ in range(filas_A)]

    print(f"\nMultiplicando matrices (Dimensiones: {filas_A}x{columnas_A} y {filas_B}x{columnas_B})...")

    # Proceso de multiplicación
    for i in range(filas_A):
        for j in range(columnas_B):
            # Calculamos el valor del elemento en la posición (i, j)
            for k in range(columnas_A):
                resultado[i][j] += A[i][k] * B[k][j]

            # Pausa de 1 segundo antes de calcular el siguiente elemento
            #time.sleep(1)

            # Calculamos el tiempo total acumulado desde el inicio del script
            tiempo_acumulado = time.perf_counter() - tiempo_inicio

            # Imprimir la posición, el valor calculado y el tiempo total acumulado
            print(f"Elemento en posición (Fila {i + 1}, Columna {j + 1}) calculado -> Valor: {resultado[i][j]} | Time: {tiempo_acumulado:.4f}s")

    return resultado

def multiplicar_secuencia(lista_matrices, tiempo_inicio):
    """Multiplica una secuencia de matrices de izquierda a derecha (A * B * C...)."""
    if not lista_matrices:
        return None
    
    acumulada = lista_matrices[0]
    for idx, siguiente_matriz in enumerate(lista_matrices[1:], start=2):
        print(f"\n--- Multiplicando resultado parcial con la matriz #{idx} ---")
        acumulada = multiplicar_dos_matrices(acumulada, siguiente_matriz, tiempo_inicio)
        if acumulada is None:
            return None
    return acumulada

def guardar_matriz(matriz, nombre_archivo):
    """Guarda la matriz resultante en un archivo de texto."""
    if not nombre_archivo.endswith('.txt'):
        nombre_archivo += '.txt'
    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        for fila in matriz:
            linea = "\t".join(str(elemento) for elemento in fila)
            archivo.write(linea + "\n")
    print(f"\n¡Éxito! El resultado final se ha guardado en '{nombre_archivo}'")

def main():
    # 1. Modo por línea de comandos (Ej: python3 multiplicadorSecuencia.py A.txt B.txt C.txt)
    if len(sys.argv) >= 4:
        nombres_entradas = sys.argv[1:-1]
        nombre_salida = sys.argv[-1]

        print("--- Multiplicador de Secuencia de Matrices ---")
        matrices = []
        for nombre in nombres_entradas:
            print(f"Cargando '{nombre}'...")
            m = leer_matriz(nombre)
            if m is None:
                sys.exit(1)
            matrices.append(m)

        # Inicio del temporizador global
        inicio = time.perf_counter()
        
        matriz_resultado = multiplicar_secuencia(matrices, inicio)
        
        fin = time.perf_counter()

        if matriz_resultado:
            guardar_matriz(matriz_resultado, nombre_salida)
            print(f"\nEl tiempo total de ejecución fue: {fin - inicio:.6f} segundos")

    # 2. Modo interactivo (si se ejecuta sin argumentos o faltan parámetros)
    else:
        print("--- Multiplicador de Matrices Paso a Paso (Modo Interactivo) ---")
        archivos_txt = listar_archivos_txt()

        if len(archivos_txt) < 2:
            print("Error: Necesitas al menos dos archivos .txt en esta carpeta para hacer la multiplicación.")
            return

        print("\nArchivos disponibles:")
        for i, archivo in enumerate(archivos_txt):
            print(f"[{i + 1}] {archivo}")

        try:
            seleccion_str = input("\nIngresa los números de los archivos a multiplicar en orden, separados por espacio (ej. 1 2 3): ")
            indices = [int(x) - 1 for x in seleccion_str.split()]

            if len(indices) < 2:
                print("Error: Debes seleccionar al menos dos archivos.")
                return

            matrices = []
            for idx in indices:
                if idx < 0 or idx >= len(archivos_txt):
                    print(f"Error: Índice {idx + 1} fuera de rango.")
                    return
                nombre_archivo = archivos_txt[idx]
                print(f"Cargando '{nombre_archivo}'...")
                m = leer_matriz(nombre_archivo)
                if m is None:
                    return
                matrices.append(m)

            inicio = time.perf_counter()
            matriz_resultado = multiplicar_secuencia(matrices, inicio)
            fin = time.perf_counter()

            if matriz_resultado:
                print("\nResultado final de la multiplicación:")
                for fila in matriz_resultado:
                    print("\t".join(str(x) for x in fila))
                
                nombre_salida = input("\nIngresa el nombre con el que deseas guardar el resultado (ej. C.txt): ").strip()
                guardar_matriz(matriz_resultado, nombre_salida)
                print(f"El tiempo total de ejecución fue: {fin - inicio:.6f} segundos")

        except ValueError:
            print("Error: Por favor ingresa un dato válido.")

if __name__ == "__main__":
    main()
