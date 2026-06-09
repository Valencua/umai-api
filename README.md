<div align="center">

# 🍽️ Restaurant Management API

### Backend desarrollado en Python + Supabase

API REST para la gestión integral de restaurantes:  
pedidos, productos, mesas, métricas y administración.

---

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)

![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=for-the-badge&logo=supabase)


</div>

---

# 📌 Características

✅ Gestión de pedidos  
✅ Gestión de productos  
✅ Métricas y reportes  
✅ Integración con Supabase  

---

# 🛠️ Stack Tecnológico

| Tecnología | Uso |
|---|---|
| Python | Backend |
| Flask | Framework API |
| Supabase | Base de datos y servicios |
| PostgreSQL | Persistencia de datos |
| Git/GitHub | Control de versiones |


---

# 🚀 Instalación

## 1️⃣ Clonar repositorio y crear rama o acceder rama

```bash
git clone https://github.com/Valencua/umai-api.git
cd umai-api
git branch tu_rama_nueva
git switch ru_rama_nueva
```

---

## 2️⃣ Ejecutar setup inicial de PYTHON

```bash
bash setup_python.sh
```
---

## 3️⃣ Activar el entorno virtual

```bash
source venv/bin/activate
```

---

## 4️⃣ Levantar el servidor

```bash
python3 -m app
```

---

# 📂 Estructura del Proyecto

```bash
📦 umai-api
┣ 📂 db
┃ ┣ 📜 __init__.py
┃ ┗ 📜 supabase_client.py
┣ 📂 umai
┃ ┣ 📂 routes
┃ ┣ 📂 services
┃ ┣ 📂 validators
┃ ┣ 📜 utils.py
┃ ┗ 📜 constants.py
┣ 📜 app.py
┣ 📜 requirements.txt
┣ 📜 .env
┣ 📜 .env.example
┣ 📜 .gitignore 
┗ 📜 README.md
```

---

# 🌱 Convención de Ramas

```bash
feature/nombre-feature
feature/metricas_nombre-metrica
```

### Ejemplos

```bash
feature/crear_pedido
feature/metricas_ventas_mensuales

```

---

# 📝 Convención de Commits

| Commit | Descripción |
|---|---|
| feat: | Nueva funcionalidad |
| fix: | Corrección de errores |
| refactor: | Mejora interna del código |
| perf: | Optimización |
| style: | Formato y estilo |
| docs: | Documentación |
| chore: | Mantenimiento |

---

## ✅ Ejemplos

```bash
feat: agregar endpoint de pedidos
fix: corregir validación de productos
docs: actualizar instalación
refactor: mejorar autenticación
```


