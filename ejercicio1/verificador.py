"""
Verificador de multiplicación de matrices (algoritmo de Freivalds).

Busca los archivos .txt que están en la misma carpeta que este script y
permite elegir:
  - la matriz A
  - la matriz B
  - la matriz C (el resultado que se quiere verificar), o calcularla con
    la función `mi_multiplicacion` definida abajo.

Formato de los .txt: una fila de la matriz por línea, con los valores
separados por espacios, tabulaciones, comas o punto y coma. Ejemplo:
    1 2 3
    4 5 6
"""

import os
import sys
import time
import numpy as np

CARPETA = os.path.dirname(os.path.abspath(__file__))


# ----------------------------------------------------------------------
# Tu función de multiplicación: reemplaza el cuerpo con tu implementación
# ----------------------------------------------------------------------
def mi_multiplicacion(A, B):
    m, p = A.shape
    _, q = B.shape
    C = np.zeros((m, q))
    for i in range(m):
        for k in range(p):
            C[i, :] += A[i, k] * B[k, :]
    return C


# ----------------------------------------------------------------------
# Verificación de Freivalds
# ----------------------------------------------------------------------
def freivalds(A, B, C, k=20, rtol=1e-9, atol=1e-9):
    """Devuelve (True, None) si C = A·B con prob. >= 1 - 2^-k.
    Devuelve (False, filas) si C != A·B con certeza; `filas` son las filas con error."""
    q = C.shape[1]
    for _ in range(k):
        r = np.random.randint(0, 2, size=(q, 1))
        izq = A @ (B @ r)      # O(n²): nunca se calcula A·B completo
        der = C @ r
        if not np.allclose(izq, der, rtol=rtol, atol=atol):
            dif = np.abs(izq - der).ravel()
            filas = np.where(dif > atol + rtol * np.abs(der).ravel())[0]
            return False, filas
    return True, None


# ----------------------------------------------------------------------
# Lectura de archivos
# ----------------------------------------------------------------------
def listar_txt():
    return sorted(f for f in os.listdir(CARPETA) if f.lower().endswith(".txt"))


def cargar_matriz(nombre):
    ruta = os.path.join(CARPETA, nombre)
    with open(ruta, encoding="utf-8") as fh:
        texto = fh.read()
    for sep in [";", ",", "\t"]:
        texto = texto.replace(sep, " ")
    filas = [linea.split() for linea in texto.splitlines() if linea.strip()]
    if not filas:
        raise ValueError(f"'{nombre}' está vacío.")
    ancho = len(filas[0])
    for i, fila in enumerate(filas, 1):
        if len(fila) != ancho:
            raise ValueError(f"'{nombre}': la fila {i} tiene {len(fila)} valores "
                             f"y la primera tiene {ancho}.")
    return np.array(filas, dtype=float)


def elegir_archivo(archivos, mensaje, permitir_calcular=False):
    print(f"\n{mensaje}")
    for i, f in enumerate(archivos, 1):
        print(f"  {i}. {f}")
    if permitir_calcular:
        print("  0. Calcular C con mi_multiplicacion(A, B)")
    while True:
        op = input("Elige un número: ").strip()
        if op.isdigit():
            n = int(op)
            if permitir_calcular and n == 0:
                return None
            if 1 <= n <= len(archivos):
                return archivos[n - 1]
        print("  Opción no válida, intenta de nuevo.")


def cargar_con_reintento(archivos, mensaje, permitir_calcular=False):
    while True:
        nombre = elegir_archivo(archivos, mensaje, permitir_calcular)
        if nombre is None:
            return None, None
        try:
            M = cargar_matriz(nombre)
            print(f"  -> {nombre}: {M.shape[0]}×{M.shape[1]}")
            return nombre, M
        except ValueError as e:
            print(f"  Error al leer: {e}")


# ----------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------
def main():
    archivos = listar_txt()
    print(f"Carpeta: {CARPETA}")
    if not archivos:
        print("No hay archivos .txt en esta carpeta.")
        sys.exit(1)

    while True:
        _, A = cargar_con_reintento(archivos, "Selecciona la matriz A:")
        _, B = cargar_con_reintento(archivos, "Selecciona la matriz B:")
        if A.shape[1] != B.shape[0]:
            print(f"\nNo se pueden multiplicar: A es {A.shape[0]}×{A.shape[1]} "
                  f"y B es {B.shape[0]}×{B.shape[1]} (las columnas de A deben "
                  f"coincidir con las filas de B).")
        else:
            nombre_c, C = cargar_con_reintento(
                archivos, "Selecciona la matriz resultado C a verificar:",
                permitir_calcular=True)
            if C is None:
                t0 = time.perf_counter()
                C = mi_multiplicacion(A, B)
                print(f"  -> C calculada con mi_multiplicacion en "
                      f"{time.perf_counter() - t0:.3f} s")

            esperado = (A.shape[0], B.shape[1])
            if C.shape != esperado:
                print(f"\nINCORRECTA: C es {C.shape[0]}×{C.shape[1]}, "
                      f"pero debería ser {esperado[0]}×{esperado[1]}.")
            else:
                t0 = time.perf_counter()
                ok, filas = freivalds(A, B, C)
                dt = time.perf_counter() - t0
                if ok:
                    print(f"\nCORRECTA (probabilidad de error < 1e-6). "
                          f"Verificado en {dt:.3f} s")
                else:
                    muestra = ", ".join(str(f + 1) for f in filas[:10])
                    extra = "…" if len(filas) > 10 else ""
                    print(f"\nINCORRECTA. Filas con error detectadas: "
                          f"{muestra}{extra}")

        if input("\n¿Hacer otra prueba? (s/n): ").strip().lower() != "s":
            break


if __name__ == "__main__":
    main()
