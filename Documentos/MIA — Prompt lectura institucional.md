# MIA — Prompt para la "Lectura de Libertad y Progreso"

El generador `00_Comun/generar_reporte_mensual.py` arma el reporte mensual **completo y
automático** (cifras, tablas y los 3 gráficos: consolidado, ejes y núcleo) y deja **una sola
sección para escribir a mano**: *"5. La lectura de Libertad y Progreso"*. Este prompt sirve
para redactarla en la voz institucional (con Claude o a mano). Es el único paso no automático.

## Cómo usarlo
1. Abrí el reporte del mes (`Documentos/MIA — Reporte Mensual (<Mes AAAA>).docx`) y mirá el
   Resumen ejecutivo, las tablas (ejes + variables) y la "Lectura de los datos" automática.
2. Pasale a Claude el prompt de abajo + esos datos (o pedile que lea `output/mia_mensual.csv`).
3. Reemplazá el placeholder de la sección 5 por el texto que devuelva.

## Prompt

> Actuá como el Departamento de Políticas Públicas de la Fundación Libertad y Progreso (usá la
> habilidad **`lyp-pp`**: primera persona del plural, liberalismo clásico, asertiva y pedagógica).
> Escribí la sección **"La lectura de Libertad y Progreso"** del reporte mensual del MIA para
> **{MES AAAA}**, en 2 a 4 párrafos de prosa (sin viñetas).
>
> Datos del mes:
> - MIA {mes} = {valor} ({provisional/cerrado}); variación vs. mes anterior {Δ}; interanual {Δaa}.
> - Ejes (nivel y Δ): Ejecutivo …, Legislativo …, Judicial …, Prensa …, Banco Central ….
> - Variables que más se movieron: {lista con Δ}.
>
> Pautas:
> - Leé el mes desde el criterio liberal: gobierno limitado, frenos y contrapesos, reglas
>   debatidas en el Congreso y no por decreto, independencia y celeridad judicial, disciplina
>   monetaria (la inflación es un fenómeno monetario), libertad de prensa.
> - Explicá QUÉ eje o variable movió el índice y POR QUÉ importa institucionalmente; no repitas
>   las cifras, interpretalas.
> - Si el mes es **provisional**, aclaralo y no sobreinterpretes variaciones chicas.
> - Es **medición e investigación, no militancia**: describí y evaluá, no reclames una política
>   concreta (encuadre no-lobbying, clave para el financiamiento).
> - Cerrá con una lectura de fondo (hacia dónde va la calidad republicana), sin exagerar un mes.
>
> Devolvé solo los párrafos de la sección, listos para pegar.

## Nota
El valor publicado del MIA es 100% determinístico y sin IA. La IA/redacción se usa **solo** para
esta lectura y la difusión — nunca toca el número. (Ver AGENTS.md → "Capa de IA".)
