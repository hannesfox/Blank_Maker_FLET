#rohteilrechner.py
import cadquery as cq
import os
import math

def process_step_file(file_path):
    # STEP-Datei mit CadQuery laden
    try:
        result = cq.importers.importStep(file_path)
        if not result:
            raise ValueError("Die STEP/STP-Datei konnte nicht geladen werden oder ist ungültig.")
        if isinstance(result, cq.Workplane):
            solid = result.val()
        else:
            solid = result
    except Exception as e:
        raise e

    # Dimensionen der Bounding Box berechnen
    bbox = solid.BoundingBox()
    x_size = bbox.xmax - bbox.xmin
    y_size = bbox.ymax - bbox.ymin
    z_size = bbox.zmax - bbox.zmin

    # Originalgröße beibehalten
    original_size = {
        'X': x_size,
        'Y': y_size,
        'Z': z_size
    }

    # Teile ausrichten
    sizes = [(x_size, 'x'), (y_size, 'y'), (z_size, 'z')]
    sizes.sort(reverse=True)  

    # Größte soll X sein, zweitgrößte Y, kleinste Z
    largest_dim, second_largest_dim, smallest_dim = sizes[0][1], sizes[1][1], sizes[2][1]

    # Rotation basierend auf der Analyse der Größen
    if largest_dim != 'x':  # Wenn die größte Dimension nicht X ist, drehen 
        if largest_dim == 'y':
            solid = solid.rotate((0, 0, 1), (0, 0, 0), 90)
        elif largest_dim == 'z':
            solid = solid.rotate((0, 1, 0), (0, 0, 0), 90)

    # Zweitgrößte Y
    bbox = solid.BoundingBox()  
    x_size = bbox.xmax - bbox.xmin
    y_size = bbox.ymax - bbox.ymin
    z_size = bbox.zmax - bbox.zmin

    # Wenn Y nicht die zweitgrößte ist, drehen X
    if second_largest_dim != 'y':
        if second_largest_dim == 'z':
            solid = solid.rotate((1, 0, 0), (0, 0, 0), 90)

    # Endgültige Größen berechnen
    bbox = solid.BoundingBox()  
    x_size = bbox.xmax - bbox.xmin
    y_size = bbox.ymax - bbox.ymin
    z_size = bbox.zmax - bbox.zmin

    # Rohmaße berechnen gemäß den neuen Regeln
    # X: Original +5 mm, auf ganze Zahl aufgerundet
    new_x = int(math.ceil(x_size + 5))
    
    # Y: Original +5, wenn Ergebnis <=30, auf 5er aufrunden, sonst auf 10er
    temp_y = y_size + 5
    if temp_y <= 30:
        new_y = int(math.ceil(temp_y / 5) * 5)
    else:
        new_y = int(math.ceil(temp_y / 10) * 10)
    
    # Z: Original +5, wenn <=30 auf 5er, sonst auf 10er
    z_plus5 = z_size + 5
    if z_plus5 <= 30:
        new_z = int(math.ceil(z_plus5 / 5) * 5)
    else:
        new_z = int(math.ceil(z_plus5 / 10) * 10)

    # Ergebnis zurückgeben
    result = {
        'original_size': original_size,  # Fließkommazahlen
        'raw_part_size': {'X': new_x, 'Y': new_y, 'Z': new_z}  # Ganzzahlen
    }
    return result
