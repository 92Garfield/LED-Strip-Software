// PCB copper and IPC-2221 trace heating parameters
export const PCB_DATA = {
    // standard copper foil weights: oz/ft^2 -> finished thickness in mm
    copperWeights: [
        { id: '0.5oz', name: '0.5 oz (17.5 µm)', thickness: 0.0175 },
        { id: '1oz',   name: '1 oz (35 µm) — standard', thickness: 0.035 },
        { id: '2oz',   name: '2 oz (70 µm)', thickness: 0.070 },
        { id: '3oz',   name: '3 oz (105 µm)', thickness: 0.105 },
    ],
    // IPC-2221 fitted curve I = k * dT^0.44 * A^0.725 (A in mil^2)
    ipc2221: {
        layers: [
            { id: 'external', name: 'External (outer layer)', k: 0.048 },
            { id: 'internal', name: 'Internal (inner layer)', k: 0.024 },
        ],
        currentExponent: 0.725,
        tempExponent: 0.44,
        // stated validity limits of the IPC-2221 chart
        maxCurrent: 35, // A
        maxTempRise: 100, // K
    },
    // temperature rises above ambient to evaluate, in K
    tempRises: [10, 20, 30],
    // mm^2 -> mil^2 (1 mm = 39.3701 mil)
    mm2ToMil2: 1550.0031,
};