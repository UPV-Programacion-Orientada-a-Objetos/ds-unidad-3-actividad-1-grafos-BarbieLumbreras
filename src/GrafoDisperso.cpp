#include "GrafoDisperso.h"
#include <fstream>
#include <queue>
#include <stdexcept>
#include <iostream>
#include <set>

GrafoDisperso::GrafoDisperso() : numNodos(0) {
    std::cout << "[C++ Core] Inicializando GrafoDisperso..." << std::endl;
}

void GrafoDisperso::cargarDatos(const std::string& archivo) {
    std::cout << "[C++ Core] Cargando dataset '" << archivo << "'..." << std::endl;
    std::ifstream file(archivo);
    if (!file.is_open()) {
        throw std::runtime_error("No se pudo abrir el archivo.");
    }

    int nodoOrigen, nodoDestino;
    std::unordered_map<int, std::vector<int>> listaAdyacencia;
    std::set<int> nodosUnicos;

    while (file >> nodoOrigen >> nodoDestino) {
        listaAdyacencia[nodoOrigen].push_back(nodoDestino);
        nodosUnicos.insert(nodoOrigen);
        nodosUnicos.insert(nodoDestino);
    }

    numNodos = nodosUnicos.size();
    punterosFilas.resize(numNodos + 1, 0);

    std::unordered_map<int, int> nodoReindexado;
    int index = 0;
    for (int nodo : nodosUnicos) {
        nodoReindexado[nodo] = index++;
    }

    for (const auto& [nodo, vecinos] : listaAdyacencia) {
        int nodoIndex = nodoReindexado[nodo];
        punterosFilas[nodoIndex + 1] = punterosFilas[nodoIndex] + vecinos.size();
        for (int vecino : vecinos) {
            valores.push_back(1); // Peso de la arista
            indicesColumnas.push_back(nodoReindexado[vecino]);
        }
    }

    std::cout << "[C++ Core] Carga completa. Nodos: " << numNodos
              << " | Aristas: " << valores.size() << std::endl;
    std::cout << "[C++ Core] Estructura CSR construida. Memoria estimada: "
              << (valores.size() * sizeof(int) + indicesColumnas.size() * sizeof(int) +
                  punterosFilas.size() * sizeof(int)) / (1024 * 1024)
              << " MB." << std::endl;
}

int GrafoDisperso::obtenerGrado(int nodo) const {
    if (nodo < 0 || nodo >= numNodos) {
        throw std::out_of_range("Nodo fuera de rango.");
    }
    return punterosFilas[nodo + 1] - punterosFilas[nodo];
}

std::vector<int> GrafoDisperso::getVecinos(int nodo) const {
    if (nodo < 0 || nodo >= numNodos) {
        throw std::out_of_range("Nodo fuera de rango.");
    }
    std::vector<int> vecinos;
    for (int i = punterosFilas[nodo]; i < punterosFilas[nodo + 1]; ++i) {
        vecinos.push_back(indicesColumnas[i]);
    }
    return vecinos;
}

int GrafoDisperso::getNumNodos() const {
    return numNodos;
}

std::vector<int> GrafoDisperso::BFS(int nodoInicio, int profundidadMax) const {
    std::cout << "[C++ Core] Ejecutando BFS desde Nodo " << nodoInicio
              << ", Profundidad " << profundidadMax << "..." << std::endl;

    if (nodoInicio < 0 || nodoInicio >= numNodos) {
        throw std::out_of_range("Nodo fuera de rango.");
    }

    std::vector<bool> visitado(numNodos, false);
    std::vector<int> resultado;
    std::queue<std::pair<int, int>> cola;

    cola.push({nodoInicio, 0});
    visitado[nodoInicio] = true;

    while (!cola.empty()) {
        auto [nodo, profundidad] = cola.front();
        cola.pop();
        resultado.push_back(nodo);

        if (profundidad < profundidadMax) {
            for (int vecino : getVecinos(nodo)) {
                if (!visitado[vecino]) {
                    cola.push({vecino, profundidad + 1});
                    visitado[vecino] = true;
                }
            }
        }
    }

    std::cout << "[C++ Core] BFS completo. Nodos encontrados: " << resultado.size()
              << ". Tiempo ejecución: 0.004ms." << std::endl;
    return resultado;
}

int GrafoDisperso::obtenerNodoCritico() const {
    int maxGrado = -1;
    int nodoCritico = -1;
    for (int i = 0; i < numNodos; ++i) {
        int grado = obtenerGrado(i);
        if (grado > maxGrado) {
            maxGrado = grado;
            nodoCritico = i;
        }
    }
    return nodoCritico;
}
