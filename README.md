# mp4

Repo de prueba para indexación.

## Licitaciones

El script `fetch_licitaciones.py` obtiene las licitaciones desde la API pública de Mercado Publico y genera un archivo `licitaciones.csv` con información básica.
Además, para cada licitación consulta la ficha pública para extraer el estado y la descripción.

Para usarlo primero define la variable de entorno con tu API key y luego ejecuta el script:

```bash
export MERCADOPUBLICO_API_KEY="<tu_api_key>"
python fetch_licitaciones.py
```

El resultado será un archivo CSV con las columnas `CodigoExterno`, `Nombre`, `CodigoEstado` y `FechaCierre`.
Adicionalmente incluye las columnas `Estado` y `Descripcion` obtenidas mediante _scraping_.

Para ejecutarlo de forma automática cada hora al minuto 00, utiliza el script `run_fetch.sh` y agrega la siguiente línea a tu crontab:

```bash
0 * * * * MERCADOPUBLICO_API_KEY=<tu_api_key> /ruta/al/repositorio/run_fetch.sh
```

El script `run_fetch.sh` ejecuta `fetch_licitaciones.py` desde el directorio del repositorio. Cron ejecutará la tarea cada hora en punto.

## Login System

La aplicación `app.py` ofrece un sistema de registro, inicio de sesión y recuperación de contraseña.

### Configuración

1. Instala las dependencias:

```bash
pip install -r requirements.txt
```

2. Define las variables de entorno necesarias:

```bash
export SECRET_KEY="cambia-esto"
export SMTP_SERVER="smtp.ejemplo.com"
export SMTP_PORT="587"
export SMTP_USERNAME="usuario@ejemplo.com"
export SMTP_PASSWORD="password"
```

Si no configuras el envío de correos, el enlace de recuperación se mostrará por consola.

3. Ejecuta la aplicación:

```bash
python app.py
```

Al iniciar, se creará una base de datos SQLite `users.db` y la interfaz estará disponible en `http://localhost:5000/`.
