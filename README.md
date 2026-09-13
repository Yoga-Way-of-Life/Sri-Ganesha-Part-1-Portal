# Śrī Gaṇeśa — Part 1 Portal

A premium, editorial-style digital portal accompanying *Śrī Gaṇeśa's Wisdom — A Handbook of Symbolism and Daily Practice*.

This repository contains the source content and lightweight static publishing system for the **Part 1 — What to Learn** portal.

## Purpose

The portal introduces the wisdom, symbolism and practical reflections explored through Śrī Gaṇeśa.

It is designed as a digital companion to the book rather than a reproduction of the manuscript.

**Part 1 — What to learn.**  
**Part 2 — How to learn and apply it.**

The portal introduces the lessons. Part 1 explores their meaning. Part 2 will explore their application.

## Current Portal

The current release contains:

- 31 editorial reading pages
- Śrī Gaṇeśa iconography and symbolic teachings
- Reflective and practical treatment of the themes
- Responsive three-column reading layout
- Previous / Next page navigation
- On-page navigation
- Responsive mobile presentation
- Light / dark theme support
- Reading progress indicator
- Optimised WebP imagery
- Accessible semantic HTML structure

## Publishing Architecture

The portal intentionally uses a small and transparent build system:

```text
Canonical Markdown
        ↓
Python build engine
        ↓
Jinja2 templates
        ↓
CSS / JavaScript / WebP assets
        ↓
Static HTML portal
        ↓
GitHub Pages
````

The guiding principle is:

> Build only what the book experience requires.

## Repository Structure

```text
.
├── 01-foreword.md
├── 02-about-the-author.md
├── 03-contents.md
├── ...
├── 31-epilogue-bowing-to-the-remover-of-darkness.md
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
├── scripts/
│   ├── build.py
│   └── image_optimizer.py
├── source-assets/
├── templates/
├── Makefile
├── requirements.txt
├── .gitignore
└── LICENSE
```

Historical or provisional source material is retained under:

```text
ARCHIVED/
```

## Requirements

* Python 3.11+
* GNU Make
* Git

Python dependencies are defined in:

```text
requirements.txt
```

## Local Development

Create and activate the project virtual environment:

```bash
python -m venv venv
source venv/Scripts/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Build the portal:

```bash
make clean && make build
```

Start the local web server:

```bash
make serve
```

The generated portal is available at:

```text
http://localhost:8000/
```

## Build Commands

```bash
make setup
make build
make serve
make test
make clean
```

## Content Philosophy

The Git Pages are intentionally **editorial rather than manuscript-mirroring**.

The book remains the source of truth.

Portal pages interpret the relevant chapter themes for digital reading, reflection and exploration. They do not attempt to reproduce the manuscript's original section numbering or structure.

## Part 1 and Part 2

The broader project is conceived in two parts.

### Part 1 — What to Learn

This portal explores the meanings, symbolism and human lessons represented through Śrī Gaṇeśa's form.

### Part 2 — How to Learn and Apply

A future phase will explore how those lessons can be translated into human capabilities, organisational competencies, observable behaviours, practices and development.

The intended progression is:

```text
Gaṇeśa Symbol
    ↓
Philosophical Principle
    ↓
Human Capability
    ↓
Organisational Competency
    ↓
Observable Behaviour
    ↓
Practice
    ↓
Assessment
    ↓
Development
```

## Design Principles

The portal follows a small set of engineering and publishing principles:

* Knowledge first
* Editorial clarity
* Respect for the source tradition
* Human-centred presentation
* Responsive and accessible design
* Minimal dependencies
* Reusable components
* Optimised assets
* Maintainable source structure
* Static-first publishing

## Status

**Current status: Part 1 portal completed for initial publication.**

The local build currently generates 31 pages successfully.

## Author

**Satya Prakash Nigam**

*Śrī Gaṇeśārpaṇam astu.*

May this work be offered with reverence, humility and sincere intent to Śrī Gaṇeśa.
