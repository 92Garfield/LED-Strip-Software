// Simplified thermal model parameters for an insulated wire in still air
export const THERMAL_DATA = {
    // combined natural convection + radiation coefficient, W / (m^2 * K)
    heatTransferCoefficient: 12,
    insulation: {
        name: 'PVC (common household / hookup wire)',
        // typical radial insulation thickness in mm
        thickness: 0.8,
        // thermal conductivity of PVC in W / (m * K)
        conductivity: 0.17,
        // maximum continuous operating temperature of PVC insulation in degC
        maxTemperature: 70,
    },
    // room temperatures to evaluate, in degC
    ambientTemperatures: [25, 40],
};
