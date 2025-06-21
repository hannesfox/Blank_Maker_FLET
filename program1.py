#program1
import ezdxf


def create_rectangle(length, width, height):
    dwg = ezdxf.new('R2010')
    msp = dwg.modelspace()

    # Rechteck mit den angegebenen Länge und Breite erstellen
    center = (0, 0, -4)
    points = [
        (center[0] - length / 2, center[1] - width / 2, center[2]),
        (center[0] + length / 2, center[1] - width / 2, center[2]),
        (center[0] + length / 2, center[1] + width / 2, center[2]),
        (center[0] - length / 2, center[1] + width / 2, center[2]),
        (center[0] - length / 2, center[1] - width / 2, center[2]),
    ]
    msp.add_polyline3d(points, dxfattribs={'layer': 'Roh', 'color': 198})

    # Kopie des Rechtecks erstellen
    copy_points = [(x, y, z + height) for x, y, z in points]
    msp.add_polyline3d(copy_points, dxfattribs={'layer': 'Roh', 'color': 198})

    # Text mit den angegebenen Seitenlängen und Höhe hinzufügen
    text = f"X: {length} mm\n Y: {width} mm\n Z: {height} mm"
    text = msp.add_text(text, dxfattribs={'height': 5, 'layer': 'Roh', 'color': 206})

    x, y = (-length / 2), (width / 2) + 4
    text.dxf.insert = (x, y, height - 4)
    text.dxf.rotation = 0

    dwg.saveas("!rohteil.dxf")


