# 🍽️ umai-api

### Restaurant Management API — Backend en Python + Supabase

API REST para la gestión integral de restaurantes: reservas, platos, reseñas, servicios, métricas y autenticación.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-API-000000?style=for-the-badge&logo=flask)
![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=for-the-badge&logo=supabase)

---

## 📌 Características

- ✅ Gestión de reservas
- ✅ Gestión de platos (menú)
- ✅ Gestión de reseñas
- ✅ Gestión de servicios
- ✅ Métricas y reportes
- ✅ Autenticación de usuarios
- ✅ Integración con Supabase

---

## 🛠️ Stack Tecnológico

| Tecnología | Uso |
|---|---|
| Python 3.11 | Lenguaje del backend |
| Flask | Framework de la API |
| Supabase | Base de datos y servicios |
| Git/GitHub | Control de versiones |

---

## 📋 Requerimientos previos

- **Python 3.11+**
- **git**
- **Linux / Ubuntu / Debian** (o **Windows con WSL**), ya que el script `setup_python.sh` usa `apt`.
- Una cuenta y proyecto de **Supabase** (para las credenciales del `.env`).

> ℹ️ El script instala automáticamente `pip` y `venv` si no están presentes.

---

## 🚀 Instalación y Ejecución

### 1️⃣ Instalar dependencias y levantar la app

```bash
bash setup_python.sh
```

Este script:
- ✓ Instala `pip` o lo actualiza si es necesario
- ✓ Crea un entorno virtual aislado en la carpeta `venv/`
- ✓ Activa el entorno virtual y verifica que se haya activado correctamente
- ✓ Instala todas las dependencias **dentro del entorno virtual** desde `requirements.txt`
- ✓ Levanta la aplicación automáticamente

> 💡 Si le diste permisos de ejecución (`chmod +x setup_python.sh`), también podés correrlo con `./setup_python.sh`.

---

## 🔧 Ejecución manual

Si preferís hacer los pasos a mano:

```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Levantar la aplicación
python3 -m app

# Para desactivar el entorno virtual
deactivate
```

---

## 🌐 Acceso a la API

Una vez levantada, la API queda disponible en:

- **Base URL**: `http://localhost:5000`

---

## 🔗 Endpoints

La API se organiza en los siguientes grupos de recursos:

| Recurso | Prefijo | Descripción |
|---|---|---|
| Autenticación | `/auth` | Registro e inicio de sesión de usuarios |
| Reservas | `/reservas` | Gestión de reservas |
| Platos | `/platos` | Gestión del menú / platos |
| Reseñas | `/reseñas` | Gestión de reseñas |
| Servicios | `/servicios` | Gestión de servicios |
| Métricas | `/metricas` | Métricas y reportes |

---

## 📦 Dependencias

Las dependencias del proyecto están en `requirements.txt`:

- **Flask 3.0.3** — Framework web para crear la API
- **Flask-Cors 5.0.0** — Manejo de CORS
- **supabase 2.30.0** — Cliente oficial de Supabase
- **python-dotenv 1.0.1** — Carga de variables de entorno desde `.env`
- **psycopg2-binary 2.9.9** — Driver de PostgreSQL

---

## 📂 Estructura del Proyecto

```
umai-api/
├── app.py                   # Punto de entrada: crea la app Flask y registra los Blueprints
├── requirements.txt         # Dependencias del proyecto
├── setup_python.sh          # Script de instalación y ejecución (Linux/WSL)
├── .env.example             # Plantilla de variables de entorno
├── .gitignore
├── db/
│   ├── connection.py        # Conexión a la base de datos con psycopg2
│   └── supabase_client.py   # Cliente de conexión a Supabase
│   └── init_db.sql          # DDL: reseñas, reservas, clientes, etiquetas, plato_etiquetas, platos, usuarios y servicios
├── umai/
│   ├── routes/              # Blueprints con los endpoints
│   ├── services/            # Reglas de negocio
│   ├── validators/          # Validaciones de datos de entrada
│   ├── utils.py             # Utilidades generales
│   └── constants.py         # Constantes globales
├── README.md                # Este archivo
└── LICENSE                  # Licencia del proyecto
```

---

## 🌱 Convención de Ramas

```
feature/nombre-feature
feature/metricas_nombre-metrica
```

### Ejemplos

```
feature/crear_reserva
feature/metricas_ventas_mensuales
```

---

## 📝 Convención de Commits

| Commit | Descripción |
|---|---|
| `feat:` | Nueva funcionalidad |
| `fix:` | Corrección de errores |
| `refactor:` | Mejora interna del código |
| `perf:` | Optimización |
| `style:` | Formato y estilo |
| `docs:` | Documentación |
| `chore:` | Mantenimiento |

### Ejemplos

```
feat: agregar endpoint de reservas
fix: corregir validación de platos
docs: actualizar instalación
refactor: mejorar autenticación
```

---

## 📄 Licencia

Consultá el archivo [LICENSE](LICENSE) para más información.
