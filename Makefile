# =============================================================================
# Sri Gaṇeśa — Part 1 Portal
# Project Automation
# =============================================================================
#
# Purpose:
#   Provides the standard command-line interface for building, testing and
#   locally serving the Sri Gaṇeśa Part 1 digital portal.
#
# Project philosophy:
#   Clean, green and lean engineering.
#
# Source-first architecture:
#
#       Canonical Markdown
#              │
#              ▼
#       Python build system
#              │
#              ▼
#       Jinja2 templates
#              │
#              ▼
#       Generated static website
#              │
#              ▼
#       Local validation / GitHub Pages
#
# Important:
#   The generated website is never the source of truth.
#   Markdown, templates, source assets and build scripts are the source.
#
# Supported targets:
#
#   make setup     Install project dependencies.
#   make build     Generate the static website.
#   make serve     Build and serve the website locally.
#   make test      Run the automated test suite.
#   make clean     Remove generated build artefacts.
#
# Environment:
#   Developed and tested with:
#       Windows
#       Git Bash
#       GNU Make
#       Python 3.11+
#
# Virtual environment:
#   The project expects a local virtual environment at:
#
#       ./venv/
#
#   Activate it before using the Makefile:
#
#       source venv/Scripts/activate
#
# Shell:
#   This Makefile intentionally uses POSIX/Git-Bash-compatible commands.
#   It should therefore be executed from Git Bash rather than cmd.exe.
#
# =============================================================================


# -----------------------------------------------------------------------------
# Shell configuration
# -----------------------------------------------------------------------------

SHELL := /bin/sh


# -----------------------------------------------------------------------------
# Project configuration
# -----------------------------------------------------------------------------

PYTHON := python
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest

BUILD_DIR := _build
SCRIPTS_DIR := scripts


# -----------------------------------------------------------------------------
# Default target
# -----------------------------------------------------------------------------

.DEFAULT_GOAL := help


# -----------------------------------------------------------------------------
# Public targets
# -----------------------------------------------------------------------------

.PHONY: help setup build serve test clean


help:
	@printf '\n'
	@printf '%s\n' 'Sri Ganesa - Part 1 Portal'
	@printf '%s\n' '=========================='
	@printf '\n'
	@printf '%s\n' 'Available targets:'
	@printf '\n'
	@printf '%s\n' '  make setup   Install project dependencies'
	@printf '%s\n' '  make build   Build the static website'
	@printf '%s\n' '  make serve   Build and serve the website locally'
	@printf '%s\n' '  make test    Run the automated test suite'
	@printf '%s\n' '  make clean   Remove generated build artefacts'
	@printf '\n'


setup:
	@printf '\n'
	@printf '%s\n' 'Installing project dependencies...'
	@printf '\n'
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@printf '\n'
	@printf '%s\n' 'Dependency installation completed.'
	@printf '\n'


build:
	@printf '\n'
	@printf '%s\n' 'Building Sri Ganesa Part 1 Portal...'
	@printf '\n'
	$(PYTHON) $(SCRIPTS_DIR)/build.py
	@printf '\n'
	@printf '%s\n' 'Build completed.'
	@printf '%s\n' 'Generated site: _build/'
	@printf '\n'


serve:
	@printf '\n'
	@printf '%s\n' 'Preparing local portal...'
	@printf '\n'
	$(MAKE) build
	@printf '\n'
	@printf '%s\n' 'Starting local web server...'
	@printf '%s\n' 'Open http://localhost:8000/ in your browser.'
	@printf '\n'
	$(PYTHON) -m http.server 8000 --directory $(BUILD_DIR)


test:
	@printf '\n'
	@printf '%s\n' 'Running automated tests...'
	@printf '\n'
	$(PYTEST)
	@printf '\n'
	@printf '%s\n' 'Test run completed.'
	@printf '\n'


clean:
	@printf '\n'
	@printf '%s\n' 'Removing generated build artefacts...'
	@printf '\n'
	@if [ -d "$(BUILD_DIR)" ]; then rm -rf "$(BUILD_DIR)"; fi
	@printf '\n'
	@printf '%s\n' 'Clean completed.'
	@printf '\n'