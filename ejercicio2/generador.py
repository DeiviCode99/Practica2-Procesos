import random

def generar_y_guardar_matriz():
    print("--- Generador de Matrices Cuadradas ---")
    
    try:
        # 1. Solicitar el tamaño al usuario
        n = int(input("Ingresa el tamaño de la matriz (ej. 5 para una de 5x5): "))
        
        if n <= 0:
            print("Error: El tamaño debe ser un número entero mayor que cero.")
            return

        # 2. Solicitar el nombre del archivo al usuario
        nombre_archivo = input("Ingresa el nombre del archivo (ej. mi_matriz): ").strip()
        
        # Asegurarnos de que el archivo termine en .txt
        if not nombre_archivo.endswith('.txt'):
            nombre_archivo += '.txt'

        # 3. Generar la matriz cuadrada con números aleatorios
        matriz = [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]
        
        # 4. Guardar la matriz en el archivo seleccionado
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            for fila in matriz:
                # Une los elementos de la fila separados por un tabulador para que se vea alineado
                linea = "\t".join(str(elemento) for elemento in fila)
                archivo.write(linea + "\n")

        print(f"\n¡Éxito! Se ha generado una matriz de {n}x{n}.")
        print(f"Puedes revisarla en el archivo: '{nombre_archivo}'")

    except ValueError:
        print("Error: Por favor, ingresa únicamente un número entero válido para el tamaño.")

# Punto de entrada del programa
if __name__ == "__main__":
    generar_y_guardar_matriz()
