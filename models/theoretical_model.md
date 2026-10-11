# Theoretical model

Relations between the topic of the page (**Laura Bassi**) and the selected entities, expressed in natural language and as a graph.
Dashed edges are **indirect relations**: entities or facts not stated in the Wikipedia page, taken from Wikidata or from the other entities.
Authority identifiers (Wikidata / VIAF / LC) are listed in [`../docs/entities.csv`](../docs/entities.csv).

## Graph

```mermaid
flowchart LR
  classDef person fill:#fde2e4,stroke:#c9184a,color:#000
  classDef place fill:#d8f3dc,stroke:#2d6a4f,color:#000
  classDef org fill:#dbe7ff,stroke:#1d4ed8,color:#000
  classDef event fill:#fff3bf,stroke:#b08900,color:#000
  classDef work fill:#ede7f6,stroke:#6a1b9a,color:#000
  classDef concept fill:#e9ecef,stroke:#495057,color:#000

  LB((Laura Bassi<br/>1711–1778)):::person

  %% people
  GV[Giuseppe Veratti]:::person
  B14[Prospero Lambertini<br/>Pope Benedict XIV]:::person
  VOL[Voltaire]:::person
  SPA[Lazzaro Spallanzani]:::person
  GAL[Luigi Galvani]:::person
  VOLTA[Alessandro Volta]:::person
  ALG[Francesco Algarotti]:::person
  MAN[Gabriele Manfredi]:::person
  ECP[Elena Cornaro Piscopia]:::person
  NEW[Isaac Newton]:::person
  PF[Paula Findlen]:::person

  %% places & organisations
  BO[Bologna]:::place
  PA[Palazzo d'Accursio]:::place
  CD[Santuario del Corpus Domini]:::place
  PS[Papal States]:::place
  UNI[University of Bologna]:::org
  ACC[Academy of Sciences<br/>of the Institute of Bologna]:::org
  ARC[Arcadian Academy]:::org

  %% events
  E1[/Defence of 49 theses<br/>17 Apr 1732/]:::event
  E2[/Doctorate<br/>12 May 1732/]:::event
  E3[/Professorship<br/>Dec 1732/]:::event
  E4[/Marriage<br/>7 Feb 1738/]:::event
  E5[/Chair of Experimental Physics<br/>1776/]:::event

  %% works
  W1[Philosophica Studia<br/>1732]:::work
  W2[De aeris compressione<br/>1745]:::work
  W3[Il Newtonianismo<br/>per le dame, 1737]:::work
  W4[Findlen 1993<br/>Isis]:::work
  Q[["Quotation: 'There is no Bassi in London'"]]:::work

  %% concepts
  C1{{Newtonianism}}:::concept
  C2{{Experimental physics}}:::concept
  C3{{Natural philosophy}}:::concept
  C4{{Electricity}}:::concept
  C5{{Women in science}}:::concept
  C6{{Age of Enlightenment}}:::concept

  %% relations
  LB -- born / died / worked in --> BO
  LB -- citizen of --> PS
  LB -- buried in --> CD
  LB -- married --> GV
  LB -- patronised by --> B14
  LB -- corresponded with --> VOL
  LB -- corresponded with --> VOLTA
  LB -- corresponded with --> ALG
  LB -- taught --> SPA
  LB -- colleague of --> GAL
  LB -- member of --> ACC
  LB -.member of.-> ARC
  LB -.student of.-> MAN
  LB -.preceded by.-> ECP

  LB -- participant in --> E1
  E1 -- took place at --> PA
  E1 -- presented --> W1
  E1 -- examined by --> UNI
  LB -- received --> E2
  E2 -- awarded by --> UNI
  LB -- appointed in --> E3
  E3 -- at --> UNI
  LB -- participant in --> E4
  E4 -- with --> GV
  LB -- appointed in --> E5
  E5 -- subject --> C2

  LB -- author of --> W2
  W1 -- subject --> C3
  W2 -- subject --> C2
  LB -- populariser of --> C1
  C1 -.named after.-> NEW
  ALG -- author of --> W3
  W3 -- subject --> C1
  LB -- worked on --> C4
  VOL -- author of --> Q
  Q -- about --> LB
  PF -- author of --> W4
  W4 -- about --> LB
  LB -.subject.-> C5
  LB -.period.-> C6
  PA -.located in.-> BO
  UNI -.located in.-> BO
  ACC -.located in.-> BO
  BO -.part of.-> PS
```

## Relations in natural language

**Life and places**
- Laura Bassi was born (29 Oct 1711) and died (20 Feb 1778) in **Bologna**, then part of the **Papal States**.
- She is buried in the **Santuario del Corpus Domini** (indirect: from Wikidata).

**People**
- She married **Giuseppe Veratti**, physician and lecturer in anatomy, on 7 February 1738.
- Cardinal **Prospero Lambertini**, later **Pope Benedict XIV**, was her most important patron.
- She corresponded with **Voltaire**, **Alessandro Volta** and **Francesco Algarotti**.
- She was a colleague of **Luigi Galvani** and the teacher of her cousin **Lazzaro Spallanzani**.
- She studied with **Gabriele Manfredi** (indirect: from Wikidata).
- **Elena Cornaro Piscopia** (Padua, 1678) was the first woman to earn a university degree; Bassi was the second.

**Events (career)**
- On 17 April 1732 she publicly defended 49 theses (*Philosophica Studia*) in the **Palazzo d'Accursio** (Palazzo Pubblico) before the professors of the **University of Bologna**.
- She received her doctorate on 12 May 1732.
- In December 1732 she was appointed professor of natural philosophy.
- In 1776 she obtained the **Chair of Experimental Physics**, which she held until her death.
- She was a member of the **Academy of Sciences of the Institute of Bologna** and of the **Arcadian Academy** (indirect: from Wikidata).

**Works and ideas**
- She wrote the treatise **De aeris compressione** (1745).
- She was the most important populariser of **Newtonianism** in Italy (indirect link to **Isaac Newton**).
- Algarotti's **Il Newtonianismo per le dame** (1737) belongs to the same Newtonian context.
- Her research fields: **experimental physics**, **natural philosophy**, **electricity**.

**Textual phenomena and bibliography**
- Quotation from Voltaire: *"There is no Bassi in London…"*.
- **Paula Findlen** wrote "Science as a Career in Enlightenment Italy: The Strategies of Laura Bassi" (*Isis*, 1993), cited in the page's bibliography.

**Subjects and classification**
- Women in science · Age of Enlightenment (LCSH sh85044032) · Physics (LCSH sh85101653) · Natural philosophy (LCSH sh85101004) · Electricity (LCSH sh85042065).
