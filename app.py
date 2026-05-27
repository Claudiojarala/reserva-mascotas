import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd

# 1. Simulación de Datos (Capa de Datos temporal para Claudio)
# Representa el calendario de reservas y las restricciones alimentarias (dietas)
reservas_iniciales = [
    {
        "id_reserva": 101, 
        "mascota": "Rango (Iguana Verde)", 
        "dueño": "Ismael Ponce", 
        "fecha_ingreso": "2026-06-01", 
        "dieta_restriccion": "Estricta: Solo hojas de mostaza, calabacín y calcio. NO insectos."
    },
    {
        "id_reserva": 102, 
        "mascota": "Snape (Pizón de Bola)", 
        "dueño": "Carlos Mendoza", 
        "fecha_ingreso": "2026-06-03", 
        "dieta_restriccion": "1 ratón descongelado de tamaño mediano cada 10 días."
    },
    {
        "id_reserva": 103, 
        "mascota": "Pelusa (Tarántula de Rodillas Rojas)", 
        "dueño": "Ana Delgado", 
        "fecha_ingreso": "2026-06-05", 
        "dieta_restriccion": "2 grillos vivos por semana. Monitorear humedad al 70%."
    },
]
df_reservas = pd.DataFrame(reservas_iniciales)

# 2. Inicializar la Aplicación de Dash
app = dash.Dash(__name__, title="Control Guardería Exótica")

# 3. Diseño de la Interfaz Visual (Frontend de la Capa de Aplicación)
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'backgroundColor': '#fcfaf7'}, children=[
    
    html.H1("Plataforma de Gestión: Guardería de Animales Exóticos 🦎🦉", style={'textAlign': 'center', 'color': '#2c3e50'}),
    html.Hr(),
    
    # Formulario para agendar o actualizar restricciones alimentarias
    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '20px', 'boxShadow': '0px 2px 4px rgba(0,0,0,0.05)'}, children=[
        html.H3("Programar Cita de Cuidado / Actualizar Dieta Específica", style={'marginTop': '0', 'color': '#16a085'}),
        
        html.Div(style={'display': 'flex', 'gap': '15px', 'flexWrap': 'wrap'}, children=[
            html.Div([
                html.Label("ID Reserva:"), html.Br(),
                dcc.Input(id='input-id-reserva', type='number', placeholder='Ej. 104', style={'padding': '8px', 'width': '100px'})
            ]),
            html.Div([
                html.Label("Mascota y Especie:"), html.Br(),
                dcc.Input(id='input-mascota', type='text', placeholder='Ej. Spike (Erizo)', style={'padding': '8px', 'width': '200px'})
            ]),
            html.Div([
                html.Label("Dueño:"), html.Br(),
                dcc.Input(id='input-dueno', type='text', placeholder='Ej. Juan Pérez', style={'padding': '8px', 'width': '150px'})
            ]),
            html.Div([
                html.Label("Fecha Ingreso:"), html.Br(),
                dcc.Input(id='input-fecha', type='text', placeholder='AAAA-MM-DD', style={'padding': '8px', 'width': '120px'})
            ]),
            html.Div([
                html.Label("Restricción Alimentaria / Dieta:"), html.Br(),
                dcc.Input(id='input-dieta', type='text', placeholder='Detalles de alimentación...', style={'padding': '8px', 'width': '350px'})
            ]),
            html.Button('Registrar Reserva', id='btn-registrar', n_clicks=0, style={
                'backgroundColor': '#16a085', 'color': 'white', 'border': 'none', 'padding': '10px 20px', 'borderRadius': '4px', 'cursor': 'pointer', 'alignSelf': 'flex-end'
            })
        ]),
        html.Div(id='output-mensaje-reserva', style={'marginTop': '15px', 'fontWeight': 'bold', 'color': '#27ae60'})
    ]),
    
    # Tabla del Calendario de Reservas Activas
    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0px 2px 4px rgba(0,0,0,0.05)'}, children=[
        html.H3("Calendario de Reservas y Dietas Activas", style={'marginTop': '0', 'color': '#2c3e50'}),
        dash_table.DataTable(
            id='tabla-reservas',
            columns=[
                {"name": "ID Reserva", "id": "id_reserva"},
                {"name": "Mascota (Especie)", "id": "mascota"},
                {"name": "Dueño / Contacto", "id": "dueño"},
                {"name": "Fecha de Ingreso", "id": "fecha_ingreso"},
                {"name": "Restricción Alimentaria / Dieta", "id": "dieta_restriccion"}
            ],
            data=df_reservas.to_dict('records'),
            style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
            style_cell={'padding': '12px', 'textAlign': 'left', 'whiteSpace': 'normal', 'height': 'auto'},
            style_data_conditional=[{
                'if': {'column_id': 'dieta_restriccion', 'filter_query': '{dieta_restriccion} contains "Estricta"'},
                'backgroundColor': '#fff2cc', 'color': '#b78103', 'fontWeight': 'bold'
            }]
        )
    ])
])

# 4. Lógica del Servidor / Callbacks (Backend de la Capa de Aplicación)
@app.callback(
    [Output('tabla-reservas', 'data'),
     Output('output-mensaje-reserva', 'children')],
    Input('btn-registrar', 'n_clicks'),
    [State('input-id-reserva', 'value'),
     State('input-mascota', 'value'),
     State('input-dueno', 'value'),
     State('input-fecha', 'value'),
     State('input-dieta', 'value')]
)
def gestionar_reservas(n_clicks, id_res, masc, owner, date, dieta):
    global df_reservas
    if n_clicks == 0 or id_res is None or not masc or not owner or not date or not dieta:
        return df_reservas.to_dict('records'), ""
    
    # Validar si el ID de reserva ya existe
    if id_res in df_reservas['id_reserva'].values:
        return df_reservas.to_dict('records'), f"❌ Error: El ID de Reserva {id_res} ya está ocupado."
    
    # Crear nueva fila (Simulación de INSERT en BD Relacional)
    nueva_reserva = {
        "id_reserva": id_res,
        "mascota": masc,
        "dueño": owner,
        "fecha_ingreso": date,
        "dieta_restriccion": dieta
    }
    
    # Añadir al DataFrame
    df_reservas = pd.concat([df_reservas, pd.DataFrame([nueva_reserva])], ignore_index=True)
    
    return df_reservas.to_dict('records'), f"✅ Reserva {id_res} registrada con éxito para la mascota {masc}."

# 5. Ejecutar Servidor
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)