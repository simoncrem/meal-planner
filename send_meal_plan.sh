#!/bin/bash
cd /Users/simoncremieux/meal_planner_app
source venv/bin/activate
export FLASK_APP=app.py
flask send-meal-plan 