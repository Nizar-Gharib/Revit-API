# -*- coding: utf-8 -*-
__title__ = "testing button"
__doc__ = """Version = 1.0
Date    = 31.07.2024
_____________________________________________________________________
Description:
Rename Views in Revit by using Find/Replace Logic.
_____________________________________________________________________
How-to:
-> Click on the button
-> Select Views
-> Define Renaming Rules
-> Rename Views
_____________________________________________________________________
Last update:
- [31.07.2024] - 1.0 RELEASE
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *
# pyRevit
from pyrevit import forms


import csv
from Autodesk.Revit.DB import FilteredElementCollector, View, ViewSheet, Transaction, XYZ

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================
#get the location points of current selection family instances


# Set the CSV file path
csv_path = r"C:\Users\nizarg\OneDrive - Bjarke Ingels Group\Documents\View List - GA.csv"



# Read CSV and store pairs
view_sheet_pairs = []
with open(csv_path, mode='r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header if there is one
    for row in reader:
        if len(row) >= 2:
            view_sheet_pairs.append((row[0].strip(), row[1].strip()))

# Collect all views and sheets in the project
all_views = {}
for v in FilteredElementCollector(doc).OfClass(View):
    if not v.IsTemplate:
        all_views[v.Name] = v

all_sheets = {}
for s in FilteredElementCollector(doc).OfClass(ViewSheet):
    all_sheets[s.Name] = s



# Start transaction
t = Transaction(doc, "Place Views on Sheets")
t.Start()

for view_name, sheet_name in view_sheet_pairs:
    view = all_views.get(view_name)
    sheet = all_sheets.get(sheet_name)

    if view and sheet:
        try:
            Viewport.Create(doc, sheet.Id, view.Id, XYZ(0, 0, 0))
            ## Place view on sheet at origin
            # sheet.AddView(view)
        except Exception as e:
            print("Could not place '{}' on '{}': {}".format(view_name, sheet_name, e))
    else:
        if not view:
            print("View '{}' not found.".format(view_name))
        if not sheet:
            print("Sheet '{}' not found.".format(sheet_name))

t.Commit()
print("Views placed on sheets successfully.")