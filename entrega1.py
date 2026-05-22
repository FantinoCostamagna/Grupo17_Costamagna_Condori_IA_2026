

# todas las coordenadas son en formato (fila, columna)
acciones = planear_rover(
    rover_inicio=(0, 0),
    bateria_inicial=20,
    zonas_sombra=[(0, 1), (0, 2)],
    muestras_igneas=[(1, 1), (1, 2)],
    muestras_sedimentarias=[(2, 3)],
)


def is_goal(self, state):
    if state.carga_muestras == [] and state.muestras_igneas == [] and state.muestras_sedimentarias == []:
        return True
    else:        
        return False


def actions(self, state): 
    acciones
    # Agregar acciones de movimiento
    for fila, columna in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Arriba, abajo, izquierda, derecha
        new_row = state.posicion[0] + fila
        new_col = state.posicion[1] + columna
        if state.bateria > 2 and (0 <= new_row < 4 and 0 <= new_col < 4):  # Verificar límites del mapa
            acciones.append("Moverse", (new_row, new_col))
        else:
            acciones.append(None)  # Acción no válida fuera del mapa
        return acciones
    
    
    # Agregar acción de sobremarcha
    for fila, columna in [(-2, 0), (2, 0), (0, -2), (0, 2)]:  # Arriba, abajo, izquierda, derecha
        new_row = state.posicion[0] + fila
        new_col = state.posicion[1] + columna
        if state.bateria > 5 and (2 <= new_row < 3 and 2 <= new_col < 3):  # Verificar límites del mapa
            acciones.append("Sobremarcha", (new_row, new_col))
        else:
            acciones.append(None)  # Acción no válida fuera del mapa
        return acciones
   
    # Agregar acción de equipar taladro
    if state.bateria > 3 and state.taladro_activo is None:
        acciones.append("Equipar taladro", "térmico")
        return acciones
    elif (state.taladro_activo == "percusión" or planear_rover.rover_inicio in state.muestras_igneas) and state.bateria > 3:
        acciones.append("Equipar taladro", "térmico")
        return acciones
    elif (state.taladro_activo == "térmico" or planear_rover.rover_inicio in state.muestras_sedimentarias) and state.bateria > 3:
        acciones.append("Equipar taladro", "percusión")
        return acciones
    else:
        acciones.append(None)  # Acción no válida si ya tiene el taladro correcto equipado
    
    # Agregar acción de perforar y recolectar
    if state.bateria > 5 and (state.posicion in state.muestras_igneas and state.taladro_activo == "térmico" and len(state.carga_muestras) < 2):
        acciones.append("Perforar y recolectar", "ignea")
        return acciones
    elif state.bateria > 5 and state.posicion in state.muestras_sedimentarias and state.taladro_activo == "percusión" and len(state.carga_muestras) < 2:
        acciones.append("Perforar y recolectar", "sedimentaria")
        return acciones



    # Agregar acción de depositar cápsula con muestras
    if state.bateria > 3 and (len(state.carga_muestras) == 2 or (len(state.carga_muestras) > 0 and state.muestras_igneas == [] and state.muestras_sedimentarias == [])):
        acciones.append("Depositar cápsula con muestras", None)
        return acciones

    
    # Agregar acción de desplegar paneles solares
    if state.posicion not in [planear_rover.zonas_sombra] and (10 >= state.bateria > 0):  # Verificar que no esté en zona de sombra y que tenga 10 o menos de batería, para evitar desperdiciar tiempo recargando cuando no es necesario
        acciones.append("Desplegar paneles solares y recargar batería", None)
        planear_rover.bateria_inicial = min(state.bateria + 10, 20)  # Recargar batería sin exceder el límite máximo
        return acciones
    else:
        acciones.append(None)  # Acción no válida en zona de sombra o si la batería está llena o agotada

            

def cost(self, estadoactual, acciones):
    if acciones[0] == "Moverse":
        return 1
    elif acciones[0] == "Sobremarcha":
        return 4
    elif acciones[0] == "Equipar taladro":
        return 1
    elif acciones[0] == "Perforar y recolectar":
        return 3
    elif acciones[0] == "Depositar cápsula con muestras":
        return len(estadoactual.carga_muestras)  # Costo de 1 por cada muestra entregada
    elif acciones[0] == "Desplegar paneles solares y recargar batería":
        return 0  # No consume batería, solo tiempo
    else:
        return float('inf')  # Acción no válida, costo infinito
 


def result(self, estadoactual, accion):
    carga_muestras = []


def heuristic(state):    # Heurística basada en la cantidad de muestras restantes , costo de recolectarlas y soltarlas en la cápsula, ajustable según la importancia de cada muestra.
    
    muestras_restantes = len(state.muestras_igneas) + len(state.muestras_sedimentarias)
    return len(muestras_restantes) * 4  # Asignar un costo de 4 por cada muestra restante, 3 es el costo de recolectar cada muestra y 1 el costo de depositarla en la cápsula (en caso que haya una sola muestra, este parado sobre ella, y tenga el taladro correspondiente).

