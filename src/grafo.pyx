# distutils: language = c++
from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp.memory cimport unique_ptr
from cpython.ref cimport PyObject

cdef extern from "GrafoDisperso.h":
    cdef cppclass GrafoDisperso:
        GrafoDisperso()
        void cargarDatos(string archivo)
        int obtenerGrado(int nodo)
        vector[int] getVecinos(int nodo)
        vector[int] BFS(int nodoInicio, int profundidadMax)
        int getNumNodos() const  # Cambiar acceso directo a numNodos por el método público
        int obtenerNodoCritico() const

cdef class PyGrafoDisperso:
    cdef unique_ptr[GrafoDisperso] grafo

    def __cinit__(self):
        self.grafo = unique_ptr[GrafoDisperso](new GrafoDisperso())

    def cargarDatos(self, archivo: str):
        cdef string archivo_cpp
        try:
            archivo_cpp = archivo.encode('utf-8')
            print(f"[Cython] Solicitud recibida: Cargar dataset '{archivo}'.")
            self.grafo.get().cargarDatos(archivo_cpp)
            print("[Cython] Dataset cargado exitosamente.")
        except Exception as e:
            print(f"[Cython] Error en cargarDatos: {e}")
            raise

    def obtenerGrado(self, nodo: int) -> int:
        return self.grafo.get().obtenerGrado(nodo)

    def getVecinos(self, nodo: int) -> list:
        cdef vector[int] vecinos = self.grafo.get().getVecinos(nodo)
        return [vecino for vecino in vecinos]

    def BFS(self, nodoInicio: int, profundidadMax: int) -> list:
        print(f"[Cython] Solicitud recibida: BFS desde Nodo {nodoInicio}, Profundidad {profundidadMax}.")
        try:
            cdef vector[int] resultado = self.grafo.get().BFS(nodoInicio, profundidadMax)
            print("[Cython] BFS completado. Retornando lista de adyacencia a Python.")
            return [nodo for nodo in resultado]
        except Exception as e:
            print(f"[Cython] Error en BFS: {e}")
            raise

    @property
    def numNodos(self) -> int:
        return self.grafo.get().getNumNodos()

    def obtenerNodoCritico(self) -> int:
        return self.grafo.get().obtenerNodoCritico()
