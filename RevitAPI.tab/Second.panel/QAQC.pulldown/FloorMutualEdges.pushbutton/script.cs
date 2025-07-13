using System;
using System.Collections.Generic;
using Autodesk.Revit.UI;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI.Selection;

namespace FloorBoundaryUpdater
{
    [Autodesk.Revit.Attributes.Transaction(Autodesk.Revit.Attributes.TransactionMode.Manual)]
    public class MatchFloorCutShape : IExternalCommand
    {
        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            UIDocument uidoc = commandData.Application.ActiveUIDocument;
            Document doc = uidoc.Document;

            try
            {
                Reference pickedRef = uidoc.Selection.PickObject(ObjectType.Element, "Select a floor to match its cut shape");
                Floor floor = doc.GetElement(pickedRef) as Floor;
                floortypeid = FilteredElementCollector
                

                if (floor == null)
                {
                    message = "Selected element is not a floor.";
                    return Result.Failed;
                }

                IList<CurveLoop> cutProfile = GetFloorCutProfile(floor);

                if (cutProfile == null || cutProfile.Count == 0)
                {
                    message = "Could not determine the cut shape of the floor.";
                    return Result.Failed;
                }

                using (Transaction trans = new Transaction(doc, "Update Floor Boundary"))
                {
                    trans.Start();

                    FloorProfile floorProfile = FloorProfile.Create(doc, cutProfile );
                    floor.SetProfile(floorProfile);

                    trans.Commit();
                }

                return Result.Succeeded;
            }
            catch (Exception ex)
            {
                message = ex.Message;
                return Result.Failed;
            }
        }

        private IList<CurveLoop> GetFloorCutProfile(Floor floor)
        {
            List<CurveLoop> profile = new List<CurveLoop>();
            Options options = new Options { ComputeReferences = true };
            GeometryElement geomElement = floor.get_Geometry(options);

            foreach (GeometryObject geomObj in geomElement)
            {
                Solid solid = geomObj as Solid;
                if (solid != null && solid.Faces.Size > 0)
                {
                    foreach (Face face in solid.Faces)
                    {
                        if (face is PlanarFace && IsTopFace(face, floor))
                        {
                            CurveLoop loop = GetFaceBoundary(face);
                            if (loop != null)
                            {
                                profile.Add(loop);
                            }
                        }
                    }
                }
            }

            return profile;
        }

        private bool IsTopFace(Face face, Floor floor)
        {
            PlanarFace planarFace = face as PlanarFace;
            return planarFace != null && planarFace.FaceNormal.IsAlmostEqualTo(XYZ.BasisZ);
        }

        private CurveLoop GetFaceBoundary(Face face)
        {
            CurveLoop curveLoop = new CurveLoop();
            EdgeArray edges = face.EdgeLoops.get_Item(0);

            foreach (Edge edge in edges)
            {
                Curve curve = edge.AsCurve();
                if (curve != null)
                {
                    curveLoop.Append(curve);
                }
            }

            return curveLoop;
        }
    }
}
