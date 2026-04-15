# ⚡ QUICK START - Dashboard en 5 Minutos

**Guía express para tener el dashboard corriendo AHORA**

---

## 🚀 OPCIÓN A: Streamlit Cloud (Recomendado - 5 min)

### Paso 1: Fork en GitHub (1 min)
```
1. Ve a GitHub
2. Busca tu repo
3. Click "Fork"
4. Espera a que termine
```

### Paso 2: Conectar a Streamlit Cloud (2 min)
```
1. Ve a https://share.streamlit.io
2. Click "New app"
3. Selecciona:
   - Repo: tu-fork
   - Branch: main
   - File: app.py
4. Click "Deploy"
```

### Paso 3: Agregar API Key (1 min)
```
1. Streamlit app → Settings (arriba a la derecha)
2. Advanced settings
3. Secrets
4. Pega esto:
   NEWSAPI_KEY=abc123
5. Click Save
```

### Paso 4: Inicializar datos (1 min)
En tu PC:
```bash
python init_sample_data.py
git add data/dashboard.db
git commit -m "Initial data"
git push
```

Espera ~30 segundos → **Dashboard listo!**

**Tu URL pública:** `https://geopolitical-dashboard-[nombre].streamlit.app`

→ **Compartible con quien quieras (sin software necesario)**

---

## 💻 OPCIÓN B: Local (Si no quieres Streamlit Cloud)

```bash
# 1. Clonar
git clone https://github.com/tu-usuario/geopolitical-risk-dashboard.git
cd geopolitical-risk-dashboard

# 2. Setup Python
python -m venv venv
source venv/bin/activate  # O: venv\Scripts\activate (Windows)
pip install -r requirements.txt

# 3. Configurar
echo "NEWSAPI_KEY=abc123" > .env

# 4. Datos iniciales
python init_sample_data.py

# 5. Ejecutar
streamlit run app.py
```

Abre en navegador: **http://localhost:8501**

---

## 📊 USAR EL DASHBOARD

### Página 1: Resumen (LEER PRIMERO)
- **Score de riesgo** (0-100)
- **Nivel** (BAJO/MEDIO/ALTO/CRÍTICO)
- **KPIs** principales (Brent, WTI)
- **Top 3 noticias del día**
- **Conclusión automática**

### Página 2: Petróleo
- Gráfico histórico 12 meses
- Cambios vs 1d, 7d, 30d
- Volatilidad

### Página 3: Polymarket
- Probabilidades implícitas
- Mercados de riesgo

### Página 4: Noticias
- Últimas noticias relevantes
- Impacto estimado

### Página 5: Análisis
- Desacoplamiento petróleo vs riesgo
- Alertas
- Metodología

---

## 🔑 Obtener NEWSAPI_KEY (Gratuito)

```
1. Ve a https://newsapi.org
2. Click "Register"
3. Crea cuenta gratuita
4. Copia tu API key
5. Pégalo en .env o Streamlit Secrets
```

---

## ✅ Verificar que Funciona

En tu navegador, deberías ver:

✅ Score de riesgo (número 0-100)
✅ Gráficos históricos
✅ Tabla de noticias
✅ Métricas de Brent/WTI

Si ves todo → **¡Felicidades, está corriendo!**

---

## 📱 Compartir (Lo Mejor)

### Si usaste Streamlit Cloud:
Tu URL pública = `https://app-name.streamlit.app`

**Envía esto a quien quieras:**
```
Ey, revisa el dashboard de riesgo geopolítico:
https://app-name.streamlit.app

No necesita instalar nada, solo abre en navegador.
```

### Si es local:
Necesitas VPS o exponer puerto (más complejo)

---

## 🔄 Auto-Actualización (Opcional)

Si quieres que se actualice automáticamente:

1. Copiar archivos `.github/workflows/` a tu repo
2. Agregarlos con git
3. Fazer push
4. Streamlit Cloud lo ejecutará automáticamente

Si no, actualiza manualmente:
```bash
python fetch_oil_prices.py
python fetch_polymarket.py
python fetch_news.py
python calculate_scores.py
```

---

## 🆘 Si Algo Falla

### "No hay datos"
```bash
python init_sample_data.py
git add data/dashboard.db
git commit -m "Fix: add sample data"
git push
```

### "NEWSAPI_KEY error"
- Verifica que la clave esté bien copiada
- No incluyas comillas: `abc123` (no `"abc123"`)
- Espera ~1 minuto después de agregar el secret

### "Connexión rechazada"
- Verifica conexión a internet
- Prueba desde otra red

### "Streamlit Cloud dice 'App unhealthy'"
- Settings → Advanced → Restart
- Espera 1 minuto
- Si sigue: Settings → Rerun

---

## 📞 Contacto

Si algo no funciona: **jcdelrio2000@gmail.com**

---

**¡Listo! Disfruta tu dashboard profesional de riesgo geopolítico 🎉**
