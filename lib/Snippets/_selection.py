# -*- coding: utf-8 -*-


# Imports
#==================================================
from Autodesk.Revit.DB import *

# Variables
#==================================================
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document


# Reusable Snippets


def get_selected_elements(filter_types=None):
    """Get Selected Elements in Revit UI.
    You can provide a list of types for filter_types parameter (optionally)

    e.g.
    sel_walls = get_selected_elements([Wall])"""
    print('Using Function from _selection.py')
    selected_element_ids = uidoc.Selection.GetElementIds()
    selected_elements    = [doc.GetElement(e_id) for e_id in selected_element_ids]

    # Filter Selection (Optionally)
    if filter_types:
        return [el for el in selected_elements if type(el) in filter_types]
    return selected_elements