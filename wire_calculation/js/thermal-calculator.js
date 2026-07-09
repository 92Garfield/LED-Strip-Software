import { THERMAL_DATA } from './data/thermal-data.js';

export class ThermalCalculator {
    /**
     * Simplified steady-state model: the insulated wire dissipates heat to
     * still air via a combined convection/radiation coefficient. The maximum
     * heat sink is reached when the insulation surface sits at its rated
     * maximum temperature.
     *
     * @param {import('./wire.js').Wire} wire
     * @param {number} length wire length in m
     * @param {number} heatGeneration total ohmic loss in W
     * @returns {{heatGeneration: number, surfaceArea: number, outerDiameter: number,
     *            perAmbient: Array<{ambient: number, maxDissipation: number,
     *            netHeat: number, equilibriumTemp: number, safe: boolean}>}}
     */
    calculate(wire, length, heatGeneration) {
        const { heatTransferCoefficient: h, insulation, ambientTemperatures } = THERMAL_DATA;

        const outerDiameter = wire.diameter + 2 * insulation.thickness; // mm
        const surfaceArea = Math.PI * (outerDiameter / 1000) * length; // m^2

        const perAmbient = ambientTemperatures.map((ambient) => {
            const maxDissipation = h * surfaceArea * (insulation.maxTemperature - ambient);
            const netHeat = heatGeneration - maxDissipation;
            const equilibriumTemp = surfaceArea > 0
                ? ambient + heatGeneration / (h * surfaceArea)
                : Infinity;
            return {
                ambient,
                maxDissipation,
                netHeat,
                equilibriumTemp,
                safe: equilibriumTemp <= insulation.maxTemperature,
            };
        });

        return { heatGeneration, surfaceArea, outerDiameter, perAmbient };
    }
}
