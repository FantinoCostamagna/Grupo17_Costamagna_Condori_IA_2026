import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier


train = pd.read_csv('datos/solicitudes_train.csv')
test = pd.read_csv('datos/solicitudes_test.csv')
bancario = pd.read_csv('datos/comportamiento_bancario.csv')

bancarioAgg = bancario.groupby('IDUsuario').agg(
    SaldoPromedioGeneral=('SaldoPromedioMensual', 'mean'),
    MaxDiasAtraso=('DiasAtrasoOtrasDeudas', 'max'),
    PromDiasAtraso=('DiasAtrasoOtrasDeudas', 'mean')
).reset_index()

train = train.merge(bancarioAgg, on='IDUsuario', how='left').fillna(0)
test = test.merge(bancarioAgg, on='IDUsuario', how='left').fillna(0)

features = ['MontoSolicitado', 'TasaInteres', 'Ingreso_Mensual', 
            'SaldoPromedioGeneral', 'MaxDiasAtraso', 'PromDiasAtraso']
X = train[features]
y = train['EstadoFinal']
Xtest = test[features]

kf = KFold(nSplits=5, shuffle=True, randomState=42)
testPreds = np.zeros(len(test))

for trainIdx, validx in kf.split(X, y):
    Xtr, ytr = X.iloc[trainIdx], y.iloc[trainIdx]
    
    model = RandomForestClassifier(
        nEstimators=100,
        maxDepth=6,          
        minSamplesSplit=20, 
        randomState=42
    )
    model.fit(Xtr, ytr)
    testPreds += model.predict_proba(Xtest)[:, 1] / kf.nSplits


test['ProbPago'] = testPreds
test['EsperanzaMatematica'] = (test['ProbPago'] * test['MontoSolicitado'] * test['TasaInteres']) - \
                               ((1 - test['ProbPago']) * test['MontoSolicitado'])


test = test.sortValues(by='EsperanzaMatematica', ascending=False)

presupuestoMaximo = 2000000
presupuestoAcumulado = 0
decisiones = []

for idx, row in test.iterrows():
    if presupuestoAcumulado + row['MontoSolicitado'] <= presupuestoMaximo:
        decisiones.append({'IDSolicitud': row['IDSolicitud'], 'Aprobado': 1})
        presupuestoAcumulado += row['MontoSolicitado']
    else:
        decisiones.append({'IDSolicitud': row['IDSolicitud'], 'Aprobado': 0})

dfSub = pd.DataFrame(decisiones)
dfSub.to_csv('submission.csv', index=False)
print("¡Archivo de envío generado correctamente sin superar el presupuesto!")