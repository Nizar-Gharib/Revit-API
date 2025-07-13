using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using System;
using System.Collections.Generic;

namespace CopyPaste
{
    [Transaction(TransactionMode.Manual)]
    public class typeMarkMapping : IExternalCommand
    {
        public Result Execute(
            ExternalCommandData commandData,
            ref string message,
            ElementSet elements)
        {
            // Define the mappings directly in the code (substring -> Type Mark value)
            Dictionary<string, string> wallTypeMarkMappings = new Dictionary<string, string>
            {
                { "ID_WA_Panel - Wood WD-01 - 20mm", "WD-01" },
                { "ID_WA_SP-01 Plaster Paint", "SP-01" },
                { "ID_WA_SP-01 Plaster Paint With Reveal", "SP-01" },
                { "ID_WA_SP-01 Plaster Paint without skirting", "SP-01" },
                {"ID_WA_SP-02 - 1/8\" Plaster No Skirting" , "SP-02" },
                {"ID_WA_SP-02 - 1/8\" Plaster w metal reveal base", "SP-02" },
                {"ID_WA_ST-02 - Stone - 20mm","ST-02"},
                {"ID_WA_TL-03 13mm - tile 8mm + thinset 5mm", "TL-03"},
                {"ID_WA_WAL 01 Knauf Framing","WAL-01"},
                {"ID_WA_WAL 01 Mada Framing","WAL-01"},
                {"ID_WA_WAL 02 Knauf Framing","WAL-02"},
                {"ID_WA_WAL 02 Mada Framing","WAL-02"},
                {"ID_WA_WAL 03 Knauf Framing","WAL-03"},
                {"ID_WA_WAL 03 Mada Framing","WAL-03"},
                {"ID_WA_WAL 03A Knauf Framing","WAL-03A"},
                {"ID_WA_WAL 04 Knauf Framing","WAL-04"},
                {"ID_WA_WAL 04A Knauf Framing","WAL-04A"},
                {"ID_WA_WAL 04 Mada Framing","WAL-04"},
                {"ID_WA_WAL 05 Knauf Framing","WAL-05"},
                {"ID_WA_WAL 05A Knauf Framing","WAL-05A"},
                {"ID_WA_WAL 05 Mada Framing","WAL-05"},
                {"ID_WA_WAL 06 Kanuf Framing","WAL-06"},
                {"ID_WA_WAL 06 Mada Framing","WAL-06"},
                {"ID_WA_WAL 06A Kanuf Framing","WAL-06A"},
                {"ID_WA_WAL 07 Knauf Framing","WAL-07"},
                {"ID_WA_WAL 07 Mada Framing","WAL-07"},
                {"ID_WA_WAL 08 Knauf Framing","WAL-08"},
                {"ID_WA_WAL 08 Mada Framing","WAL-08"},
                {"ID_WA_WAL 09 Knauf Framing","WAL-09"},
                {"ID_WA_WAL 09 Mada Framing","WAL-09"},
                {"ID_WA_WAL 10 Knauf Framing 1 side","WAL-10"},
                {"ID_WA_WAL 10 Mada Framing 1 side","WAL-10"},
                {"ID_WA_WAL 11 Knauf Framing 1 side","WAL-11"},
                {"ID_WA_WAL 11 Mada Framing 1 side","WAL-11"},
                {"ID_WA_WAL 11A Knauf Framing 1 side","WAL-11A"},
                {"ID_WA_WAL 12 Knauf Framing","WAL-12"},
                {"ID_WA_WAL 12 Mada Framing","WAL-12"},
                {"ID_WA_WAL 12.1 Mada Framing","WAL-12"},
                {"ID_WA_WAL 12A Knauf Framing","WAL-12A"},
                {"ID_WA_WAL 13 Knauf Framing","WAL-13"},
                {"ID_WA_WAL 13A Knauf Framing","WAL-13A"},
                {"ID_WA_WAL 13B Knauf Framing","WAL-13B"},
                {"ID_WA_WAL 14  Knauf Framing 1 side 2","WAL-14"},
                {"ID_WA_WAL 14A  Knauf Framing 1 side","WAL-14A"},
                {"ID_WA_WAL 16  Knauf Framing 1 side","WAL-16"},
                {"ID_WA_WAL 16A  Knauf Framing 1 side","WAL-16A"},
                {"ID_WA_WAL 16B  Knauf Framing 1 side","WAL-16B"},
                {"ID_WA_WAL 17  Knauf Framing","WAL-17"},
                {"ID_WA_WAL-01 - 12.5mm Knauf GC - MRB","WAL-01"},
                {"ID_WA_WAL-01 - 12.5mm Knauf GC - MRB (NS)","WAL-01"},
                {"ID_WA_WAL-01 Mada Plaster Board","WAL-01"},
                {"ID_WA_WAL-02 - 2-12.5mm Knauf GC - Regular Board","WAL-02"},
                {"ID_WA_WAL-03 - 12.5mm Knauf Aquapanel Indoor","WAL-03"},
                {"ID_WA_WAL-03A - Side A 15.9mm Knauf GB - WRTX Board","WAL-03A"},
                {"ID_WA_WAL-03A - Side B 12.5mm Aquapanel Indoor","WAL-03A"},
                {"ID_WA_WAL-04 - 15.9mm Knauf GB - WRTX Board","WAL-04"},
                {"ID_WA_WAL-04A - 15.9mm Knauf GB - WRTX Board","WAL-04A"},
                {"ID_WA_WAL-05 - 12.5mm Knauf  GC - MRB","WAL-05"},
                {"ID_WA_WAL-05A - 2-12.5mm Knauf  GC - MRB","WAL-05A"},
                {"ID_WA_WAL-06 - 15.9mm Knauf GW - TX Board","WAL-06"},
                {"ID_WA_WAL-06A - 15.9mm Knauf GW - TX Board","WAL-06A"},
                {"ID_WA_WAL-07 - 12.5 Knauf GC - Regular Board","WAL-07"},
                {"ID_WA_WAL-08  - 12.5 Knauf GC - Regular Board","WAL-08"},
                {"ID_WA_WAL-09 - 12.5mm Knauf GC - Regular Board","WAL-09"},
                {"ID_WA_WAL-10 - 2-12.5mm Knauf GC - Regular Board","WAL-10"},
                {"ID_WA_WAL-11 - 12.5mm Knauf GC - Regular Board","WAL-11"},
                {"ID_WA_WAL-11A - 12.5mm Knauf GC - Regular Board","WAL-11A"},
                {"ID_WA_WAL-11B - 12.5mm Knauf GC - MRB","WAL-11B"},
                {"ID_WA_WAL-12 - 12.5mm Knauf GC - Regular Board","WAL-12"},
                {"ID_WA_WAL-12A - 12.5mm Knauf GC - MRB","WAL-12A"},
                {"ID_WA_WAL-13 - 2-12.5mm Knauf GC - Regular Board","WAL-13"},
                {"ID_WA_WAL-13A - 2-12.5mm Knauf GC - RB & MRB","WAL-13A"},
                {"ID_WA_WAL-13B - 2-12.5mm Knauf GC - RB & AP","WAL-13B"},
                {"ID_WA_WAL-13B - 2-12.5mm Knauf GC - RB & MRB","WAL-13B"},
                {"ID_WA_WAL-14 - 2-12.5mm Knauf GC - Regular Board","WAL-14"},
                {"ID_WA_WAL-14A - 2-12.5mm Knauf GC - Regular Board","WAL-14A"},
                {"ID_WA_WAL-15  - 12.5 Knauf GC - Regular Board","WAL-15"},
                {"ID_WA_WAL-15A - 12.5mm Knauf GC - MRB","WAL-15A"},
                {"ID_WA_WAL-16 - 2-12.5mm Knauf GC - Regular Board","WAL-16"},
                {"ID_WA_WAL-16A - 12.5mm Knauf GC - MRB","WAL-16A"},
                {"ID_WA_WAL-16B - 12.5mm Knauf GC - Aqua Panel","WAL-16B"},
                {"ID_WA_WAL-16B - 12.5mm Knauf GC - Regular Board","WAL-16B"},
                {"ID_WA_WAL-17 - 12.5mm Knauf GC - MRB","WAL-17"},
                {"ID_WA_WAL-18 - 15.9mm Knauf GW - TX Board","WAL-18"},
                {"ID_WA_WAL-19 - 15.9mm Knauf GB - WRTX Board","WAL-19"},
                {"ID_WA_WAL-20 - Side A 15.9mm Knauf GB - WRTX Board","WAL-20"},
                {"ID_WA_WAL-20 - Side B 12.5mm Aquapanel Indoor","WAL-20"},
                {"ID_WA_WAL-21 - Side A 15.9mm Knauf GB - WRTX Board","WAL-21"},
                {"ID_WA_WAL-21 - Side B 12.5mm Aquapanel Indoor","WAL-21"},
                {"ID_WA_WAL-22 - Side A 12.5mm Knauf GC - MRB 2","WAL-22"},
                {"ID_WA_WAL-22 - Side B 12.5mm Aquapanel Indoor","WAL-22"}
                // Add additional mappings here
            };

            // Get the active document in Revit
            Document doc = commandData.Application.ActiveUIDocument.Document;

            // Start a transaction
            using (Transaction transaction = new Transaction(doc, "Set Wall Type Marks"))
            {
                transaction.Start();

                // Get all wall types in the document
                FilteredElementCollector collector = new FilteredElementCollector(doc)
                    .OfClass(typeof(WallType));

                foreach (WallType wallType in collector)
                {
                    // Get the wall type name
                    string wallTypeName = wallType.Name;

                    // Check if the wall type name contains any of the keys in the dictionary
                    foreach (var entry in wallTypeMarkMappings)
                    {
                        if (wallTypeName.Contains(entry.Key))
                        {
                            // Get the Type Mark parameter
                            Parameter typeMarkParam = wallType.LookupParameter("Type Mark");

                            // Set the Type Mark to the mapped value if writable
                            if (typeMarkParam != null && !typeMarkParam.IsReadOnly)
                            {
                                typeMarkParam.Set(entry.Value);
                            }
                            break;
                        }
                    }
                }

                transaction.Commit();
            }

            return Result.Succeeded;
        }
    }
}
