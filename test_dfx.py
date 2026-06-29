from importer.dxf_importer import DXFImporter

imp = DXFImporter()

doc = imp.load(r"rochette.dxf")

print()

print("Nombre d'entités :", len(doc.entities))

print(type(doc.entities[0]))