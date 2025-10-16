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
from pyrevit import revit, script

from Autodesk.Revit.DB import Categories
from Autodesk.Revit.DB import Element

from Autodesk.Revit.DB import XYZ

from Autodesk.Revit.DB import APIObject

from Autodesk.Revit.UI.Selection import ObjectType, PickBoxStyle
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
# Initialize output
output = script.get_output()

# ======================================================================
# SCRIPT: HARD RESET DETAIL ITEM ROTATION TO 0
# ======================================================================



# ----------------------------------------------------------------------
# 1. Get the Detail Items to Reset
# ----------------------------------------------------------------------
selection = revit.get_selection()

if not selection.elements:
    output.print_md("### ⚠️ No Detail Items Selected")
    output.print_md("Please **select the detail items** you want to reset and run the script again.")
    script.exit()

# Filter selection to ensure we only have Detail Items
items_to_reset = [
    el for el in selection.elements if hasattr(el, 'Category') and el.Category and el.Category.Name == "Detail Items"
]

if not items_to_reset:
    output.print_md("### ⚠️ No Detail Items Found in Selection")
    output.print_md("The current selection does not contain any Detail Items. Please select them and try again.")
    script.exit()

# ----------------------------------------------------------------------
# 2. Set Rotation Parameter to 0
# ----------------------------------------------------------------------

reset_count = 0
t = Transaction(doc, 'Hard Reset Detail Rotation to 0')

try:
    t.Start()
    for item in items_to_reset:
        loc = item.Location
        if loc and hasattr(loc, 'Rotation'):
            current_rotation = loc.Rotation
            if abs(current_rotation) > 1e-6:  # Only rotate if not already zero
                # Rotation axis is Z, rotation center is the item's point
                axis = XYZ.BasisZ
                rotation_line = Line.CreateUnbound(loc.Point, axis)
                loc.Rotate(rotation_line, -current_rotation)
                reset_count += 1
        else:
            output.print_md("Skipping item ID {}: No rotation property found.".format(item.Id))
    t.Commit()
    output.print_md("### 🎉 Success! {} Detail Items Reset".format(reset_count))
    output.print_md("The rotation property was reset to 0 radians for selected items.")
except Exception as ex:
    if t.HasStarted() and t.IsActive:
        t.RollBack()
    output.print_md("### ❌ Transaction Failed")
    output.print_md("An error occurred: {}".format(ex))