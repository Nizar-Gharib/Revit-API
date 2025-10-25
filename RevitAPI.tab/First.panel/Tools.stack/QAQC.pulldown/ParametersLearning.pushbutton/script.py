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
ref_picked_obj = uidoc.Selection.PickObject(ObjectType.Element, "Select a view to rename")
elem = doc.GetElement(ref_picked_obj)
elem_type = doc.GetElement(elem.GetTypeId())

elem_parameters = elem.Parameters
type_parameters = elem_type.Parameters

param_approved_by = elem.get_Parameter(BuiltInParameter.SHEET_APPROVED_BY).AsString()
param_Height = elem_type.LookupParameter("Height").AsDouble()
# param_elem_Height = elem.LookupParameter("Height").AsDouble()
param_Height_m = UnitUtils.ConvertFromInternalUnits(param_Height, UnitTypeId.Meters)

print(param_approved_by)
print(param_Height_m)
# print(param_elem_Height)


t = Transaction(doc, "set parameters")
try:
    t.Start()

    new_height = UnitUtils.ConvertToInternalUnits(3, UnitTypeId.Meters)
    new_height_m = UnitUtils.ConvertFromInternalUnits(new_height, UnitTypeId.Meters)
    elem_type.LookupParameter("Height").Set(new_height)


    new_approved_by = "John Doe"
    elem.get_Parameter(BuiltInParameter.SHEET_APPROVED_BY).Set(new_approved_by)

    print('Changed height to: {}'.format(new_height_m))
    print('Changed approved by to: {}'.format(new_approved_by))
except Exception as e:
    print('Error: {}'.format(e))

t.Commit()