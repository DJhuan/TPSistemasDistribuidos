#!/usr/bin/env bash

ollama serve &
ollama list
ollama pull nomic-embed-text