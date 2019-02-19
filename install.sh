#!/usr/bin/env bash

conda install --name miami-university-cse-464-group-project $@
conda env export --name miami-university-cse-464-group-project > environment.yml
