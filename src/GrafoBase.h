#ifndef GRAFOBASE_H
#define GRAFOBASE_H

#include <vector>
#include <string>

class GrafoBase {
public:
    virtual ~GrafoBase() = default;

    virtual void cargarDatos(const std::string& archivo) = 0;
    virtual int obtenerGrado(int nodo) const = 0;
    virtual std::vector<int> getVecinos(int nodo) const = 0;
    virtual std::vector<int> BFS(int nodoInicio, int profundidadMax) const = 0;
    virtual int obtenerNodoCritico() const = 0;
};

#endif // GRAFOBASE_H
