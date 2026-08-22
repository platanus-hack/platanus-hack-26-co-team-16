# Makefile — team-16 · Simulador de cumplimiento de politica publica
# Dueno: Juanda (R5 · integracion/validacion). Ver docs/ROLES.md.
#
# Tres comandos. `make validate` es el que importa: imprime EL numero del backtest.
# Mientras una pieza no exista, su target dice la verdad en vez de fallar con un stack trace.

SHELL := /bin/bash
PY    ?= python3
SEED  ?= 42

.DEFAULT_GOAL := help
.PHONY: help run test validate reproduce estado supuestos

help:
	@echo ""
	@echo "  team-16 · Simulador de cumplimiento de politica publica"
	@echo ""
	@echo "  make run        Corre una simulacion completa (seed=$(SEED))"
	@echo "  make test       Tests del nucleo determinista"
	@echo "  make validate   Los 4 candados de validacion e imprime EL numero"
	@echo "  make reproduce  Reproduce el resultado principal con un comando"
	@echo "  make estado     Que esta cableado y que no"
	@echo ""
	@echo "  Documentacion: AGENTS.md · VALIDATION.md · docs/PLAN.md"
	@echo ""

run:
	@if [ -f scripts/run_simulacion.py ]; then \
		$(PY) scripts/run_simulacion.py --seed $(SEED); \
	else \
		echo "PENDIENTE · make run"; \
		echo "  Falta: scripts/run_simulacion.py (R5) sobre engine/ (R2, Manuel)."; \
		echo "  Se cablea en el checkpoint C3 (H+10): la corrida punta a punta."; \
		echo "  Mientras tanto la referencia del flujo es docs/FLUJO.md."; \
	fi

# Los tests del nucleo viven en `engine/` y `behavior/`, no solo en `tests/`:
# cada duenio los escribe en su carpeta. Este target los corria solo desde
# `tests/` e imprimia "No hay tests todavia" mientras 58 pasaban en `engine/`.
test:
	@if ! command -v pytest >/dev/null 2>&1; then \
		echo "PENDIENTE · make test — pytest no esta instalado (pip install -r requirements.txt)."; \
	else \
		pytest engine/ tests/ -q; \
		echo ""; \
		echo "  regresiones de behavior/ (no son pytest, corren solas):"; \
		$(PY) -m behavior.pruebas | tail -3; \
	fi

validate:
	@if [ -f scripts/validate.py ]; then \
		$(PY) scripts/validate.py; \
	else \
		echo ""; \
		echo "  VALIDACION — sin datos aun."; \
		echo ""; \
		echo "  EL numero del backtest existe en el checkpoint C5 (H+20 a H+26)."; \
		echo "  Se publica salga como salga: un error grande medido y reportado"; \
		echo "  vale mas que una cifra que nadie puede refutar."; \
		echo ""; \
		echo "  Los 4 candados y su estado: VALIDATION.md"; \
		echo "  Metodologia completa:      docs/PLAN.md seccion 5"; \
		echo ""; \
	fi

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
	          data/poblacion.parquet data/momentos.json; do \
		if [ -e "$$f" ]; then echo "    [x] $$f"; else echo "    [ ] $$f"; fi; \
	done
	@echo ""
	@echo "  Supuestos tomados en el codigo (informe de honestidad):"
	@n=$$(grep -rnI --exclude-dir=__pycache__ "SUPUESTO:" engine behavior data api web scripts tests 2>/dev/null | wc -l | tr -d ' '); \
	 echo "    $$n en codigo · listarlos con: make supuestos"
	@echo ""

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
