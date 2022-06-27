#!/bin/bash

poetry install
poetry build

read -p "Publish to PyPi? [y/N]" -e answer
if [ $answer == "y" -o $answer == "Y" ]
then
  poetry publish
fi
