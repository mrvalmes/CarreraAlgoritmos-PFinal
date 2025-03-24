import time
import random
import tracemalloc
import threading
import matplotlib.pyplot as plt
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Event


class Animacion:
    def __init__(self, algoritmos):
        self.algoritmos = algoritmos
        self.progreso = {algo: 0 for algo in algoritmos}
        self.activo = True
        self.lock = Lock()
        self.terminados = set()
        self.inicio_global = time.time()
        self.evento_terminado = Event()

    def actualizar_progreso(self, algoritmo, progreso):
        with self.lock:
            self.progreso[algoritmo] = min(
                99.9, progreso
            )  # Mantener por debajo de 100% hasta terminar

    def marcar_terminado(self, algoritmo):
        with self.lock:
            self.terminados.add(algoritmo)
            self.progreso[algoritmo] = 100  # Asegurar que llegue al 100%

            # Si todos los algoritmos han terminado, notificar
            if len(self.terminados) == len(self.algoritmos):
                self.evento_terminado.set()

    def mostrar_animacion(self):
        longitud_pista = 50  # Longitud de la pista de carrera

        while self.activo:
            # Limpiar pantalla
            os.system("cls" if os.name == "nt" else "clear")

            print(f"\n{'=' * 70}")
            print(
                f"CARRERA DE ALGORITMOS - Tiempo transcurrido: {time.time() - self.inicio_global:.2f}s"
            )
            print(f"{'=' * 70}")

            # Mostrar progreso de cada algoritmo
            with self.lock:  # Proteger la lectura del progreso
                for algoritmo in self.algoritmos:
                    # Calcular cuántos asteriscos mostrar basado en el progreso
                    asteriscos = int((self.progreso[algoritmo] / 100) * longitud_pista)
                    espacios = longitud_pista - asteriscos

                    # Determinar si el algoritmo ha terminado
                    estado = (
                        "[TERMINADO]"
                        if algoritmo in self.terminados
                        else "[EJECUTANDO]"
                    )

                    # Mostrar barra de progreso
                    print(
                        f"{algoritmo.ljust(25)} {estado} |{'🏃‍♂️‍➡️' * asteriscos}{' ' * espacios}| {self.progreso[algoritmo]:.1f}%"
                    )

            print(f"{'=' * 70}")

            # Verificar si todos los algoritmos han terminado
            if len(self.terminados) == len(self.algoritmos):
                print("\n¡Todos los algoritmos han terminado!")
                self.activo = False
                break

            time.sleep(0.01)  # Actualizar cada 100ms


class AlgoritmosComparacion:
    def __init__(self, tamano_arreglo=10000, rango_valores=10000):
        self.tamano_arreglo = tamano_arreglo
        self.rango_valores = rango_valores
        self.arreglo_original = [
            random.randint(1, rango_valores) for _ in range(tamano_arreglo)
        ]
        self.resultados = {}
        self.memoria_utilizada = {}
        self.tiempos_finalizacion = {}
        self.valor_buscar = random.choice(self.arreglo_original)

        # Configurar la animacion
        self.algoritmos = [
            "Busqueda Secuencial",
            "Busqueda Binaria",
            "Ordenamiento Burbuja",
            "Quick Sort",
            "Ordenamiento por Insercion",
        ]
        self.animacion = Animacion(self.algoritmos)
        self.tiempo_inicio_global = 0

    def busqueda_binaria(self, arreglo, valor):
        nombre = "Busqueda Binaria"
        # Necesitamos un arreglo ordenado para Busqueda binaria
        arreglo_ordenado = sorted(arreglo)

        # Pequeña pausa para simular tiempo de ordenamiento
        time.sleep(0.1)

        inicio = time.time()
        tracemalloc.start()

        izquierda, derecha = 0, len(arreglo_ordenado) - 1
        encontrado = False
        indice = -1

        # Estimar el número máximo de pasos (log2(n))
        max_pasos = max(1, int(2 * (len(arreglo_ordenado)).bit_length()))

        paso_actual = 0
        while izquierda <= derecha:
            paso_actual += 1

            # Actualizar progreso
            progreso = min(99.9, (paso_actual / max_pasos) * 100)
            self.animacion.actualizar_progreso(nombre, progreso)

            medio = (izquierda + derecha) // 2
            if arreglo_ordenado[medio] == valor:
                encontrado = True
                indice = medio
                break
            elif arreglo_ordenado[medio] < valor:
                izquierda = medio + 1
            else:
                derecha = medio - 1

            # Pequeña pausa para visualizar mejor la animacion
            time.sleep(0.05)

        snapshot = tracemalloc.take_snapshot()
        memoria = sum(stat.size for stat in snapshot.statistics("lineno"))
        tracemalloc.stop()

        fin = time.time()
        tiempo = fin - inicio

        self.resultados[nombre] = tiempo
        self.memoria_utilizada[nombre] = memoria
        self.tiempos_finalizacion[nombre] = fin - self.tiempo_inicio_global

        # Asegurar que llega a 100% antes de terminar
        self.animacion.actualizar_progreso(nombre, 100)
        self.animacion.marcar_terminado(nombre)

        return encontrado, indice, tiempo, memoria

    def busqueda_secuencial(self, arreglo, valor):
        nombre = "Busqueda Secuencial"
        inicio = time.time()
        tracemalloc.start()

        encontrado = False
        indice = -1

        # Simular tiempo de procesamiento para cada elemento
        for i in range(len(arreglo)):
            # Actualizar progreso
            progreso = (i / len(arreglo)) * 100
            self.animacion.actualizar_progreso(nombre, progreso)

            # Pequeña pausa para visualizacion en arreglos pequeños
            if len(arreglo) < 1000:
                time.sleep(0.001)

            if arreglo[i] == valor:
                encontrado = True
                indice = i
                break

        snapshot = tracemalloc.take_snapshot()
        memoria = sum(stat.size for stat in snapshot.statistics("lineno"))
        tracemalloc.stop()

        fin = time.time()
        tiempo = fin - inicio

        self.resultados[nombre] = tiempo
        self.memoria_utilizada[nombre] = memoria
        self.tiempos_finalizacion[nombre] = fin - self.tiempo_inicio_global

        self.animacion.marcar_terminado(nombre)

        return encontrado, indice, tiempo, memoria

    def quick_sort(self, arreglo):
        nombre = "Quick Sort"
        inicio = time.time()
        tracemalloc.start()

        arreglo_copia = arreglo.copy()
        total_elementos = len(arreglo_copia)
        elementos_ordenados = [0]  # Lista mutable para contar elementos ordenados

        def _quick_sort(arr, inicio, fin):
            if inicio < fin:
                pivote = particionar(arr, inicio, fin)

                # Contar aproximadamente cuántos elementos hemos "fijado" en su posicion final
                elementos_ordenados[0] += 1
                progreso = min(100, (elementos_ordenados[0] / total_elementos) * 100)
                self.animacion.actualizar_progreso(nombre, progreso)

                _quick_sort(arr, inicio, pivote - 1)
                _quick_sort(arr, pivote + 1, fin)

        def particionar(arr, inicio, fin):
            pivote = arr[fin]
            i = inicio - 1

            for j in range(inicio, fin):
                if arr[j] <= pivote:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]

            arr[i + 1], arr[fin] = arr[fin], arr[i + 1]
            return i + 1

        _quick_sort(arreglo_copia, 0, len(arreglo_copia) - 1)

        snapshot = tracemalloc.take_snapshot()
        memoria = sum(stat.size for stat in snapshot.statistics("lineno"))
        tracemalloc.stop()

        fin = time.time()
        tiempo = fin - inicio

        self.resultados[nombre] = tiempo
        self.memoria_utilizada[nombre] = memoria
        self.tiempos_finalizacion[nombre] = fin - self.tiempo_inicio_global

        # Asegurar que llega a 100% antes de terminar
        self.animacion.actualizar_progreso(nombre, 100)

        self.animacion.marcar_terminado(nombre)

        return arreglo_copia, tiempo, memoria

    def ordenamiento_burbuja(self, arreglo):
        nombre = "Ordenamiento Burbuja"
        inicio = time.time()  # Start time
        tracemalloc.start()  # Start memory tracking

        n = len(arreglo)
        arreglo_copia = arreglo.copy()

        # Total de iteraciones en el peor caso: n*(n-1)/2
        total_iteraciones = n

        for i in range(n):
            # Actualizar progreso basado en iteraciones externas
            progreso = (i / total_iteraciones) * 100
            self.animacion.actualizar_progreso(nombre, progreso)

            intercambio = False
            for j in range(0, n - i - 1):
                if arreglo_copia[j] > arreglo_copia[j + 1]:
                    arreglo_copia[j], arreglo_copia[j + 1] = (
                            arreglo_copia[j + 1],
                            arreglo_copia[j],
                        )
                    intercambio = True

            # Si no hubo intercambios, el arreglo ya está ordenado
            if not intercambio:
                break

        # Asegurar que llega a 100% antes de terminar
        self.animacion.actualizar_progreso(nombre, 100)

        # detener lectura de memoria y guardar resultado
        memoria = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()

        # Stop time and calculate elapsed time
        fin = time.time()
        tiempo = fin - inicio

        # guardar resultados
        self.resultados[nombre] = tiempo
        self.memoria_utilizada[nombre] = memoria
        self.tiempos_finalizacion[nombre] = fin - self.tiempo_inicio_global

        # Mark as completed
        self.animacion.marcar_terminado(nombre)

        return arreglo_copia

    def ordenamiento_insercion(self, arreglo):
        nombre = "Ordenamiento por Insercion"
        inicio = time.time()
        tracemalloc.start()

        arreglo_copia = arreglo.copy()
        n = len(arreglo_copia)

        for i in range(1, n):
            # Actualizar progreso
            progreso = (i / n) * 100
            self.animacion.actualizar_progreso(nombre, progreso)
            # time.sleep(0.01)  # Pequeña pausa para actualizar la animacion

            actual = arreglo_copia[i]
            j = i - 1

            while j >= 0 and actual < arreglo_copia[j]:
                arreglo_copia[j + 1] = arreglo_copia[j]
                j -= 1

            arreglo_copia[j + 1] = actual

        # Asegurar que el progreso llegue al 100%
        self.animacion.actualizar_progreso(nombre, 100)
        self.animacion.marcar_terminado(nombre)

        snapshot = tracemalloc.take_snapshot()
        memoria = sum(stat.size for stat in snapshot.statistics("lineno"))
        tracemalloc.stop()

        fin = time.time()
        tiempo = fin - inicio

        # guardar resultados
        self.resultados = {}
        self.memoria_utilizada = {}
        self.tiempos_finalizacion = {}

        self.resultados[nombre] = tiempo
        self.memoria_utilizada[nombre] = memoria
        self.tiempos_finalizacion[nombre] = fin - self.tiempo_inicio_global

        return arreglo_copia, tiempo, memoria

    def ejecutar_algoritmos_concurrentes(self):
        print(
            f"Preparando ejecucion de algoritmos con un arreglo de tamaño {self.tamano_arreglo}..."
        )
        print(f"Valor a buscar: {self.valor_buscar}")
        print("Iniciando carrera de algoritmos...")

        self.tiempo_inicio_global = time.time()

        # Iniciar hilo de animacion
        hilo_animacion = threading.Thread(target=self.animacion.mostrar_animacion)
        hilo_animacion.daemon = True
        hilo_animacion.start()

        with ThreadPoolExecutor() as executor:
            executor.submit(self.ordenamiento_burbuja, self.arreglo_original)
            executor.submit(self.ordenamiento_insercion, self.arreglo_original)            
            executor.submit(
                self.busqueda_secuencial, self.arreglo_original, self.valor_buscar
            )
            executor.submit(
                self.busqueda_binaria, self.arreglo_original, self.valor_buscar
            )
            executor.submit(self.quick_sort, self.arreglo_original)

        # Esperar a que termine la animacion
        self.animacion.activo = False
        hilo_animacion.join(timeout=1)

        # Ordenar resultados por tiempo de ejecucion
        resultados_ordenados = sorted(self.resultados.items(), key=lambda x: x[1])

        print("\n\n--- Resultados de tiempo de ejecucion ---")
        for algoritmo, tiempo in resultados_ordenados:
            print(f"{algoritmo}: {tiempo:.6f} segundos")

        print("\n--- Resultados de memoria utilizada ---")
        for algoritmo in resultados_ordenados:
            nombre = algoritmo[0]
            memoria = self.memoria_utilizada[nombre]
            print(f"{nombre}: {memoria/1024:.2f} KB")

        print("\n--- Orden de finalizacion ---")
        orden_finalizacion = sorted(
            self.tiempos_finalizacion.items(), key=lambda x: x[1]
        )
        for i, (algoritmo, tiempo) in enumerate(orden_finalizacion):
            print(f"{i+1}. {algoritmo}: termino a los {tiempo:.6f} segundos")

        # Crear gráficas
        self.generar_graficas()

        return resultados_ordenados

    def generar_graficas(self):
        algoritmos = list(self.resultados.keys())
        tiempos = list(self.resultados.values())
        memorias = [
            self.memoria_utilizada[algo] / 1024 for algo in algoritmos
        ]  # Convertir a KB

        # Ordenar por tiempo
        indices_ordenados = sorted(range(len(tiempos)), key=lambda i: tiempos[i])
        algoritmos_ordenados = [algoritmos[i] for i in indices_ordenados]
        tiempos_ordenados = [tiempos[i] for i in indices_ordenados]
        memorias_ordenadas = [memorias[i] for i in indices_ordenados]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Gráfica de tiempos
        bars1 = ax1.bar(algoritmos_ordenados, tiempos_ordenados, color="skyblue")
        ax1.set_title("Tiempo de Ejecucion por Algoritmo")
        ax1.set_ylabel("Tiempo (segundos)")
        ax1.set_xlabel("Algoritmo")
        plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")

        # Añadir etiquetas de valor
        for bar in bars1:
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.02,
                f"{height:.4f}s",
                ha="center",
                va="bottom",
                rotation=0,
            )

        # Gráfica de memoria
        bars2 = ax2.bar(algoritmos_ordenados, memorias_ordenadas, color="lightgreen")
        ax2.set_title("Memoria Utilizada por Algoritmo")
        ax2.set_ylabel("Memoria (KB)")
        ax2.set_xlabel("Algoritmo")
        plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")

        # Añadir etiquetas de valor
        for bar in bars2:
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.02,
                f"{height:.1f} KB",
                ha="center",
                va="bottom",
                rotation=0,
            )

        plt.tight_layout()
        plt.savefig("resultados_algoritmos.png")
        plt.close()

        print("\nGráficas generadas y guardadas como 'resultados_algoritmos.png'")
        print(
            "\nRealizado por: Henry Valmes ft Ramon Minaya, 2025, para Algoritmos Paralelos"
        )


if __name__ == "__main__":
    # Solicitar tamaño del arreglo al usuario
    try:
        tamano = int(input("Ingrese el tamaño del arreglo (recomendado: 10000): "))
    except ValueError:
        print("Valor no válido. Usando tamaño predeterminado de 10000.")
        tamano = 10000

    comparador = AlgoritmosComparacion(tamano_arreglo=tamano)
    resultados = comparador.ejecutar_algoritmos_concurrentes()

    ganador = resultados[0]
    print(
        f"\n🏆 El algoritmo más rápido fue: {ganador[0]} con un tiempo de {ganador[1]:.6f} segundos"
    )
