#ifndef GRAFODISPERSO_H
#define GRAFODISPERSO_H

#include "GrafoBase.h"
#include <vector>
#include <string>
#include <unordered_map>

class GrafoDisperso : public GrafoBase {
private:
    std::vector<int> valores;
    std::vector<int> indicesColumnas;
    std::vector<int> punterosFilas;
    int numNodos;

public:
    GrafoDisperso();
    void cargarDatos(const std::string& archivo) override;
    int obtenerGrado(int nodo) const override;
    std::vector<int> getVecinos(int nodo) const override;
    std::vector<int> BFS(int nodoInicio, int profundidadMax) const override;
    int obtenerNodoCritico() const override;

    int getNumNodos() const; // Nuevo método público para acceder a numNodos
};

#endif // GRAFODISPERSO_H
