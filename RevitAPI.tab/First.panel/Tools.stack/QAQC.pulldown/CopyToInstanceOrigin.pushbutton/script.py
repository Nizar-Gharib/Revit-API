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
from Autodesk.Revit.UI.Selection import ObjectType
from System.Collections.Generic import List

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
current_selection = uidoc.Selection
selected_ids = uidoc.Selection.GetElementIds()
selected_instances = [doc.GetElement(id) for id in selected_ids]
pts = [i.Location.Point for i in selected_instances if isinstance(i, FamilyInstance)]

#select the lines you want to copy to the pts location
selected_lines = uidoc.Selection.PickObjects(ObjectType.Element)


lines = [doc.GetElement(ref) for ref in selected_lines]
lines_ids = List[ElementID]([i.Id for i in lines])
if not lines:
    forms.alert("No lines selected.", exitscript=True)

else:
#copy the lines to the pts location
    with Transaction(doc, "Copy Lines") as t:
        t.Start()
        for pt in pts:
            ElementTransformUtils.CopyElements(doc, lines_ids,doc, pt - lines[0].GeometryCurve.GetEndPoint(0), CopyPasteOptions())
        t.Commit()

