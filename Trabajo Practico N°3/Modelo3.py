#
# 
# CON ESTE OBTUVIMOS EL MEJOR RESULTADO DE LOS TRES MODELOS, YA QUE SE LE SUMA EL SALDO PROMEDIO DEL USUARIO A LA ESPERANZA MATEMATICA, LO CUAL NOS DA UNA MEJOR PREDICCION DE LA RENTABILIDAD DE CADA SOLICITUD.


import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier

train = pd.read_csv('C:\\Users\\tamar\\Downloads\\Grupo17_Costamagna_Condori_IA_2026-main\\Trabajo Practico N°3\\datos\\solicitudes_train.csv')
test = pd.read_csv('C:\\Users\\tamar\\Downloads\\Grupo17_Costamagna_Condori_IA_2026-main\\Trabajo Practico N°3\\datos\\solicitudes_test.csv')
bancario = pd.read_csv('C:\\Users\\tamar\\Downloads\\Grupo17_Costamagna_Condori_IA_2026-main\\Trabajo Practico N°3\\datos\\comportamiento_bancario.csv')

bancarioAgg = bancario.groupby('IDUsuario').agg(  
    SaldoPromedioGeneral=('SaldoPromedioMensual', 'mean'),
    MaxDiasAtraso=('DiasAtrasoOtrasDeudas', 'max'),
    PromDiasAtraso=('DiasAtrasoOtrasDeudas', 'mean')
).reset_index() # Agrupa por IDUsuario y calcula las estadísticas que consideramos importantes para el modelo, como el saldo promedio general, el máximo de días de atraso y el promedio de días de atraso. 

train = train.merge(bancarioAgg, on='IDUsuario', how='left').fillna(0) 
test = test.merge(bancarioAgg, on='IDUsuario', how='left').fillna(0) # Unificamos los datos de train y test con los datos agregados del comportamiento bancario, utilizando el IDUsuario como clave. Cualquier valor faltante se rellena con 0.

features = ['MontoSolicitado', 'TasaInteres', 'IngresoMensual', 
            'SaldoPromedioGeneral', 'MaxDiasAtraso', 'PromDiasAtraso'] # Variables que consideramos relevantes para predecir el EstadoFinal de la solicitud.

X = train[features] 
y = train['EstadoFinal'] 
Xtest = test[features] 


kf = KFold(n_splits=5, shuffle=True, random_state=42) # Validacion cruzada con 5 particiones, un shuffle de los datos y la semilla random_state para reproducibilidad.

testPreds = np.zeros(len(test)) # Esto nos permite almacenar las predicciones de probabilidad de pago para cada solicitud en el conjunto de prueba.

for trainIdx, validx in kf.split(X, y):
    Xtr, ytr = X.iloc[trainIdx], y.iloc[trainIdx]
    # Modelo random foerst con 100 árboles, profundidad máxima de 6, un mínimo de 20 muestras para dividir un nodo y una semilla random_state para reproducibilidad.
    model = RandomForestClassifier(   
        n_estimators=100,
        max_depth=6,          
        min_samples_split=20, 
        random_state=42
    )
    model.fit(Xtr, ytr)
    testPreds += model.predict_proba(Xtest)[:, 1] / kf.n_splits  

 
test['ProbPago'] = testPreds # Test para almacenar las predicciones de probabilidad de pago para cada solicitud en el conjunto de prueba.
test['Retorno_por_inversion_/_perdida_total'] = ((test['ProbPago'] * (test['MontoSolicitado'] * test['TasaInteres'])) - \
                               ((1 - test['ProbPago']) * test['MontoSolicitado']))

test['EsperanzaMatematica'] = (test['Retorno_por_inversion_/_perdida_total'] / test['MontoSolicitado']) * test['SaldoPromedioGeneral'] # Este calculo lo que nos da es el retorno esperado por cada unidad de dinero invertida, teniendo en cuenta tambien el saldo promedio del usuario.

test = test.sort_values(by= ['EsperanzaMatematica'], ascending=False)

presupuestoMaximo = 2000000
presupuestoAcumulado = 0
decisiones = []


# Si no superamos el presupuesto maximo, aprobamos la solicitud y sumamos el monto solicitado al presupuesto acumulado, sino se rechaza la solicitud y no se suma al presupuesto acumulado. 
for idx, row in test.iterrows():
    if  presupuestoAcumulado + row['MontoSolicitado'] <= presupuestoMaximo: 
        decisiones.append({'ID_Solicitud': row['IDSolicitud'], 'Decision_Aprobacion': 1})
        presupuestoAcumulado += row['MontoSolicitado']
    else:
        decisiones.append({'ID_Solicitud': row['IDSolicitud'], 'Decision_Aprobacion': 0})

dfSub = pd.DataFrame(decisiones)
dfSub.to_csv('submission.csv', index=False) # Se crea el csv
print("¡Archivo de envío generado correctamente sin superar el presupuesto!")