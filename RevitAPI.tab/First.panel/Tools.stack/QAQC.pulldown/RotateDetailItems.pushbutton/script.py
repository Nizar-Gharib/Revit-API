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
# Initialize output
output = script.get_output()

# ----------------------------------------------------------------------
# 1. Get the Detail Items to Rotate
# ----------------------------------------------------------------------
# Detail items are typically in the current selection
selection = revit.get_selection()

if not selection.elements:
    output.print_md("### ⚠️ No Detail Items Selected")
    output.print_md("Please **select all the detail items** you want to rotate and run the script again.")
    script.exit()

# Filter selection to ensure we only have Detail Items
items_to_rotate = [
    el for el in selection.elements if hasattr(el, 'Category') and el.Category and el.Category.Name == "Detail Items"
]

if not items_to_rotate:
    output.print_md("### ⚠️ No Detail Items Found in Selection")
    output.print_md("The current selection does not contain any Detail Items. Please select them and try again.")
    script.exit()

# ----------------------------------------------------------------------
# 2. Get the Reference Detail Item
# ----------------------------------------------------------------------
# Prompt user to select the single reference detail item
try:
    output.print_md("### Select Reference Detail Item")
    output.print_md("Please click on the single **reference detail item**.")
    
    # Imports necessary for PickObject (Revit UI)
    from Autodesk.Revit.UI.Selection import ObjectType
    
    # Use PickObject to get the reference element
    ref_element = uidoc.Selection.PickObject(
        ObjectType.Element,
        "Select the reference Detail Item to face."
    )
    
    # Get the element from the picked reference
    reference_item = doc.GetElement(ref_element.ElementId)
    
    if reference_item.Category.Name != "Detail Items":
        output.print_md("### ❌ Incorrect Selection")
        output.print_md("The selected reference is not a Detail Item. Please re-run and select a valid reference.")
        script.exit()
        
except Exception as e:
    # Python 2.7 error handling syntax: except Exception, e:
    if "Operation aborted" in str(e):
        output.print_md("### 🛑 Operation Cancelled")
        output.print_md("No reference detail item was selected. Script aborted.")
    else:
        output.print_md("### ❌ An error occurred during selection: {}".format(e))
    script.exit()


# ----------------------------------------------------------------------
# 3. Calculate Reference Point and Rotation
# ----------------------------------------------------------------------

# Get the location point of the reference item
# Detail items use LocationPoint
ref_loc = reference_item.Location
if not ref_loc or not hasattr(ref_loc, 'Point'):
    output.print_md("### ❌ Reference Item Location Error")
    output.print_md("The reference detail item does not have a valid location point. Script aborted.")
    script.exit()
    
ref_point = ref_loc.Point

# The vector that represents the item's initial "front" direction.
# We assume the item's front is along the Y-axis (0, 1, 0)
initial_vector = XYZ.BasisY 

rotated_count = 0

# Start a transaction to make changes to the document
t = Transaction(doc, 'Rotate Detail Items to Face Reference')
try:
    t.Start()
    
    for item in items_to_rotate:
        item_loc = item.Location
        if not item_loc or not hasattr(item_loc, 'Point'):
            # Python 2.7 string formatting
            output.print_md("Skipping item ID {}: Location point not found.".format(item.Id))
            continue
            
        item_point = item_loc.Point
        
        # 1. Calculate the vector from the item being rotated to the reference point
        target_vector = ref_point.Subtract(item_point).Normalize()
        
        # 2. Check for zero length vector (item is at the same location as reference)
        if target_vector.GetLength() == 0:
            output.print_md("Skipping item ID {}: Coincident with reference point.".format(item.Id))
            continue
            
        # Detail Items exist on a 2D plane (the view plane), so we only care about X and Y
        # Set Z to zero for 2D calculation by projecting onto the XY plane
        target_vector_2d = XYZ(target_vector.X, target_vector.Y, 0).Normalize()
        initial_vector_2d = XYZ(initial_vector.X, initial_vector.Y, 0).Normalize()

        # 3. Calculate the angle between the initial vector and the target vector
        
        # Angle magnitude (always positive)
        angle_magnitude = initial_vector_2d.AngleTo(target_vector_2d)
        
        # Z-component of the cross product for direction (sign determines direction)
        cross_z = initial_vector_2d.X * target_vector_2d.Y - initial_vector_2d.Y * target_vector_2d.X
        
        # Determine the sign of the angle
        angle_signed = angle_magnitude if cross_z >= 0 else -angle_magnitude
        
        # 4. Create the rotation axis and rotation line
        # The rotation axis for 2D is the Z-axis (0, 0, 1)
        # The rotation line must pass through the item's current location point
        rotation_axis = XYZ.BasisZ
        rotation_line = Line.CreateUnbound(item_point, rotation_axis)
        
        # 5. Apply the rotation
        item_loc.Rotate(rotation_line, angle_signed)
        
        rotated_count += 1
        
    t.Commit()
    
    # Final Output
    output.print_md("### 🎉 Success! {} Detail Items Rotated".format(rotated_count))
    output.print_md("The selected detail items were rotated to face the reference item (ID: {}).".format(reference_item.Id))

except Exception as ex:
    if t.HasStarted() and t.IsActive:
        t.RollBack()
    output.print_md("### ❌ Transaction Failed")
    output.print_md("An error occurred: {}".format(ex))
