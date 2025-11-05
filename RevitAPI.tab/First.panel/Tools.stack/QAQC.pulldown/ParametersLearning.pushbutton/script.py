# -*- coding: utf-8 -*-
__title__ = "Rename Views"
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
from Autodesk.Revit.UI.Selection import ObjectType
# pyRevit
from pyrevit import forms
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory
from pyrevit import DB
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

#1️⃣ Select Views

#collect all floor types in the document
floor_types  = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsElementType().ToElements()
floor_types_params = [ft.Parameters for ft in floor_types]

#print names of all floor types
for f in floor_types:
    name = DB.Element.Name.__get__(f)
    type_params = f.Parameters
    print(name)
    for p in type_params:
        print(p.Definition.Name)
    print('---'*50)

# Write these to a csv file
import csv
import os
output_file = r"C:\Users\nizarg\OneDrive - Bjarke Ingels Group\Desktop\NG Personal Notes\RevitAPI\Testing CSV\floor_types_params.csv"

with open(output_file, mode='w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Floor Type", "Parameter"])
    for f in floor_types:
        name = DB.Element.Name.__get__(f)
        type_params = f.Parameters
        for p in type_params:
            writer.writerow([name, p.Definition.Name])
    print('CSV file created at: {}'.format(output_file))
t = Transaction(doc, "set parameters")
try:
    t.Start()

    
except Exception as e:
    print('Error: {}'.format(e))

t.Commit()