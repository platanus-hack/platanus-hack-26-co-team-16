# Makefile — team-16 · Simulador de cumplimiento de politica publica
# Dueno: Juanda (R5 · integracion/validacion). Ver docs/ROLES.md.
#
# Tres comandos. `make validate` es el que importa: imprime EL numero del backtest.
# Mientras una pieza no exista, su target dice la verdad en vez de fallar con un stack trace.

SHELL := /bin/bash
# Si existe el venv del proyecto se usa ESE, que es donde estan las dependencias
# (pandas, pyarrow, anthropic, fastapi). El python3 del sistema suele tener solo
# una parte, y entonces el target pasaba el chequeo y reventaba mas adelante
# leyendo el parquet. Se puede forzar otro con `make PY=/ruta/a/python3`.
PY    ?= $(shell [ -x .venv/bin/python3 ] && echo .venv/bin/python3 || echo python3)
SEED  ?= 42

.DEFAULT_GOAL := help
.PHONY: help run determinismo calibracion test validate reproduce estado supuestos \
        servidor enjambre humo

help:
	@echo ""
	@echo "  team-16 · Simulador de cumplimiento de politica publica"
	@echo ""
	@echo "  make run        Corre una simulacion completa (seed=$(SEED), \$$0, sin API key)"
	@echo "  make determinismo  Dos corridas y compara: la prueba de AGENTS.md"
	@echo "  make calibracion   La corrida SIN politica que pide la compuerta G3"
	@echo "  make test       Tests del nucleo determinista"
	@echo "  make validate   Los 4 candados de validacion e imprime EL numero"
	@echo "  make reproduce  Reproduce el resultado principal con un comando"
	@echo "  make estado     Que esta cableado y que no"
	@echo "  make servidor   La API del enjambre (uvicorn :8000, SSE por ronda)"
	@echo "  make enjambre   El frontend (Next.js :3000; requiere make servidor aparte)"
	@echo "  make humo       Humo contra el deploy: make humo URL=https://..."
	@echo ""
	@echo "  Documentacion: AGENTS.md · VALIDATION.md · docs/PLAN.md"
	@echo ""

# Corre por la ABLACION determinista: $0, sin API key y sin red. El camino del
# producto (LLM) se corre desde la API (`make servidor`); este target existe para
# que un jurado que acaba de clonar el repo pueda teclear algo y ver la corrida.
run:
	$(PY) scripts/run_simulacion.py --seed $(SEED)

# La prueba que AGENTS.md promete: "mismo seed, mismo resultado, verificable
# corriendo make run dos veces". Estaba enunciada y no habia forma de correrla.
determinismo:
	@echo "  dos corridas con seed=$(SEED), comparando el artefacto canonico..."
	@$(PY) scripts/run_simulacion.py --seed $(SEED) --solo-hash > .det.a
	@$(PY) scripts/run_simulacion.py --seed $(SEED) --solo-hash > .det.b
	@if diff -q .det.a .det.b >/dev/null; then \
		echo "  IDENTICO · sha256 $$(cat .det.a)"; rm -f .det.a .det.b; \
	else \
		echo "  DISTINTO: $$(cat .det.a) contra $$(cat .det.b)"; \
		rm -f .det.a .det.b; exit 1; \
	fi

# La corrida SIN politica que pide la compuerta G3 de VALIDATION.md.
calibracion:
	$(PY) scripts/run_simulacion.py --seed $(SEED) --aumento 0

# Los tests del nucleo viven en `engine/` y `behavior/`, no solo en `tests/`:
# cada duenio los escribe en su carpeta. Este target los corria solo desde
# `tests/` e imprimia "No hay tests todavia" mientras 58 pasaban en `engine/`.
# Tambien se saltaba `api/`, asi que `make test` decia 95 y la suite que el
# equipo corre a mano decia 111: dos cuentas distintas de lo mismo.
test:
	@if ! command -v pytest >/dev/null 2>&1; then \
		echo "PENDIENTE · make test — pytest no esta instalado (pip install -r requirements.txt)."; \
	else \
		pytest engine/ api/ tests/ -q; \
		echo ""; \
		echo "  regresiones de behavior/ (no son pytest, corren solas):"; \
		$(PY) -m behavior.pruebas | tail -3; \
	fi

# Sale con codigo 1 mientras haya compuertas fuera de PASA, y eso es a proposito.
# `make validate ARGS=--dry` hace la pasada seca (no corre simulaciones).
validate:
	$(PY) scripts/validate.py $(ARGS)

# C4 — corre en una maquina limpia SIN API key. Importa la cache versionada del
# escenario demo si existe; si no, cae a la ablacion, que es determinista sin
# depender de nada externo. Es el nivel 2 (y el 3) de la ADR 0009.
reproduce:
	@if [ -f scripts/reproduce.py ]; then \
		$(PY) scripts/reproduce.py --seed $(SEED); \
	else \
		echo "PENDIENTE · make reproduce — llega junto con el numero de validacion (C5)."; \
	fi

estado:
	@echo ""
	@echo "  Que esta cableado:"
	@for f in Makefile README.md AGENTS.md ARCHITECTURE.md VALIDATION.md LICENSE \
	          scripts/run_simulacion.py scripts/validate.py scripts/reproduce.py \
	          data/poblacion.parquet data/momentos.json \
	          artefactos/corrida.json artefactos/corrida.manifiesto.json \
	          artefactos/calibracion_base.json; do \
		if [ -e "$$f" ]; then echo "    [x] $$f"; else echo "    [ ] $$f"; fi; \
	done
	@echo ""
	@echo "  Supuestos tomados en el codigo (informe de honestidad):"
	@n=$$(grep -rnI --exclude-dir=__pycache__ "SUPUESTO:" engine behavior data api web scripts tests 2>/dev/null | wc -l | tr -d ' '); \
	 echo "    $$n en codigo · listarlos con: make supuestos"
	@echo ""

# La interfaz: dos procesos, la API del motor y el frontend del enjambre.
# Se corren en dos terminales (make servidor / make enjambre).
servidor:
	@$(PY) -c "import fastapi, uvicorn, pandas, pyarrow, anthropic" 2>/dev/null || { \
		echo "PENDIENTE · make servidor — faltan dependencias en $(PY)."; \
		echo "  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"; \
		exit 1; }
	@echo "  API del enjambre en http://localhost:8000 · Ctrl-C para parar"
	@if [ -z "$$ANTHROPIC_API_KEY" ]; then \
		echo "  OJO: sin ANTHROPIC_API_KEY. El modo LLM caera a cache, y sin cache dara error."; \
	fi
	$(PY) -m uvicorn api.servidor:app --port 8000

enjambre:
	@if [ ! -d web/enjambre/node_modules ]; then \
		echo "  instalando dependencias de web/enjambre (primera vez)..."; \
		cd web/enjambre && npm install --no-audit --no-fund; \
	fi
	cd web/enjambre && npm run dev

# ¿La URL desplegada transmite una corrida de verdad? La home puede cargar
# perfecto con el motor caído: esto abre el SSE y verifica que las rondas
# cierran. Corre la ablación determinista, así que cuesta $0 y se puede repetir
# cuantas veces haga falta. `LLM=1` corre el camino del producto y SÍ gasta.
humo:
	@if [ -z "$(URL)" ]; then \
		echo ""; \
		echo "  uso: make humo URL=https://enjambre-web-xxxx.onrender.com"; \
		echo "       make humo URL=... LLM=1   # el camino del producto (gasta creditos)"; \
		echo ""; \
		echo "  El runbook completo del deploy esta en docs/DEPLOY.md"; \
		echo ""; \
		exit 1; \
	fi
	@"$(PY)" scripts/humo_deploy.py $(URL) $(if $(LLM),--llm,)

# El informe de honestidad del proyecto, con UN solo comando.
#
# `-I` ignora binarios y `--exclude-dir=__pycache__` salta el bytecode: sin eso el
# conteo contaba los `.pyc` y daba un numero distinto segun si alguien habia
# corrido Python antes (54 o 94, segun quien lo corriera). Un informe de
# honestidad que no es reproducible no sirve para nada.
supuestos:
	@grep -rnI --exclude-dir=__pycache__ "SUPUESTO:" engine behavior data api web scripts tests 2>/dev/null || true
	@echo ""
	@echo "  total: $$(grep -rnI --exclude-dir=__pycache__ "SUPUESTO:" engine behavior data api web scripts tests 2>/dev/null | wc -l | tr -d ' ') supuestos declarados"
