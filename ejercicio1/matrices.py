import os
import time

def listar_archivos_txt():
    """Busca y devuelve una lista de archivos .txt en el directorio actual."""
    archivos = [archivo for archivo in os.listdir('.') if archivo.endswith('.txt')]
    return archivos

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

def multiplicar_matrices(A, B):
    """Realiza la multiplicación iterando elemento por elemento con una pausa de 1 segundo."""
    filas_A = len(A)
    columnas_A = len(A[0])
    filas_B = len(B)
    columnas_B = len(B[0])

    if columnas_A != filas_B:
        print(f"Error: No se pueden multiplicar. La matriz A tiene {columnas_A} columnas y la matriz B tiene {filas_B} filas.")
        return None

    resultado = [[0 for _ in range(columnas_B)] for _ in range(filas_A)]

    print("\nIniciando el cálculo elemento por elemento...")
    
    # Proceso de multiplicación
    for i in range(filas_A):
        for j in range(columnas_B):
            # Calculamos el valor del elemento en la posición (i, j)
            for k in range(columnas_A):
                resultado[i][j] += A[i][k] * B[k][j]
            
            # Imprimir la posición y el valor calculado (sumamos 1 a los índices para que sea más legible)
            print(f"Elemento en posición (Fila {i + 1}, Columna {j + 1}) calculado -> Valor: {resultado[i][j]}")
            
            # Pausa de 1 segundo antes de calcular el siguiente elemento
            time.sleep(1)

    return resultado

def guardar_matriz(matriz, nombre_archivo):
    """Guarda la matriz resultante en un archivo de texto."""
    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        for fila in matriz:
            linea = "\t".join(str(elemento) for elemento in fila)
            archivo.write(linea + "\n")
    print(f"\n¡Éxito! El resultado final se ha guardado en '{nombre_archivo}'")

def main():
    print("--- Multiplicador de Matrices Paso a Paso ---")
    archivos_txt = listar_archivos_txt()

    if len(archivos_txt) < 2:
        print("Error: Necesitas al menos dos archivos .txt en esta carpeta para hacer la multiplicación.")
        return

    print("\nArchivos disponibles:")
    for i, archivo in enumerate(archivos_txt):
        print(f"[{i + 1}] {archivo}")

    try:
        seleccion1 = int(input("\nElige el número del PRIMER archivo (Matriz A): ")) - 1
        seleccion2 = int(input("Elige el número del SEGUNDO archivo (Matriz B): ")) - 1

        if seleccion1 < 0 or seleccion2 < 0 or seleccion1 >= len(archivos_txt) or seleccion2 >= len(archivos_txt):
            print("Error: Selección fuera de rango.")
            return

        archivo1 = archivos_txt[seleccion1]
        archivo2 = archivos_txt[seleccion2]

        print(f"\nCargando '{archivo1}' y '{archivo2}'...")
        
        matriz_A = leer_matriz(archivo1)
        matriz_B = leer_matriz(archivo2)

        if not matriz_A or not matriz_B:
            return

        matriz_resultado = multiplicar_matrices(matriz_A, matriz_B)

        if matriz_resultado:
            print("\nResultado final de la multiplicación:")
            for fila in matriz_resultado:
                print("\t".join(str(x) for x in fila))
            
            nombre_salida = input("\nIngresa el nombre con el que deseas guardar el resultado (ej. mi_resultado): ").strip()
            
            if not nombre_salida.endswith('.txt'):
                nombre_salida += '.txt'
            
            guardar_matriz(matriz_resultado, nombre_salida)

    except ValueError:
        print("Error: Por favor ingresa un dato válido.")

if __name__ == "__main__":
    main()
