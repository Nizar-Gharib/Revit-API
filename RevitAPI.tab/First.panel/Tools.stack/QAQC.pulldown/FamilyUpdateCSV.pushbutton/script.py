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
import csv
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit.UI import *
# pyRevit
from pyrevit import forms
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory
from pyrevit import DB
from pyrevit import script
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
logger = script.get_logger()
output = script.get_output()
# === USER INPUT ===
# Adjust to your CSV path
csv_path = forms.pick_file(file_ext='csv', multi_file=False)
if not csv_path:
    logger.error('CSV file not found {}'.format(csv_path))

floor_data = []
with open(csv_path, 'r') as f:
    # Change delimiter to ',' if comma-separated
    reader = csv.DictReader(f)
    data = [row for row in reader]

    # Log header info
    print("Loaded {} rows from CSV.".format(len(data)))
    print("CSV columns: {}".format(reader.fieldnames))

    # Example: iterate through rows
    for row in data:
        old_name = row.get('Old Name', '').strip()
        new_name = row.get('New Name', '').strip()
        type_mark = row.get('Type Mark', '').strip()
        keynote = row.get('Keynote', '').strip()
        description = row.get('Description', '').strip()
        type_comments = row.get('Type Comments', '').strip()

        # Example processing logic
        print("Processing: {} -> {}".format(old_name, new_name))
        print(type_mark)
        print(keynote)
        print(type_comments)
        print(description)

        # You can now map this info to Revit elements or types here
print ('-'*100)
print ('csv data for 2 columns are: {}'.format(floor_data))
# === COLLECT ALL FLOOR TYPES ===
collector = FilteredElementCollector(doc)\
    .OfClass(FloorType)\
    .ToElements()


# === START TRANSACTION ===
t = Transaction(doc, "Update Floor Type Parameters from CSV")
t.Start()

for ft in collector:

    type_name = Element.Name.__get__(ft)

    if type_name == old_name:
        type_name.Set(new_name)
    print (type_name.AsString())



t.Commit()

# === PRINT FEEDBACK ===
# output_text = "\n".join(report)
# print(output_text)
