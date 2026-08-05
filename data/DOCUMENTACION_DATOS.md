# Manual y Diccionario de Datos Meteorologicos e Hidrometricos de Arequipa (Ano Completo 2025-2026)

## Red de Estaciones SENAMHI - Direccion Zonal 06 Arequipa

---

## 1. Introduccion al Dataset y Cobertura Temporal Anual

Este dataset reune la informacion geografica, climatica e hidrométrica de **30 estaciones meteorologicas e hidrometricas** representativas de la region de Arequipa, cubriendo un **periodo continuo de 1 AÑO COMPLETO (365 dias, del 01 de Agosto de 2025 al 31 de Julio de 2026)**.

La inclusion de un ciclo anual completo permite evaluar las **4 estaciones del ano** y las dinámicas estacionales extremas del sur peruano:

- **Verano (Enero a Marzo)**: Epoca de lluvias intensas, crecida de rios y tormentas electricas altiplanicas.
- **Otono (Abril a Mayo)**: Descenso paulatino de temperaturas e inicio de heladas nocturnas.
- **Invierno (Junio a Agosto)**: Temporada seca con heladas radiativas extremas (hasta -20 C en Imata) y baja humedad relativa.
- **Primavera (Septiembre a Diciembre)**: Radiacion solar maxima diurna (indices UV > 16) e incremento de temperatura.

La informacion esta organizada en 4 archivos CSV independientes:

1. **`estaciones.csv`**: Catalogo maestro geografico y ambiental de las 30 estaciones.
2. **`mediciones_hora.csv`**: Serie temporal meteorologica horaria de 365 dias continuos (**262,800 registros**).
3. **`mediciones_minuto.csv`**: Telemetria de alta resolucion (5 minutos) en ventanas estacionales de monitoreo rapido (**30,240 registros**).
4. **`mediciones_uv.csv`**: Registros diarios de Radiacion Ultravioleta (UVI) durante los 365 dias del ano (**23,725 registros**).

---

## 2. Analisis Climatico Profundo: Imata y la Red Altoandina

### A. Diagnostico del Microclima de Imata en el Ciclo Anual

La estacion de **Imata** (distrito de San Antonio de Chuca, Provincia de Caylloma, **4,519 msnm**, Coordenadas: `-15.83400, -71.08800`) constituye el punto de referencia clave para la alerta temprana ante heladas agrometeorologicas y variabilidad climatica en Arequipa.

- **Importancia Hidrologica**: Imata se ubica en la cabecera de cuenca del Rio Sumbay, afluente principal que da nacimiento al Rio Chili, el cual alimenta el sistema de represas (Aguada Blanca, El Frayle, Pillones) que abastece de agua potable e hidroelectricidad a la ciudad de Arequipa.
- **Heladas Radiativas de Invierno (Junio-Agosto)**: Durante los meses de junio, julio y agosto, la ausencia de nubosidad y la bajisima humedad relativa provocan una perdida acelerada de calor por radiacion terrena durante la noche. Las temperaturas minimas descienden rutinariamente a rangos de **-10 C a -20 C**, siendo uno de los puntos mas frios habitados del Peru.
- **Oscilacion Termica Diurna Extrema**: Debido a la menor densidad atmosferica a 4,500 msnm, el aire se calienta rapidamente bajo la radiacion solar diurna alcanzando +12 C a +15 C a las 13:00 horas, para luego desplomarse a -15 C a las 05:00 horas. Esta amplitud termica de **27 C a 30 C en menos de 18 horas** genera un estres fisiologico extremo en camelidos sudamericanos y vegetacion de bofedal.
- **Precipitaciones Solidas y Temporales de Verano (Enero-Marzo)**: En verano, la llegada de humedad proveniente de la cuenca amazonica interactua con la masa de aire frio andino, produciendo tormentas electricas de alta frecuencia, granizadas intensas y nevadas ("viento blanco").
- **Radiacion UV Extrema**: La atenuacion atmosferica es minima por la altitud, alcanzando indices UV superiores a **16.0 - 18.0** durante los meses de primavera y verano al mediodia solar.

---

### B. Caracterizacion de las Estaciones Altoandinas Similares a Imata

Las siguientes estaciones del dataset comparten altitud elevada, riesgo critico de heladas y comportamiento de puna fria:

1. **Crucero Alto** (4,520 msnm | San Antonio de Chuca, Caylloma):
   Punto altiplanico nival ubicado en la divisoria continental. Presenta el registro de temperaturas mas bajo de la red vial interoceanica Arequipa-Juliaca, afectando el transito terrestre por congelamiento de carpeta asfaltica.
2. **Condoroma** (4,625 msnm | Callalli, Caylloma):
   Estacion de mayor altitud de la red, ubicada junto al embalse del mismo nombre. Clima subpolar de alta montana donde las heladas se presentan durante los 365 dias del ano.
3. **Vincocaya** (4,380 msnm | San Antonio de Chuca, Caylloma):
   Ubicada en un abra o paso entre cerranias andinas. Experimenta vientos helados constantes que amplifican la sensacion termica por enfriamiento de viento (wind chill) desciendo la sensacion termica por debajo de -22 C.
4. **Pillones** (4,360 msnm | San Antonio de Chuca, Caylloma):
   Ubicada en las inmediaciones de la Represa Pillones. Monitorea la formacion de hielo superficial en la laguna de la represa y aportes hidricos por descongelamiento.
5. **Salinas** (4,300 msnm | San Juan de Tarucani, Arequipa):
   Ubicada en la depresion del Salar de la Reserva Nacional de Salinas y Aguada Blanca. Fenomeno de inversion termica severa en el fondo de la cuenca endorreica.
6. **Patahuasi** (4,200 msnm | Yanque, Caylloma):
   Estacion de control en la bifurcacion vial Arequipa-Puno-Cusco. Fundamental para el monitoreo de friajes y nevadas que interrumpen el transporte de carga interprovincial.
7. **Vizcachani** (4,310 msnm | Caylloma, Caylloma):
   Ubicada en la cuenca alta del Rio Colca, zona de influencia ganadera alpaquera y minera.
8. **Sumbay** (4,120 msnm | San Juan de Tarucani, Arequipa):
   Monitorea la estepa altiplanica de ichu y bofedales, punto critico para el pastoreo de vicunas y alpacas.
9. **Sibayo** (3,810 msnm) y **Callalli** (3,860 msnm):
   Estaciones de transicion entre la Puna y la cabecera del Valle del Colca, propensas a nevadas de inicio de estacion.
10. **Orcopampa** (3,780 msnm | Castilla):
    Ubicada en la zona alta del Valle de los Volcanes, expuesta a vientos catabaticos nocturnos descendentes de los nevados Firura y Coropuna.

---

### C. Caracterizacion de las Estaciones de Valle, Ciudad y Costa

1. **Valle del Colca y Cañones**:
   - **Chivay** (3,651 msnm | Caylloma): Estacion meteorologica del valle interandino alto. Monitorea heladas agrometeorologicas en cultivos de quinua, kiwicha y papas nativas.
   - **Cotahuasi** (2,680 msnm | La Union): Ubicada en el fondo del cañón mas profundo de America. Microclima templado-calido protegido del viento altiplanico.
   - **Pampacolca** (3,650 msnm | Castilla): Ladera sur del Nevado Coropuna, monitorea escorrentia de deshielo.
2. **Cuenca Media del Chili y Ciudad de Arequipa**:
   - **Chiguata** (2,970 msnm): Falda oriental del volcan Misti, monitorea precipitaciones pluviometricas que originan huaycos en las quebradas.
   - **Yura** (2,590 msnm): Zona desertica y de quebradas al noroccidente de la ciudad.
   - **Charcani** (2,610 msnm), **Puente del Diablo** (2,580 msnm) y **Tingo Grande** (2,180 msnm): Estaciones hidrometricas sobre el cauce de los rios Chili y Socabaya. Miden la altura de la lamina de agua en metros para prevenir desbordes e inundaciones urbanas durante el verano.
   - **Pampilla** (2,335 msnm), **Huasacache** (2,240 msnm), **Cayma** (2,400 msnm) y **San Francisco** (2,550 msnm): Estaciones de la campiña y zona urbana de Arequipa.
   - **UV Arequipa** (2,325 msnm): Estacion radiometrica especializada en medicion de espectro ultravioleta B.
3. **Pampas Costeras y Valles Secos**:
   - **Majes - El Pedregal** (1,410 msnm): Clima desertico subtropical arido con alta radiacion diurna y evaporacion.
   - **La Joya - San Camilo** (1,270 msnm) y **Bella Esperanza** (1,850 msnm): Valles de irrigacion agricola de exportacion.

---

## 3. Diccionario Detallado de Datos (Data Dictionary)

---

### Archivo 1: `estaciones.csv`

El archivo `estaciones.csv` constituye el catalogo maestro de referenciacion espacial y bioclimatica de la red.

| Nombre de Columna | Tipo de Dato      | Concepto y Descripcion                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Ejemplo de Valor                          |
| :---------------- | :---------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------- |
| `estacion_nombre` | Texto (String)    | Nombre oficial e inequivoco de la estacion meteorologica segun el catalogo nacional del SENAMHI. Sirve como clave de cruce con las mediciones.                                                                                                                                                                                                                                                                                                                             | `Imata`, `Patahuasi`, `Chivay`            |
| `tipo`            | Texto (Enum)      | Categoria operativa de la estacion:<br>- `REGULAR`: Estacion convencional o automatica meteorologica estandar.<br>- `EMA`: Estacion Meteorologica Automatica (sensores multiparametricos cada hora).<br>- `EPA`: Estacion Pluviometrica Automatica (enfocada en lluvia).<br>- `EHA`: Estacion Hidrométrica Automatica (medicion de nivel de rio).<br>- `UV`: Estacion dedicada a la medicion de radiacion ultravioleta.<br>- `HIDROMETRICA`: Medidor hidrologico de cauce. | `EMA`, `HIDROMETRICA`                     |
| `latitud`         | Flotante (Float8) | Coordenada de latitud geografica en grados decimales (Datum WGS84). Representa la posicion respecto al ecuador terrestre (valores negativos para el hemisferio sur).                                                                                                                                                                                                                                                                                                       | `-15.83400`                               |
| `longitud`        | Flotante (Float8) | Coordenada de longitud geografica en grados decimales (Datum WGS84). Representa la posicion al oeste del meridiano de Greenwich (valores negativos).                                                                                                                                                                                                                                                                                                                       | `-71.08800`                               |
| `altitud_msnm`    | Entero (Integer)  | Elevacion oficial sobre el nivel medio del mar expresada en metros (msnm). Determina el gradiente termico y la presion atmosferica.                                                                                                                                                                                                                                                                                                                                        | `4519`                                    |
| `provincia`       | Texto (String)    | Provincia politica del departamento de Arequipa a la que pertenece territorialmente la estacion.                                                                                                                                                                                                                                                                                                                                                                           | `Caylloma`, `Arequipa`, `Castilla`        |
| `distrito`        | Texto (String)    | Distrito administrativo dentro de la provincia donde esta instalada la estacion.                                                                                                                                                                                                                                                                                                                                                                                           | `San Antonio de Chuca`, `Yura`            |
| `zona_climatica`  | Texto (String)    | Descripcion sintetica de la region natural, piso ecologico, patron de humedad y severidad de riesgo de heladas.                                                                                                                                                                                                                                                                                                                                                            | `Puna Frigida / Heladas extremas (-18 C)` |

---

### Archivo 2: `mediciones_hora.csv`

El archivo `mediciones_hora.csv` contiene la serie temporal de parametros meteorologicos e hidrometricos consolidados cada hora durante **365 dias continuos**.

| Nombre de Columna    | Tipo de Dato | Unidad   | Rango Valido          | Concepto y Significado de la Variable                                                                                                                                                  |
| :------------------- | :----------- | :------- | :-------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `estacion_nombre`    | Texto        | N/A      | N/A                   | Nombre de la estacion coincidente con `estaciones.csv`.                                                                                                                                |
| `fecha`              | Timestamp    | ISO 8601 | `YYYY-MM-DD HH:MM:SS` | Fecha y hora exacta del registro (Hora Local Peru, UTC-5). Cobertura continua de 1 ano completo (2025-08-01 a 2026-07-31).                                                             |
| `temperatura_inst`   | Flotante     | C        | -25.0 C a 45.0 C      | **Temperatura Instantanea del Aire**: Muestra puntual tomada al minuto 60 a 2 metros de altura sobre el suelo.                                                                         |
| `temperatura_max`    | Flotante     | C        | -20.0 C a 48.0 C      | **Temperatura Maxima Horaria**: Valor mas alto registrado dentro de la ventana de 60 minutos.                                                                                          |
| `temperatura_min`    | Flotante     | C        | -30.0 C a 40.0 C      | **Temperatura Minima Horaria**: Valor mas bajo registrado en esa hora. En Imata permite detectar heladas nocturnas.                                                                    |
| `humedad_inst`       | Flotante     | %        | 0.0 % a 100.0 %       | **Humedad Relativa Instantanea**: Porcentaje de saturacion de vapor de agua. En invierno desciende a menos del 10-15%.                                                                 |
| `precipitacion_hora` | Flotante     | mm       | 0.0 mm a 150.0 mm     | **Precipitacion Horaria Acumulada**: Lluvia o equivalente de nieve caida en la hora (1 mm = 1 l/m²).                                                                                   |
| `precipitacion_dia`  | Flotante     | mm       | 0.0 mm a 400.0 mm     | **Precipitacion Diaria Acumulada**: Sumatoria continua caida durante el dia hidrologico.                                                                                               |
| `nivel_inst_m`       | Flotante     | m        | 0.00 m a 15.00 m      | **Nivel Instantaneo de Rio**: Altura de la lamina de agua en cauce medida por sensor radar ultrasonico. Muestra crecidas estivales en `Charcani`, `Puente del Diablo`, `Tingo Grande`. |
| `nivel_med_m`        | Flotante     | m        | 0.00 m a 15.00 m      | **Nivel Medio del Rio**: Promedio aritmetico del nivel durante la hora.                                                                                                                |
| `bateria_v`          | Flotante     | V        | 10.5 V a 15.0 V       | **Voltaje de Bateria Solar**: Tension en voltios de la bateria alimentada por panel fotovoltaico.                                                                                      |

---

### Archivo 3: `mediciones_minuto.csv`

El archivo `mediciones_minuto.csv` contiene telemetria de alta resolucion temporal (5 minutos) enfocada en avenidas de rio y tormentas intensas durante los 12 meses del ano.

| Nombre de Columna   | Tipo de Dato | Unidad   | Rango Valido          | Concepto y Significado de la Variable                                                      |
| :------------------ | :----------- | :------- | :-------------------- | :----------------------------------------------------------------------------------------- |
| `estacion_nombre`   | Texto        | N/A      | N/A                   | Nombre de la estacion de monitoreo rapido.                                                 |
| `fecha`             | Timestamp    | ISO 8601 | `YYYY-MM-DD HH:MM:SS` | Marca de tiempo en bloques de 5 minutos durante el ciclo anual.                            |
| `precipitacion_min` | Flotante     | mm       | 0.00 mm a 25.00 mm    | **Precipitacion en 5 Minutos**: Agua caida durante la ventana de 300 segundos.             |
| `intensidad_min`    | Flotante     | mm/h     | 0.0 mm/h a 200.0 mm/h | **Intensidad Instantanea de Lluvia**: Tasa proyectada a 1 hora (`precipitacion_min * 12`). |
| `nivel_inst_m`      | Flotante     | m        | 0.00 m a 15.00 m      | **Nivel de Cauce en Tiempo Real**: Cota de rio en metros para alerta de crecidas.          |
| `bateria_v`         | Flotante     | V        | 10.5 V a 15.0 V       | **Voltaje del Sistema**: Estado de energia del nodo transmisor.                            |

---

### Archivo 4: `mediciones_uv.csv`

El archivo `mediciones_uv.csv` registra la radiacion ultravioleta B diaria (06:00 a 18:00 h) durante los 365 dias del ano.

| Nombre de Columna | Tipo de Dato | Unidad        | Rango Valido                                                  | Concepto y Significado de la Variable                                                                                                                           |
| :---------------- | :----------- | :------------ | :------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `estacion_nombre` | Texto        | N/A           | N/A                                                           | Nombre de la estacion radiometrica.                                                                                                                             |
| `fecha`           | Timestamp    | ISO 8601      | `YYYY-MM-DD HH:MM:SS`                                         | Fecha y hora de lectura UV diurna.                                                                                                                              |
| `indice_uv`       | Flotante     | UVI           | 0.0 a 20.0+                                                   | **Indice de Radiacion Ultravioleta (UVI)**: Intensidad de radiacion eritematica. Alcanza picos maximos en verano y primavera.                                   |
| `categoria_uv`    | Texto        | Categoria OMS | `Bajo`, `Moderado`, `Alto`, `Muy Alto`, `Extremadamente Alto` | **Clasificacion OMS**:<br>- `0.0 - 2.9`: Bajo<br>- `3.0 - 5.9`: Moderado<br>- `6.0 - 7.9`: Alto<br>- `8.0 - 10.9`: Muy Alto<br>- `>= 11.0`: Extremadamente Alto |
