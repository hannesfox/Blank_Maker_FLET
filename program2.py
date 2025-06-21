#program2
import ezdxf

def create_circle(diameter, height):
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Erster Kreis
    radius = diameter / 2
    center = (0, 0, -6)
    circle1 = msp.add_circle(center, radius,dxfattribs={'layer': 'Roh', 'color': 198})

    # Zweiter Kreis
    center = (0, 0, height -6)
    circle2 = msp.add_circle(center, radius,dxfattribs={'layer': 'Roh', 'color': 198})

    # Bemaßung hinzufügen
    mtext_diameter = msp.add_mtext(f"Diameter = {diameter}", dxfattribs={'layer': 'Roh', 'color': 198})
    mtext_diameter.set_location((radius * 1.2, 4, height -3))

    mtext_height = msp.add_mtext(f"Height = {height}", dxfattribs={'layer': 'Roh', 'color': 206})
    mtext_height.set_location((radius * 1.2, -4, height - 3))

    # DXF-Datei speichern
    doc.saveas("!rohteil.dxf")

def on_button_click():
    diameter = float(entry_diameter.get())
    height = float(entry_height.get())
    create_circle(diameter, height)

def on_enter_pressed(event):
    if entry_diameter.get() and entry_height.get():
        diameter = float(entry_diameter.get())
        height = float(entry_height.get())
        create_circle(diameter, height)
