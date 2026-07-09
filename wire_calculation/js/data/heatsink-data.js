// Heatsink materials and ways of attaching the wire/strip to the heatsink
export const HEATSINK_DATA = {
    materials: [
        // surfaceEfficiency derates the sink surface for how evenly the
        // material spreads heat across it (isothermal-sink assumption)
        { id: 'aluminium', name: 'Aluminium', thermalConductivity: 205, specificHeat: 897, surfaceEfficiency: 0.95 },
        { id: 'copper',    name: 'Copper',    thermalConductivity: 385, specificHeat: 385, surfaceEfficiency: 1.0 },
        { id: 'steel',     name: 'Steel',     thermalConductivity: 50,  specificHeat: 490, surfaceEfficiency: 0.7 },
    ],
    // conductance of the joint in W / (m^2 * K), across the contact area
    connections: [
        { id: 'factory-tape',    name: "Strip's own glue (factory 3M tape)",   conductance: 1500 },
        { id: 'thermal-adhesive',name: 'Thermal adhesive',                     conductance: 3000 },
        { id: 'thermal-paste',   name: 'Thermal paste, clamped / screwed',     conductance: 5000 },
        { id: 'ordinary-glue',   name: 'Ordinary glue',                        conductance: 500 },
        { id: 'silicone-jacket', name: 'Silicone jacket (IP65/67) in between', conductance: 150 },
        { id: 'loose',           name: 'Cable ties / loose contact',           conductance: 100 },
    ],
};
