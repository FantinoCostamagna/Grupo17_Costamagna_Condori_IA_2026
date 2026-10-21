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
test = test.merge(bancarioAgg, on='IDUsuario', how='left').fillna(0)

features = ['MontoSolicitado', 'TasaInteres', 'IngresoMensual', 
            'SaldoPromedioGeneral', 'MaxDiasAtraso', 'PromDiasAtraso'] #
X = train[features]
y = train['EstadoFinal']
Xtest = test[features]

kf = KFold(n_splits=5, shuffle=True, random_state=42)
testPreds = np.zeros(len(test))

for trainIdx, validx in kf.split(X, y):
    Xtr, ytr = X.iloc[trainIdx], y.iloc[trainIdx]
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,          
        min_samples_split=20, 
        random_state=42
    )
    model.fit(Xtr, ytr)
    testPreds += model.predict_proba(Xtest)[:, 1] / kf.n_splits


test['ProbPago'] = testPreds
Retorno_por_inversion_/_perdida_total = ((test['ProbPago'] * (test['MontoSolicitado'] * test['TasaInteres'])) - \
                               ((1 - test['ProbPago']) * test['MontoSolicitado']))

test['EsperanzaMatematica'] = (test['Retorno_por_inversion_/_perdida_total'] / test['MontoSolicitado']) * test['SaldoPromedioGeneral'] #Este calculo lo que nos da es el retorno esperado por cada unidad de dinero invertida, teniendo en cuenta tambien el saldo promedio del usuario.

test = test.sort_values(by= ['EsperanzaMatematica'], ascending=False)

presupuestoMaximo = 2000000
presupuestoAcumulado = 0
decisiones = []

for idx, row in test.iterrows():
    if  presupuestoAcumulado + row['MontoSolicitado'] <= presupuestoMaximo:
        decisiones.append({'ID_Solicitud': row['IDSolicitud'], 'Decision_Aprobacion': 1})
        presupuestoAcumulado += row['MontoSolicitado']
    else:
        decisiones.append({'ID_Solicitud': row['IDSolicitud'], 'Decision_Aprobacion': 0})

dfSub = pd.DataFrame(decisiones)
dfSub.to_csv('submission.csv', index=False)
print("¡Archivo de envío generado correctamente sin superar el presupuesto!")