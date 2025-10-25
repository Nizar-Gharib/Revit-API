# -*- coding: utf-8 -*-
__title__ = "Imported Category"
__doc__ = """Version = 1.0
Date    = 20.09.2025
_____________________________________________________________________
Description:
Override the graphics of the listed DWGs as per an external csv file
_____________________________________________________________________
How-to:
-> Ensure the csv file path is listed below
-> Ensure the dwg files are listed below (with .dwg at the end of their names)
-> Just run the script within pyRevit environment and it will do the job
_____________________________________________________________________
Last update:
- [21.10.2025] - 1.0 RELEASE
_____________________________________________________________________
Author: Nizar Gharib"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *
# pyRevit
# from pyrevit import forms
from Autodesk.Revit.DB import Categories
from Autodesk.Revit.DB import Element
from Autodesk.Revit.DB import CategoryNameMap
from Autodesk.Revit.DB import APIObject
from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit.UI.Selection import PickBoxStyle
from Autodesk.Revit.DB import FilteredElementCollector



# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================
import clr
import csv
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *

# Path to the CSV file
csv_path = r"C:\Users\nizarg\OneDrive - Bjarke Ingels Group\Desktop\VPHIL\02 WIP\05 Scripts\BPD100_VLF_FACADE_LAYER TABLE.csv"

# Mapping of built-in pattern names to their ElementIds
BUILTIN_LINE_PATTERNS = {
    "solid": LinePatternElement.GetSolidPatternId(),
    #"dash": ElementId(10250438),
    #"dot": ElementId(267225),
    #"dash dot": ElementId(1135064),
    #"dash dot dot": ElementId(267224),
    # Add more if needed, with correct built-in IDs
}

# Load the CSV file using Python's built-in csv module
data = []
with open(csv_path, mode='r') as file:  # Remove encoding='utf-8' for compatibility
    csv_reader = csv.reader(file)
    next(csv_reader)  # Skip the header row
    for row in csv_reader:
        # Ensure the row has exactly 6 columns (Layer Name, R, G, B, Line Weight, Line Pattern)
        if len(row) == 6:
            try:
                # Assuming the CSV has Layer Name, R, G, B, Line Weight, and Line Pattern
                Layer_name, R, G, B, LW, LP = row

                pattern_collector = FilteredElementCollector(doc).OfClass(LinePatternElement).ToElements()
                pattern_names = {p.Name.lower(): p.Id for p in pattern_collector}
                                
                lp_key = LP.strip().lower()
                if lp_key in BUILTIN_LINE_PATTERNS:
                    LP_id = BUILTIN_LINE_PATTERNS[lp_key]
                else:
                    LP_id = pattern_names.get(lp_key, ElementId(ElementId.InvalidElementId.IntegerValue))
                
                # Add the data to the list
                data.append((Layer_name, int (R),int(G), int(B), int(LW), LP_id))
            except ValueError as e:
                print("Skipping row due to error: %s - Row data: %s" % (str(e), str(row)))
        else:
            print("Skipping row due to incorrect number of columns: %s" % str(row))


# Get the categories in the document

documentCategories = doc.Settings.Categories

def override_dwg_layers(Layer_name, R, G, B, LW, LP_id):
    for cat in documentCategories:
        if cat.Name in ("BPD 100_ENV_ST.dwg",
                         "BPD 100_ENV_Roof plans_Roof A.dwg",
                           "BPD 100_ENV_Roof plans_Roof B.dwg",
                             "BPD 100_ENV_Roof plans_Roof C.dwg",
                               "BPD 100_ENV_Roof plans_Roof D.dwg",
                                 "BPD 100_ENV_Roof plans_Roof E.dwg",
                                   "BPD 100_ENV_NP1.dwg", "BPD 100_ENV_NP2.dwg", "BPD 100_ENV_NP3.dwg",
                                     "BPD 100_ENV_NP4.dwg", "BPD 100_ENV_NP5.dwg", "BPD 100_ENV_NP6.dwg",
                                       "BPD 100_ENV_NP7.dwg"):
            print(cat.Name)
            getsubcategories = cat.SubCategories

            for subcat in getsubcategories:
                if subcat.Name == Layer_name:
                    print(subcat.Name)
                    if LW > 0:
                        subcat.SetLineWeight(LW, GraphicsStyleType.Projection)
                    else:
                        subcat.SetLineWeight(1, GraphicsStyleType.Projection)
                    subcat.LineColor = Color(R, G, B)
                    # Only set line pattern if LP_id is valid
                    if LP_id != ElementId.InvalidElementId:
                        subcat.SetLinePatternId(LP_id, GraphicsStyleType.Projection)
                    else:
                        print("Warning: Line pattern not found for layer '{}'. Skipping line pattern override.".format(Layer_name))


t = Transaction(doc, 'Modify Subcategory Properties')
t.Start()
try:
    for (layer_name, R, G, B, LW, LP_id) in data:
        override_dwg_layers(layer_name, R, G, B, LW, LP_id)

    t.Commit()
except Exception as e:
    t.RollBack()
    print("Error occurred: %s" % str(e))