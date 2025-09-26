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
# pyRevit
# from pyrevit import forms

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

from Autodesk.Revit.DB import LinePatternElement

#collect all line patterns in the document
line_patterns = FilteredElementCollector(doc).OfClass(LinePatternElement).ToElements()
#line_pattern_Ids = [lp.Id for lp in line_patterns]

line_pattern_dict = {lp.Name.lower(): lp.Id for lp in line_patterns}
line_pattern_names = [lp.Name.lower() for lp in line_patterns]



for key, value in sorted(line_pattern_dict.items()):
    print("{},{}".format(key, value.IntegerValue))

for i in sorted(line_pattern_names):
    print (i)
