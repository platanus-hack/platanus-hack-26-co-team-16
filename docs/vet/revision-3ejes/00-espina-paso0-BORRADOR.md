# Paso 0 · El problema — BORRADOR para pegar arriba de `docs/vet/02-la-idea-en-3-pasos.md`

> **Estado: borrador.** Lo escribió el agente de Manuel el 23-ago de madrugada leyendo el repo.
> Necesita 5 minutos del equipo para aprobarse o corregirse. **Toca `docs/vet/`, se avisa al grupo.**
> Hay **una decisión abierta** marcada abajo; es la única que no se puede tomar leyendo el repo.

---

## Quién tiene el problema

Quien firma un decreto de salario mínimo, y quien lo va a revisar en el Consejo de Estado.

Hoy, cuando se decide un aumento del 23%, la proyección oficial supone que **la política se cumple**.
Ese supuesto no se mide: se asume. La informalidad se conoce **un año después**, por encuesta, cuando
ya no hay nada que decidir. No existe forma ex-ante de decir **quién** no va a poder pagarlo.

Eso es lo que ningún dato disponible contesta hoy, y es la información que solo puede salir de una
simulación: no *"¿cuánta informalidad habrá?"* sino **"¿qué empleadores, con qué caja y en qué sector,
no tienen con qué cumplir?"**.

## Qué produce esta simulación que no se consigue de otra forma

**Un mapa ex-ante de quién absorbe el costo, y el número de qué tan equivocado está ese mapa.**

Dos piezas, y las dos son necesarias:

1. **El mapa.** 81 celdas de empleador reconstruidas de la GEIH del DANE, cada una con su caja
   mensual y su costo de despido calculado del Código Sustantivo del Trabajo. Un agente propone
   cómo adaptarse en un espacio **abierto**; un árbitro determinista veta lo que la aritmética no
   aguanta. Nadie que no tenga caja para indemnizar puede despedir, por convincente que suene.
2. **El error.** El criterio de éxito se escribió y se commiteó **antes** de bajar los datos con los
   que se iba a juzgar. El resultado se publicó salga como saliera, y salió mal: **37,37 pp de error,
   con el signo contrario**. La persistencia tonta le gana ocho veces.

## Por qué el error es el producto y no la vergüenza

Todo simulador de política pública entrega un número. **Ninguno entrega qué tan equivocado está.**
Por eso se usan como retórica y no como instrumento: son irrefutables por construcción.

Este entrega las dos cosas, y lo primero que hizo fue refutar su propio mecanismo estrella. Eso no
es un simulador que falló: es el único tipo de simulador con el que se puede discutir.

## Cómo cada paso sirve a esto

| Paso | Contesta | Sirve al problema porque |
|---|---|---|
| 0 · el problema | ¿a quién le duele? | fija contra qué se mide todo lo demás |
| 1 · la población no se inventa | ¿de dónde salen estos empleadores? | sin población real el mapa distributivo no significa nada |
| 2 · el modelo propone, la aritmética manda | ¿qué parte es difícil? | es lo que hace el mapa **factible** y no una lista de deseos del LLM |
| 3 · le pusimos número a nuestro error | ¿por qué creerte? | es la mitad del producto, no un descargo |

---

## ⚠️ La decisión abierta — 10 minutos de equipo, no se resuelve leyendo el repo

**Qué se afirma como resultado del proyecto.** Dos opciones, incompatibles:

- **(A) El aparato.** *"Traemos la máquina que le pone número al error de un simulador de política."*
  El mapa distributivo es la demostración de que la máquina corre. **Fuerte porque es cierto y
  verificable; débil porque un juez puede oír "construimos un simulador que no funciona".**
- **(B) El mapa.** *"Traemos el mapa ex-ante de quién no puede pagar el alza, con su banda y su error
  publicado."* **Fuerte porque es un producto con usuario; débil porque el backtest dice que el
  agregado que sale de ese mapa está mal por 37 pp, y hay que explicar por qué el reparto sirve
  aunque el total no.**

**Recomendación: (B) con (A) como defensa**, en ese orden y no al revés. El problema del Paso 0 pide
un mapa, no una máquina. Y el argumento de por qué el reparto puede servir aunque el nivel falle es
real y decible: el modelo no tiene canales positivos, así que su informalidad es **cota superior** —
está declarado en `VALIDATION.md` bloque D. Falla el nivel; el orden relativo de quién aprieta
primero no depende de los canales que faltan.

**Esa última frase hay que verificarla, no afirmarla.** Es exactamente lo que debe contestar la
revisión del eje B (fundamentación). Si no se sostiene, se cae a (A) sin drama.
