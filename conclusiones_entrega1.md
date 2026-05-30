# Grupo17_Costamagna_Condori_IA_2026
Conclusiones

Podemos destacar que la IA plantea el mismo estado que planteamos nosotros. Las principales diferencias se encuentran en la heurística y en la implementación de las acciones. Además, la entrega realizada por la IA utiliza librerías externas que nosotros no empleamos, ya que no fueron incluidas en el enunciado del trabajo.

La heurística desarrollada por la IA es considerablemente más simple y rápida que la nuestra. Sin embargo, también resulta menos precisa, ya que estima el costo restante principalmente a partir de la cantidad de muestras pendientes y la distancia al objetivo más cercano. En cambio, nuestra heurística considera múltiples factores del problema, como movimientos, batería disponible, recargas necesarias, cambios de taladro, recolección, depósito y una estimación del recorrido óptimo, logrando una representación más completa del costo restante.

En cuanto a las acciones, observamos que ambas soluciones contemplan esencialmente las mismas operaciones. La diferencia radica en la estructura de implementación: la IA genera directamente el nuevo estado y el costo asociado a cada acción, mientras que nuestra solución primero determina las acciones posibles y posteriormente calcula el estado resultante y su costo. Esto proporciona una mayor separación de responsabilidades y una estructura más modular y mantenible, aunque la implementación de la IA resulta más directa.

Por último, al comparar la performance y los tiempos de ejecución, ambas entregas superan correctamente todos los tests y obtienen resultados en tiempos reducidos. Sin embargo, la entrega realizada por la IA presenta un tiempo de ejecución aproximado de 2,2 segundos, mientras que nuestra implementación resuelve los mismos casos en alrededor de 1 segundo. Por lo tanto, podemos concluir que nuestra solución presenta un mejor rendimiento general.
