from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
import numpy as np

# Función para cargar datos
def load_data():
    df = pd.read_csv(r"C:\Users\David MIranda A\Desktop\proyecto_final_bcia\datos_infracciones.csv")
    return df

# Llamamos a la función para cargar los datos y asignarlos a 'df'
df = load_data()

# Definir variables de normalización
ingreso_maximo = df["Ingreso_estimado"].max()
estrato_maximo = 6  # Suponiendo que el estrato máximo es 6
tarifa_maxima = df["Tarifa_servicios_publicos"].max()

# Agregar columna para indicar si realizó capacitación
df["Capacitacion_realizada"] = np.random.choice([True, False], size=len(df))

# Función para calcular el pago con descuento por capacitación
def calcular_pago_con_descuento(row):
    if row["Estrato_socioeconomico"] <= 3:
        # Estratos 1 a 3: pagan el 100% de la multa y deben hacer curso obligatorio
        return row["Valor_multa"]
    else:
        # Estratos 4 a 6: se aplica un ajuste según los factores
        factor_ingreso = row["Ingreso_estimado"] / ingreso_maximo
        factor_estrato = row["Estrato_socioeconomico"] / estrato_maximo
        factor_tarifa = row["Tarifa_servicios_publicos"] / tarifa_maxima

        porcentaje_pago = factor_ingreso * factor_estrato * factor_tarifa
        porcentaje_pago = max(0.10, min(porcentaje_pago, 1.0))
        pago_base = row["Valor_multa"] * porcentaje_pago

        # Aplicar descuento del 20% si realizó la capacitación
        if row["Capacitacion_realizada"]:
            pago_base *= 0.80  # Descuento del 20%

        return pago_base

# Aplicar el cálculo para obtener el pago final
df["Pago_final"] = df.apply(calcular_pago_con_descuento, axis=1)

# Definir la API con FastAPI
app = FastAPI()

@app.get("/", response_class=JSONResponse)
async def root():
    return {"message": "Propuesta de pago para tu multa de tránsito"}

@app.get("/multa/{id}", response_class=JSONResponse)
async def obtener_multa(id: int):
    multa = df[df["ID"] == id]
    if multa.empty:
        raise HTTPException(status_code=404, detail="Multa no encontrada")
    multa_dict = multa.to_dict(orient="records")[0]
    return multa_dict
