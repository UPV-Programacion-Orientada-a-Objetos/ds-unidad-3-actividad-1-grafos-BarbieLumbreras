import sys
import os
import matplotlib

# Configurar el backend de matplotlib para Tkinter
matplotlib.use("TkAgg")

# Agregar el directorio 'src' al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from grafo import PyGrafoDisperso
import io
import contextlib


class NeuroNetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NeuroNet - Análisis de Grafos Masivos")
        self.root.geometry("1024x768")
        self.grafo = PyGrafoDisperso()
        self.archivo_actual = None
        self.num_aristas = 0
        self.memoria_mb = 0

        # ==================== PANEL IZQUIERDO ====================
        self.frame_izquierdo = tk.Frame(root, width=200, relief=tk.RIDGE, borderwidth=2)
        self.frame_izquierdo.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.frame_izquierdo.pack_propagate(False)

        # --- Carga de Dataset ---
        self.frame_carga = tk.LabelFrame(self.frame_izquierdo, text="Carga de Dataset", padx=10, pady=10)
        self.frame_carga.pack(fill=tk.X, padx=5, pady=5)

        self.button_cargar = tk.Button(self.frame_carga, text="Seleccionar Archivo", 
                                       command=self.cargar_archivo, width=20)
        self.button_cargar.pack(pady=5)

        self.label_archivo = tk.Label(self.frame_carga, text="", fg="blue", wraplength=180)
        self.label_archivo.pack(pady=5)

        # --- Métricas del Grafo ---
        self.frame_metricas = tk.LabelFrame(self.frame_izquierdo, text="Métricas del Grafo", padx=10, pady=10)
        self.frame_metricas.pack(fill=tk.X, padx=5, pady=5)

        self.label_nodos = tk.Label(self.frame_metricas, text="Nodos: 0", anchor=tk.W)
        self.label_nodos.pack(fill=tk.X, pady=2)

        self.label_aristas = tk.Label(self.frame_metricas, text="Aristas: 0", anchor=tk.W)
        self.label_aristas.pack(fill=tk.X, pady=2)

        self.label_memoria = tk.Label(self.frame_metricas, text="Memoria (MB): 0", anchor=tk.W)
        self.label_memoria.pack(fill=tk.X, pady=2)

        self.label_nodo_critico = tk.Label(self.frame_metricas, text="Nodo Mayor Grado: -", anchor=tk.W)
        self.label_nodo_critico.pack(fill=tk.X, pady=2)

        # --- Controles de Análisis ---
        self.frame_controles = tk.LabelFrame(self.frame_izquierdo, text="Controles de Análisis", padx=10, pady=10)
        self.frame_controles.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(self.frame_controles, text="Nodo Inicial:", anchor=tk.W).pack(fill=tk.X)
        self.entry_nodo_inicio = tk.Entry(self.frame_controles)
        self.entry_nodo_inicio.pack(fill=tk.X, pady=2)
        self.entry_nodo_inicio.insert(0, "0")

        tk.Label(self.frame_controles, text="Profundidad:", anchor=tk.W).pack(fill=tk.X)
        self.entry_profundidad = tk.Entry(self.frame_controles)
        self.entry_profundidad.pack(fill=tk.X, pady=2)
        self.entry_profundidad.insert(0, "2")

        self.button_bfs = tk.Button(self.frame_controles, text="Ejecutar BFS", 
                                    command=self.ejecutar_bfs, width=15)
        self.button_bfs.pack(pady=5)

        self.button_nodo_critico = tk.Button(self.frame_controles, text="Calcular Nodo Crítico", 
                                             command=self.calcular_nodo_critico, width=15)
        self.button_nodo_critico.pack(pady=5)

        # ==================== PANEL CENTRAL ====================
        self.frame_central = tk.Frame(root)
        self.frame_central.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Visualización de Grafo ---
        self.frame_visualizacion = tk.LabelFrame(self.frame_central, text="Visualización de Grafo", padx=5, pady=5)
        self.frame_visualizacion.pack(fill=tk.BOTH, expand=True)

        self.figure = plt.Figure(figsize=(10, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.frame_visualizacion)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # ==================== PANEL INFERIOR (CONSOLA) ====================
        self.frame_consola = tk.LabelFrame(root, text="Consola de Logs", padx=5, pady=5)
        self.frame_consola.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.text_consola = scrolledtext.ScrolledText(self.frame_consola, height=8, 
                                                      bg="black", fg="green", 
                                                      font=("Courier", 9))
        self.text_consola.pack(fill=tk.BOTH, expand=True)
        
        # Redirigir stdout a la consola
        sys.stdout = TextRedirector(self.text_consola, "stdout")

        self.log("NeuroNet iniciado. Listo para cargar datasets.")

    def log(self, mensaje):
        """Agregar mensaje a la consola"""
        self.text_consola.insert(tk.END, f"{mensaje}\n")
        self.text_consola.see(tk.END)

    def cargar_archivo(self):
        archivo = filedialog.askopenfilename(
            initialdir=os.path.abspath(os.path.join(os.path.dirname(__file__), "datasets")),
            filetypes=[("Archivos de texto", "*.txt")]
        )
        if archivo:
            try:
                self.log(f"[NeuroNet] Cargando archivo: {os.path.basename(archivo)}")
                self.grafo.cargarDatos(archivo)
                self.archivo_actual = archivo
                self.actualizar_interfaz(archivo)
                self.log(f"[NeuroNet] Dataset cargado exitosamente.")
            except Exception as e:
                self.log(f"[NeuroNet] Error: {str(e)}")
                messagebox.showerror("Error", str(e))

    def actualizar_interfaz(self, archivo):
        # Actualizar métricas
        num_nodos = self.grafo.numNodos
        
        # Calcular número de aristas (aproximado)
        self.num_aristas = sum(self.grafo.obtenerGrado(i) for i in range(min(num_nodos, 1000)))
        if num_nodos > 1000:
            self.num_aristas = int(self.num_aristas * (num_nodos / 1000))
        
        # Estimar memoria (muy aproximado)
        self.memoria_mb = (num_nodos * 4 + self.num_aristas * 8) / (1024 * 1024)
        
        nodo_critico = self.grafo.obtenerNodoCritico()
        max_grado = self.grafo.obtenerGrado(nodo_critico) if nodo_critico != -1 else 0

        self.label_archivo.config(text=os.path.basename(archivo))
        self.label_nodos.config(text=f"Nodos: {num_nodos:,}")
        self.label_aristas.config(text=f"Aristas: {self.num_aristas:,}")
        self.label_memoria.config(text=f"Memoria (MB): {self.memoria_mb:.2f}")
        self.label_nodo_critico.config(text=f"Nodo Mayor Grado: {nodo_critico}")

        # Visualizar el grafo con estrategias según el tamaño
        self.visualizar_grafo_completo(archivo)

    def ejecutar_bfs(self):
        nodo_inicio = self.entry_nodo_inicio.get()
        profundidad = self.entry_profundidad.get()
        if nodo_inicio.isdigit() and profundidad.isdigit():
            nodo_inicio = int(nodo_inicio)
            profundidad = int(profundidad)
            try:
                self.log(f"[NeuroNet] Ejecutando BFS desde nodo {nodo_inicio}, profundidad {profundidad}...")
                resultado = self.grafo.BFS(nodo_inicio, profundidad)
                self.visualizar_subgrafo(resultado, "BFS")
                self.log(f"[NeuroNet] BFS completado: {len(resultado)} nodos encontrados.")
            except Exception as e:
                self.log(f"[NeuroNet] Error en BFS: {str(e)}")
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showerror("Error", "Por favor ingrese valores válidos para Nodo Inicial y Profundidad.")

    def calcular_nodo_critico(self):
        try:
            self.log("[NeuroNet] Calculando nodo crítico...")
            nodo_critico = self.grafo.obtenerNodoCritico()
            grado = self.grafo.obtenerGrado(nodo_critico)
            self.label_nodo_critico.config(text=f"Nodo Mayor Grado: {nodo_critico}")
            self.log(f"[NeuroNet] Nodo crítico: {nodo_critico} (grado: {grado})")
            messagebox.showinfo("Nodo Crítico", f"Nodo: {nodo_critico}\nGrado: {grado}")
        except Exception as e:
            self.log(f"[NeuroNet] Error: {str(e)}")
            messagebox.showerror("Error", str(e))

    def visualizar_grafo_completo(self, archivo):
        self.ax.clear()
        G = nx.DiGraph()
        num_nodos = self.grafo.numNodos
        
        try:
            # Estrategia 1: Grafos pequeños (<1000 nodos) - Visualización completa con etiquetas
            if num_nodos < 1000:
                for nodo in range(num_nodos):
                    vecinos = self.grafo.getVecinos(nodo)
                    for vecino in vecinos:
                        G.add_edge(nodo, vecino)
                nx.draw(G, ax=self.ax, with_labels=True, node_color="lightblue", 
                       font_weight="bold", node_size=300, font_size=8)
                self.ax.set_title(f"Grafo Completo: {os.path.basename(archivo)}")
            
            # Estrategia 2: Grafos medianos (1000-10000 nodos) - Visualización completa sin etiquetas
            elif num_nodos < 10000:
                for nodo in range(num_nodos):
                    vecinos = self.grafo.getVecinos(nodo)
                    for vecino in vecinos:
                        G.add_edge(nodo, vecino)
                nx.draw(G, ax=self.ax, with_labels=False, node_color="lightblue", 
                       node_size=50, alpha=0.6)
                self.ax.set_title(f"Grafo: {os.path.basename(archivo)} ({num_nodos} nodos)")
            
            # Estrategia 3: Grafos grandes (>10000 nodos) - Muestreo con BFS para garantizar conectividad
            else:
                # Usar BFS desde el nodo crítico para obtener un subgrafo conectado
                nodo_critico = self.grafo.obtenerNodoCritico()
                
                # Ajustar profundidad para obtener aproximadamente 1000 nodos
                profundidad = 3
                nodos_muestra = self.grafo.BFS(nodo_critico, profundidad)
                
                # Si obtenemos muy pocos nodos, aumentar profundidad
                while len(nodos_muestra) < 500 and profundidad < 6:
                    profundidad += 1
                    nodos_muestra = self.grafo.BFS(nodo_critico, profundidad)
                
                # Si obtenemos demasiados, limitar a los primeros 1500
                if len(nodos_muestra) > 1500:
                    nodos_muestra = nodos_muestra[:1500]
                
                nodos_set = set(nodos_muestra)
                
                # Construir subgrafo con los nodos del BFS (todos conectados)
                for nodo in nodos_muestra:
                    vecinos = self.grafo.getVecinos(nodo)
                    for vecino in vecinos:
                        if vecino in nodos_set:
                            G.add_edge(nodo, vecino)
                
                # Visualizar con layout optimizado
                pos = nx.spring_layout(G, k=0.5, iterations=20)
                nx.draw(G, pos, ax=self.ax, with_labels=False, node_color="lightblue", 
                       node_size=30, alpha=0.7, edge_color="gray", width=0.5)
                self.ax.set_title(f"Grafo (subgrafo conectado): {os.path.basename(archivo)}\n({len(nodos_muestra)} de {num_nodos} nodos)")
            
            self.canvas.draw()
        except Exception as e:
            self.log(f"[NeuroNet] Error al visualizar: {str(e)}")
            messagebox.showerror("Error al visualizar el grafo", str(e))

    def visualizar_subgrafo(self, nodos, tipo="Subgrafo"):
        self.ax.clear()
        G = nx.DiGraph()
        try:
            nodos_set = set(nodos)
            for nodo in nodos:
                vecinos = self.grafo.getVecinos(nodo)
                for vecino in vecinos:
                    if vecino in nodos_set:
                        G.add_edge(nodo, vecino)
            
            pos = nx.spring_layout(G, k=0.5, iterations=30)
            nx.draw(G, pos, ax=self.ax, with_labels=True, node_color="lightgreen", 
                   font_weight="bold", node_size=300, font_size=8)
            self.ax.set_title(f"{tipo}: {len(nodos)} nodos, {G.number_of_edges()} aristas")
            self.canvas.draw()
        except Exception as e:
            self.log(f"[NeuroNet] Error al visualizar subgrafo: {str(e)}")
            messagebox.showerror("Error al visualizar el subgrafo", str(e))


class TextRedirector:
    """Redirige stdout/stderr a un widget de texto"""
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.insert(tk.END, str)
        self.widget.see(tk.END)
    
    def flush(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = NeuroNetApp(root)
    root.mainloop()
