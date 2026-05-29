# Grupo17_Costamagna_Condori_IA_2026
conclusiones:

El factor determinante en el tiempo de resolución no es el tamaño del mapa en sí, sino la cantidad y variedad de módulos a posicionar. A mayor número de variables, el espacio de estados crece de forma exponencial, incrementando significativamente los pasos de backtracking.
Al aplicar de forma unaria las restricciones geográficas directamente en la creación de los dominios redujo drásticamente el espacio de búsqueda inicial. Esto evitó que el algoritmo evaluara miles de combinaciones estructuralmente inválidas.
Las restricciones binarias y n-arias actúan como fuertes podas en el árbol de búsqueda. Si bien restringen el dominio rápidamente, en mapas muy densos o con muchos cráteres provocan un backtracking más profundo debido a los conflictos de colisión.
El motor de simpleai.search.backtrack demostró ser altamente eficiente para resolver los casos simples y medianos en pocos segundos. Sin embargo, en escenarios críticos con alta densidad de módulos y restricciones activas en simultáneo, el tiempo de cómputo se eleva evidenciando la complejidad intrínseca de los problemas.