# entrega1_por_ia.py
from simpleai.search import SearchProblem, astar
from heapq import heappush, heappop
from itertools import count




MAX_BATTERY = 20




def planear_rover(
    rover_inicio,
    bateria_inicial,
    zonas_sombra,
    muestras_igneas,
    muestras_sedimentarias,
):
    zonas_sombra = frozenset(zonas_sombra)
    muestras_igneas = frozenset(muestras_igneas)
    muestras_sedimentarias = frozenset(muestras_sedimentarias)


    estado_inicial = (
        rover_inicio,             # posición
        bateria_inicial,          # batería
        "ninguno",                # taladro
        0,                        # carga
        muestras_igneas,
        muestras_sedimentarias,
    )


    if es_objetivo(estado_inicial):
        return []


    puntos = [rover_inicio]
    puntos.extend(muestras_igneas)
    puntos.extend(muestras_sedimentarias)
    puntos.extend(zonas_sombra)


    if puntos:
        filas = [p[0] for p in puntos]
        cols = [p[1] for p in puntos]


        margen = 8


        min_r = min(filas) - margen
        max_r = max(filas) + margen
        min_c = min(cols) - margen
        max_c = max(cols) + margen
    else:
        min_r = -10
        max_r = 10
        min_c = -10
        max_c = 10


    frontera = []
    contador = count()


    g_score = {estado_inicial: 0}


    heappush(
        frontera,
        (
            heuristica(estado_inicial),
            next(contador),
            estado_inicial,
        ),
    )


    padre = {}
    accion_padre = {}


    while frontera:


        _, _, actual = heappop(frontera)


        if es_objetivo(actual):
            return reconstruir(
                actual,
                padre,
                accion_padre,
            )


        costo_actual = g_score[actual]


        for accion, vecino, costo in sucesores(
            actual,
            zonas_sombra,
            min_r,
            max_r,
            min_c,
            max_c,
        ):


            nuevo_g = costo_actual + costo


            if nuevo_g < g_score.get(vecino, float("inf")):


                g_score[vecino] = nuevo_g
                padre[vecino] = actual
                accion_padre[vecino] = accion


                f = nuevo_g + heuristica(vecino)


                heappush(
                    frontera,
                    (
                        f,
                        next(contador),
                        vecino,
                    ),
                )


    return []




def es_objetivo(estado):
    _, _, _, carga, igneas, sedimentarias = estado


    return (
        carga == 0
        and not igneas
        and not sedimentarias
    )




def heuristica(estado):
    pos, _, _, carga, igneas, sedimentarias = estado


    restantes = len(igneas) + len(sedimentarias)


    h = restantes * 2


    objetivos = []


    for p in igneas:
        objetivos.append(p)


    for p in sedimentarias:
        objetivos.append(p)


    if objetivos:
        d = min(
            abs(pos[0] - r) + abs(pos[1] - c)
            for r, c in objetivos
        )


        h += d // 2


    if carga == 2:
        h += 1


    return h




def sucesores(
    estado,
    zonas_sombra,
    min_r,
    max_r,
    min_c,
    max_c,
):
    (
        posicion,
        bateria,
        taladro,
        carga,
        igneas,
        sedimentarias,
    ) = estado


    r, c = posicion


    # -----------------------
    # MOVIMIENTO NORMAL
    # -----------------------


    movimientos = (
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
    )


    for dr, dc in movimientos:


        nr = r + dr
        nc = c + dc


        if not (
            min_r <= nr <= max_r
            and min_c <= nc <= max_c
        ):
            continue


        nueva_bateria = bateria - 1


        if nueva_bateria <= 0:
            continue


        yield (
            ("moverse", (nr, nc)),
            (
                (nr, nc),
                nueva_bateria,
                taladro,
                carga,
                igneas,
                sedimentarias,
            ),
            1,
        )


    # -----------------------
    # SOBREMARCHA
    # -----------------------


    for dr, dc in movimientos:


        nr = r + dr * 2
        nc = c + dc * 2


        if not (
            min_r <= nr <= max_r
            and min_c <= nc <= max_c
        ):
            continue


        nueva_bateria = bateria - 4


        if nueva_bateria <= 0:
            continue


        yield (
            ("sobremarcha", (nr, nc)),
            (
                (nr, nc),
                nueva_bateria,
                taladro,
                carga,
                igneas,
                sedimentarias,
            ),
            1,
        )


    # -----------------------
    # EQUIPAR
    # -----------------------


    if bateria > 1:


        if taladro != "termico":


            yield (
                ("equipar", "termico"),
                (
                    posicion,
                    bateria - 1,
                    "termico",
                    carga,
                    igneas,
                    sedimentarias,
                ),
                3,
            )


        if taladro != "percusion":


            yield (
                ("equipar", "percusion"),
                (
                    posicion,
                    bateria - 1,
                    "percusion",
                    carga,
                    igneas,
                    sedimentarias,
                ),
                3,
            )


    # -----------------------
    # RECOLECTAR IGNEA
    # -----------------------


    if (
        posicion in igneas
        and taladro == "termico"
        and carga < 2
        and bateria > 3
    ):


        nuevas = frozenset(
            x for x in igneas
            if x != posicion
        )


        yield (
            ("recolectar", "ignea"),
            (
                posicion,
                bateria - 3,
                taladro,
                carga + 1,
                nuevas,
                sedimentarias,
            ),
            2,
        )


    # -----------------------
    # RECOLECTAR SEDIMENTARIA
    # -----------------------


    if (
        posicion in sedimentarias
        and taladro == "percusion"
        and carga < 2
        and bateria > 3
    ):


        nuevas = frozenset(
            x for x in sedimentarias
            if x != posicion
        )


        yield (
            ("recolectar", "sedimentaria"),
            (
                posicion,
                bateria - 3,
                taladro,
                carga + 1,
                igneas,
                nuevas,
            ),
            2,
        )


    # -----------------------
    # DEPOSITAR
    # -----------------------


    restantes = (
        len(igneas)
        + len(sedimentarias)
    )


    puede_depositar = False


    if carga == 2:
        puede_depositar = True


    elif carga == 1 and restantes == 0:
        puede_depositar = True


    if (
        puede_depositar
        and bateria > 1
    ):


        costo = carga


        yield (
            ("depositar", None),
            (
                posicion,
                bateria - 1,
                taladro,
                0,
                igneas,
                sedimentarias,
            ),
            costo,
        )


    # -----------------------
    # RECARGAR
    # -----------------------


    if (
        posicion not in zonas_sombra
        and bateria < MAX_BATTERY
    ):


        nueva_bateria = min(
            MAX_BATTERY,
            bateria + 10,
        )


        yield (
            ("recargar", None),
            (
                posicion,
                nueva_bateria,
                taladro,
                carga,
                igneas,
                sedimentarias,
            ),
            4,
        )




def reconstruir(
    objetivo,
    padre,
    accion_padre,
):
    camino = []


    actual = objetivo


    while actual in padre:


        camino.append(
            accion_padre[actual]
        )


        actual = padre[actual]


    camino.reverse()


    return camino

