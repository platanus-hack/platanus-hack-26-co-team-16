# Makefile — team-16 · Simulador de cumplimiento de politica publica
# Dueno: Juanda (R5 · integracion/validacion). Ver docs/ROLES.md.
#
# Tres comandos. `make validate` es el que importa: imprime EL numero del backtest.
# Mientras una pieza no exista, su target dice la verdad en vez de fallar con un stack trace.

SHELL := /bin/bash
PY    ?= python3
SEED  ?= 42

.DEFAULT_GOAL := help
.PHONY: help run test validate reproduce estado

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

test:
	@if ! command -v pytest >/dev/null 2>&1; then \
		echo "PENDIENTE · make test — pytest no esta instalado (pip install pytest)."; \
	elif [ -z "$$(find tests -name 'test_*.py' -print -quit 2>/dev/null)" ]; then \
		echo "PENDIENTE · make test"; \
		echo "  No hay tests todavia. Los primeros cuatro estan enumerados en tests/README.md:"; \
		echo "  determinismo · el veto · fiscalizacion endogena · contratos."; \
		echo "  Se cablean con Manuel (R2) alrededor de H+6."; \
	else \
		pytest tests/ -q; \
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

reproduce:
	@if [ -f scripts/reproduce.py ]; then \
		$(PY) scripts/reproduce.py; \
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
	@n=$$(grep -rn "SUPUESTO:" engine behavior data api web scripts tests 2>/dev/null | wc -l | tr -d ' '); \
	 echo "    $$n en codigo · listarlos con: grep -rn \"SUPUESTO:\" engine behavior data api web"
	@echo ""
