# Aiuti di Stato in Italia — RNA 2016–2025

**Sito: https://salvatorefinizio.github.io/aiuti-stato-rna/**

Dieci anni di sostegno pubblico alle imprese italiane letti dal **Registro Nazionale Aiuti
di Stato** (RNA): **502,1 miliardi di euro** di ESL e **24,0 milioni di concessioni** tra
maggio 2016 e dicembre 2025 (119 file mensili di open data).

Il progetto è un insieme di pagine HTML statiche e autoconsistenti — dati e codice sono
inline, nessuna chiamata di rete a runtime — più la pipeline Python che le genera a partire
dai dump RNA e da alcune fonti esterne.

<sub>*English:* a static data-journalism site on ten years of Italian State aid, built from
the public RNA open-data dumps. Pages are in Italian with an EN toggle (top-right).
Everything under `site/` is self-contained HTML; `scripts/` holds the Python build pipeline.</sub>

---

## Le pagine

| Pagina | Contenuto |
|---|---|
| [`index.html`](site/index.html) | Home: KPI principali e navigazione per tema |
| [`panorama.html`](site/panorama.html) | Quadro d'insieme: beneficiari, settori, obiettivi di policy |
| [`geografia.html`](site/geografia.html) | Mappa NUTS3: valore assoluto, aiuto pro capite, concentrazione per anno |
| [`controllate.html`](site/controllate.html) | Capitalismo di Stato: società partecipate MEF e CDP |
| [`quadro-giuridico.html`](site/quadro-giuridico.html) | Basi giuridiche UE (GBER, quadri di crisi, *de minimis*) e strumenti |
| [`green-digitale.html`](site/green-digitale.html) | Transizione ecologica (65,4 mld) e digitale (29,8 mld) |
| [`innovazione.html`](site/innovazione.html) | Aiuti × brevetti: beneficiari incrociati con PATSTAT |
| [`esploratore.html`](site/esploratore.html) | Grafo interattivo delle 247 partecipate MEF/CDP e delle catene di controllo |
| [`dashboard.html`](site/dashboard.html) | Cruscotto integrale — sorgente canonica da cui sono derivate le pagine tematiche |

Ogni pagina ha un glossario degli acronimi in testa, un selettore lingua IT/EN e un pulsante
di download CSV per singolo grafico.

## I dati

### Fonte principale

**RNA — Registro Nazionale Aiuti di Stato**, [rna.gov.it](https://www.rna.gov.it/) · sezione
Open Data. Circa 74 dump mensili in `data/data_rna/` (ZIP), da cui si ricavano concessioni,
beneficiari, strumenti, basi giuridiche e obiettivi. Dati pubblici, riutilizzabili con
citazione della fonte.

Grandezza chiave: **ESL** (Equivalente Sovvenzione Lorda), il valore standardizzato UE del
vantaggio economico netto per il beneficiario — non l'importo nominale erogato.

### Fonti di arricchimento

| Fonte | Uso | Nel repo? |
|---|---|---|
| **Orbis / Bureau van Dijk** (BvD ID, struttura societaria) | match dei beneficiari RNA con identificativi d'impresa; catene di controllo delle partecipate | **No** — licenza proprietaria |
| **PATSTAT** (EPO, Autumn 2025) | conteggio famiglie brevettuali e classi CPC per beneficiario | **No** — licenza EPO |
| **Eurostat NUTS 2021 (03M)** | geometrie NUTS2/NUTS3 per le mappe | rigenerabile, vedi pipeline |
| **ISTAT / conti nazionali** | PIL e popolazione per i rapporti pro capite e % del PIL | `data/gdp_2016_2025.csv` |
| Elenchi partecipazioni pubbliche (MEF, CDP) | perimetro delle società a controllo pubblico | `data/partecipate_*.csv` |

> ⚠️ **Dati licenziati non versionati.** Orbis/BvD e PATSTAT sono soggetti a licenza e
> **non sono presenti in questo repository**: né i dump grezzi, né i file di match
> (`data/firms_bvdid.csv`, `corporate_structure_*.xlsx`) — sono esclusi via `.gitignore`.
> Nel repo compaiono solo aggregati derivati (conteggi per impresa/settore/anno) nei
> datamart JSON. Per rieseguire la pipeline di innovazione serve un accesso proprio a
> Orbis e PATSTAT.

Anche i dump RNA grezzi e i CSV di lavoro restano locali (`data/*.csv`, `data/data_rna/`,
`data/nuts_sectors/`): sono pesanti e riscaricabili dalla fonte.

## Struttura del repository

```
data/             input grezzi (non versionati: CSV, dump RNA, geojson)
data/generated/   datamart JSON prodotti dagli script
scripts/          pipeline Python + script di generazione pagine  → vedi scripts/README.md
site/             output pubblicato: pagine HTML + assets/         → deploy su gh-pages
```

Le pagine tematiche sono **generate** da `dashboard.html`: non vanno modificate a mano.
La sorgente da cui rigenerare tutto è il cruscotto.

## Come rigenerare

La procedura completa — ordine di esecuzione, script per script, con i tempi attesi e le
dipendenze esterne — è documentata in **[`scripts/README.md`](scripts/README.md)**.

In sintesi:

```bash
python3 scripts/build_nuts3_geo.py         # geometrie NUTS3
python3 scripts/build_innovation_data.py   # datamart innovazione (richiede Orbis + PATSTAT)
python3 scripts/build_soe_data.py          # datamart partecipate
python3 scripts/build_innovation_page.py   # → site/innovazione.html
python3 scripts/gen_pages.py               # dashboard.html → pagine tematiche
python3 scripts/add_glossaries.py          # glossari (dopo gen_pages)
python3 scripts/add_i18n.py                # toggle IT/EN
python3 scripts/add_downloads.py           # pulsanti download CSV
```

> Gli script assumono il percorso assoluto della root del repo e leggono alcuni input molto
> grandi da percorsi locali (Dropbox). Vanno adattati prima di rieseguirli altrove.

Deploy:

```bash
git subtree push --prefix site origin gh-pages
```

## Avvertenze sull'interpretazione

- L'**ESL** non è la spesa pubblica effettiva: è il valore-aiuto stimato secondo le regole UE.
  Somme su strumenti eterogenei (contributi, garanzie, crediti d'imposta) vanno lette con cautela.
- La copertura del registro **cresce nei primi anni**, per via dell'avvio progressivo: 5.535
  concessioni nel 2016, 202mila nel 2017, 606mila nel 2018, poi milioni l'anno. I confronti
  temporali che partono dal 2016–2017 misurano in buona parte l'entrata a regime dell'RNA,
  non un aumento degli aiuti.
- Le pagine si fermano a **dicembre 2025**; i datamart contengono anche il primo trimestre
  2026 (ancora incompleto), escluso dai totali pubblicati.
- Il match RNA × Orbis avviene su **codice fiscale / partita IVA** e non è esaustivo: le
  sezioni su innovazione e partecipate coprono un sottoinsieme dei beneficiari, non il totale.
- I totali possono differire leggermente tra pagine rigenerate in momenti diversi rispetto ai
  dump RNA scaricati.

## Licenza e citazione

Il repository ha una **doppia licenza**, perché contiene due cose diverse:

| Cosa | Licenza | File |
|---|---|---|
| **Codice** — `scripts/`, HTML/CSS/JS in `site/` | [MIT](LICENSE) | `LICENSE` |
| **Dati e contenuti** — `data/generated/`, grafici, analisi | [CC BY 4.0](LICENSE-DATA) | `LICENSE-DATA` |

Entrambe consentono il riuso, anche commerciale, con attribuzione.

**Dati di terzi non coperti.** Le licenze qui sopra coprono solo gli aggregati e l'analisi
prodotti da questo progetto: non concedono alcun diritto sulle fonti sottostanti. Orbis/BvD
e PATSTAT sono proprietari, non ridistribuiti, e chi volesse rieseguire quelle sezioni deve
procurarsi una licenza propria. Dettagli in [`LICENSE-DATA`](LICENSE-DATA).

Citazione suggerita:

> S. Finizio, *Aiuti di Stato in Italia 2016–2025 — elaborazione su dati RNA*,
> https://salvatorefinizio.github.io/aiuti-stato-rna/ — CC BY 4.0

Elaborazione propria su dati RNA. Il progetto non è affiliato né approvato da alcuna
amministrazione pubblica.
