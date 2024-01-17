# How to create graphical Evaluation

## Input file

Ablesung-Gas.xlsx, rows with an entry in column Bemerkung willl be skipped

## Excel

    Main file to run ist extend_xls_by_temperaturre2.py build upon modul TemperatrueTimeCourse.py.
    It generates GasverbrauchKorrelationTemperatur.100.xlsx.
    Rename it to GasverbrauchKorrelationTemperatur.xlsx and update Auswertung.xlsx to create a graphic.
    Depreciated because old simple approach: extend_xls_by_temperaturre.py and getdwddata.py.

## Jupyter / matplotlib

    Main notebook is Auswertung-0.ipynb. I ran it in Jupyter lab and vs code with jupyter extension.

## interactive chart, Python / matplotlib

    Main file to run is auswertung-2.py, uses AnnotatedCursor2.py
