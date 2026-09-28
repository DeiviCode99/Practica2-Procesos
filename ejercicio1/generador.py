import random
import sys
import time

def generar_y_guardar_matriz():
    print("--- Generador de Matrices Cuadradas ---")
    
    try:
        n = None
        nombre_archivo = None

        # 1. Analizar argumentos desde la terminal sin importar el orden o formato
        if len(sys.argv) >= 3:
            # Si pasaron dos argumentos o más, revisamos cuáles son el número y cuál es el archivo
            args = sys.argv[1:]
            for arg in args:
                try:
                    # Intentamos convertir el argumento a número entero
                    if n is None:
                        n = int(arg)
                    else:
                        nombre_archivo = arg
                except ValueError:
                    # Si no es un número entero, asumimos que es el nombre del archivo
                    nombre_archivo = arg
        elif len(sys.argv) == 2:
            # Si pasaron un solo argumento combinado (ej. 100A.txt o A100.txt)
            argumento = sys.argv[1].strip()
            # Extraemos todos los dígitos que formen el número de tamaño
            partes_num = "".join([c for c in argumento if c.isdigit()])
            partes_txt = "".join([c for c in argumento if not c.isdigit()])
            
            if partes_num:
                n = int(partes_num)
                nombre_archivo = partes_txt if partes_txt else f"matriz_{n}.txt"
            else:
                print("Error: No se encontró ningún número para el tamaño de la matriz.")
                sys.exit(1)
        else:
            # 2. Modo interactivo (si se ejecuta sin argumentos)
            n = int(input("Ingresa el tamaño de la matriz (ej. 100): "))
            nombre_archivo = input("Ingresa el nombre del archivo (ej. A.txt): ").strip()

        if n is None or n <= 0:
            print("Error: El tamaño de la matriz debe ser un número entero mayor que cero.")
            return

        if not nombre_archivo:
            nombre_archivo = f"matriz_{n}.txt"

        # Asegurarnos de que el archivo termine en .txt
        if not nombre_archivo.endswith('.txt'):
            nombre_archivo += '.txt'

        # 3. Generar la matriz cuadrada con números aleatorios midiendo el tiempo
        inicio = time.perf_counter()
        matriz = [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]
        
        # 4. Guardar la matriz en el archivo seleccionado
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            for fila in matriz:
                linea = "\t".join(str(elemento) for elemento in fila)
                archivo.write(linea + "\n")
        
        fin = time.perf_counter()

        print(f"\n¡Éxito! Se ha generado una matriz de {n}x{n}.")
        print(f"Puedes revisarla en el archivo: '{nombre_archivo}'")
        print(f"El tiempo de ejecución fue: {fin - inicio:.6f} segundos")

    except ValueError:
        print("Error: Por favor, asegúrate de ingresar un número entero válido para el tamaño.")
        sys.exit(1)

# Punto de entrada del programa
if __name__ == "__main__":
    generar_y_guardar_matriz()
