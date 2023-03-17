#!/usr/bin/env bash

sudo npm install @actions/core
sudo npm install @actions/github
sudo npm i -g @vercel/ncc

sudo ncc build index.js --license licenses.txt