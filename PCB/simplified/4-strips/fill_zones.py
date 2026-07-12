"""Refills the zones of led-controller-simple.kicad_pcb (run after build_board.py)."""
import pcbnew

b = pcbnew.LoadBoard("led-controller-simple.kicad_pcb")
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save("led-controller-simple.kicad_pcb")
print("zones filled:", b.Zones().size() if hasattr(b.Zones(), "size") else len(b.Zones()))
