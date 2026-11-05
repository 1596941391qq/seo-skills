# EveryInfra SEO Skills

<!-- rq223-banner -->
<p align="center"><img alt="EveryInfra SEO Skills — Skills gratuitas de SEO y GEO global para Claude Code, Codex y 10 hosts" src="assets/banner-es.jpg" width="100%"></p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg">
    <img alt="Las casillas de 18 mercados lingüísticos se iluminan mientras la skill audita example.com para el mercado coreano y enumera los hallazgos reales." src="assets/hero-light.svg" width="100%">
  </picture>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.40.1-brightgreen" alt="versión 0.40.1">
  <img src="https://img.shields.io/badge/license-Apache--2.0-brightgreen" alt="Apache-2.0">
  <img src="https://img.shields.io/badge/markets-18-brightgreen" alt="18 mercados lingüísticos">
  <img src="https://img.shields.io/badge/dependencies-Python_stdlib_only-brightgreen" alt="Solo la biblioteca estándar de Python">
</p>

<p align="center"><a href="README.md">简体中文</a> · <a href="README.en.md">English</a> · <b>Español</b></p>

**Descarga gratuita. Usa tu propia herramienta de IA y tu propio modelo.**

**Instálala con una línea** (detecta <img src="assets/icons/claude.svg" width="16" height="16" alt=""> Claude Code, <img src="assets/icons/codex.svg" width="16" height="16" alt=""> Codex, <img src="assets/icons/cursor.svg" width="16" height="16" alt=""> Cursor y otros entornos que tengas instalados):

```bash
curl -fsSL https://raw.githubusercontent.com/everyinfra/seo-skills/main/install.sh | bash
```

> La mantiene [EveryInfra](https://everyinfra.com/es?utm_source=github&utm_medium=readme&utm_campaign=seo-skills&utm_content=maintainer_line). Si una tarea necesita datos en vivo, EveryInfra tiene una [API de búsqueda web](https://everyinfra.com/es/products/search?utm_source=github&utm_medium=readme&utm_campaign=seo-skills&utm_content=search_api) (17 herramientas) y [API de datos para 90 plataformas](https://everyinfra.com/es/market?utm_source=github&utm_medium=readme&utm_campaign=seo-skills&utm_content=data_apis); esta skill no depende de ellas.

EveryInfra SEO Skills va por la versión `0.40.1` y usa la licencia Apache-2.0. Es una sola skill de trabajo para SEO y GEO, `seo-suite`: instrucciones, notas de referencia y plantillas de salida. No llama a ningún modelo, no incluye proveedor, no necesita API key ni dependencias de ejecución. El modelo y su cuota son los de la herramienta de IA que ya usas.

**Lo que la distingue: SEO y GEO global en un solo flujo.** Un equipo que vende en todo el mundo no quiere una docena de herramientas de un solo mercado. Esta suite reúne **18 mercados lingüísticos** en un mismo espacio de trabajo y puntúa cada uno por separado: chino, inglés, ruso (Yandex/Alice), coreano (<img src="assets/icons/naver.svg" width="16" height="16" alt=""> Naver/AI Briefing), japonés (Yahoo! JAPAN + Bing + AI Overviews), español (las divisiones de es-419 en Latinoamérica), portugués (Brasil, el mercado más fuerte de <img src="assets/icons/codex.svg" width="16" height="16" alt=""> ChatGPT), árabe (RTL y MSA frente a dialectos), francés (Ley 96), alemán (Sie/du en DACH), indonesio (baku frente a gaul), hindi (la realidad de Hinglish en tres escrituras), italiano (it-CH como locale propio), turco (un segundo mercado de Yandex, ~26 %), vietnamita (variantes con y sin diacríticos + Cốc Cốc), tailandés (segmentación de una escritura sin espacios), polaco (normalización de diacríticos) y neerlandés (nl-BE flamenco). Lo global no es un módulo aparte: está **dentro de cada conjunto de capacidades**, con [multilingual-workflow.md](skills/seo-suite/references/overview/multilingual-workflow.md) como columna vertebral.

## Lo que solo trae esta suite

- **18 portales de mercado.** `references/markets/` tiene un portal por mercado lingüístico, escrito en octubre de 2026 a partir de investigación en el idioma de cada mercado: buscadores, herramientas locales, conocimiento de la comunidad y notas de cumplimiento.
- **Disciplina de evidencia.** Cada afirmación lleva su tipo de fuente y su vida útil; la skill nunca informa de una señal que no está en la página ni promete mejoras de posición, tráfico o citas en IA. Los consejos de GEO están acotados por un archivo de restricciones de evidencia (`references/content/geo-evidence.md`).
- **Un circuito de actualización propio.** `intel_check.py` vigila 18 fuentes (blogs de buscadores, políticas de robots y rastreadores de IA, especificaciones de agentes, medidores de cuota de mercado), confirma cada cambio, lo relaciona con los archivos de referencia afectados y clasifica la actualización de P0 a P3.
- **Un monitor, no auditorías sueltas.** `monitor.py` hace comprobaciones diarias y de deriva semanal, guarda instantáneas en SQLite y emite alertas en cuatro niveles con enfriamiento; `notify.py` reparte los avisos por cuatro canales según la gravedad.
- **Puertas de CI para SEO.** Una acción compuesta en la raíz (`action.yml`) audita cada pull request, falla por debajo de un `min-score` y genera SARIF, JUnit y anotaciones de PR con `ci_format.py`: una regresión de SEO aparece como un test que falla.
- **Un orquestador.** `project.py` da a cada sitio un espacio de trabajo y una máquina de cinco estados (auditar → priorizar → corregir → verificar → monitorizar); `run triage` encadena rastreo, auditoría, puntuación y prioridades en un solo comando.

## Qué aportas tú

- Una herramienta de IA compatible con Skills y tu propio modelo configurado.
- Para tareas con datos, tus propias exportaciones: Google Search Console, GA4, Bing Webmaster Tools o exportaciones de herramientas de posiciones, enlaces o rastreo de tus cuentas.
- Las API externas opcionales (por ejemplo PageSpeed Insights o Knowledge Graph Search) necesitan tus propias claves; este repositorio no trae ninguna.
- Las acciones hacia fuera (correos de outreach, publicación) las redacta la skill y solo se ejecutan cuando tú confirmas.

## Pruébala en 60 segundos

Sin dependencias ni API keys: todos los scripts funcionan solo con la biblioteca estándar de Python. Después de clonar o descomprimir, una cadena de comandos lleva `example.com` por el circuito mínimo **auditoría → puntuación por capas → plan de corrección**:

```bash
cd seo-skills/skills/seo-suite
python3 scripts/site_audit.py https://example.com --json > /tmp/audit.json
python3 scripts/health_score.py --input /tmp/audit.json
python3 scripts/fix_plan.py --audit /tmp/audit.json --estimate
```

<p align="center"><img alt="Ejecución real: salida de terminal de site_audit, health_score y fix_plan sobre example.com (2026-10-27)" src="assets/real-run-example-com.png" width="100%"></p>

Para auditar con las reglas de un mercado concreto, añade `--market`, por ejemplo `--market ko` (límites de título y descripción en caracteres de ancho completo para coreano).

## Instalación

**<img src="assets/icons/claude.svg" width="16" height="16" alt=""> Claude Code / <img src="assets/icons/zcode.svg" width="16" height="16" alt=""> ZCode** (este repositorio trae manifiestos de plugin en `.claude-plugin/` y `.zcode-plugin/`):

```bash
claude plugin marketplace add everyinfra/seo-skills
claude plugin install seo-suite@everyinfra-seo-skills
```

**Cualquier entorno compatible con Agent Skills** (<img src="assets/icons/codex.svg" width="16" height="16" alt=""> Codex, <img src="assets/icons/cursor.svg" width="16" height="16" alt=""> Cursor, <img src="assets/icons/gemini.svg" width="16" height="16" alt=""> Gemini CLI, <img src="assets/icons/copilot.svg" width="16" height="16" alt=""> Copilot, Windsurf, Goose, Amp…): el instalador de una línea de arriba detecta los entornos instalados y se adapta a cada uno; también puedes copiar `skills/seo-suite` en la carpeta de skills de la herramienta, por ejemplo `~/.agents/skills/`. Carpetas y forma de invocación por entorno: [HOSTS.md](HOSTS.md).

## Actividad de desarrollo

<!-- readme-stats: charts are regenerated daily, do not edit by hand -->

Commits por día en todos los repositorios de EveryInfra, incluido el gateway privado (solo recuentos), y versiones por semana. El gráfico se regenera cada día y muestra su hora de actualización.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/readme-stats/activity-es-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/readme-stats/activity-es-light.svg">
  <img alt="Commits por día en todos los repositorios de EveryInfra y versiones por semana" src="assets/readme-stats/activity-es-light.svg" width="100%">
</picture>

## Constrúyela con nosotros

Ningún equipo conoce por dentro los 18 mercados. Si sabes cómo funciona la búsqueda en tu mercado, o ves un consejo desactualizado, añádelo: un portal de mercado, una regla corregida, un script o una plantilla. Consulta [CONTRIBUTING.md](CONTRIBUTING.md). Los mantenedores revisan cada contribución a mano y la acreditan en [CONTRIBUTORS.md](CONTRIBUTORS.md). Ideas y preguntas en [Discussions](https://github.com/everyinfra/seo-skills/discussions).

## Más

La descripción completa de capacidades, el apartado «Why now» con sus fuentes y la estructura del repositorio están en el [README en inglés](README.en.md) y en el [README en chino](README.md). Historial de versiones: [CHANGELOG.md](CHANGELOG.md).

Problemas y sugerencias en [GitHub Issues](https://github.com/everyinfra/seo-skills/issues). No pegues API keys, credenciales, datos de clientes ni otra información confidencial.

Apache-2.0; consulta [LICENSE](LICENSE) y [NOTICE](NOTICE).
