import { THERMAL_DATA } from './data/thermal-data.js';

export class HeatsinkCalculator {
    /**
     * Two-node steady-state model: the wire couples into the heatsink through
     * its insulation plus the chosen connection layer, over a contact strip
     * as wide as the wire. The upper half of the wire surface and the whole
     * heatsink surface shed heat to still air.
     *
     * @param {import('./wire.js').Wire} wire
     * @param {number} length wire length in m
     * @param {number} heatGeneration total ohmic loss in W
     * @param {{massPerMeter: number, surfacePerMeter: number,
     *          material: {specificHeat: number, surfaceEfficiency: number},
     *          connection: {conductance: number}}} config
     *        massPerMeter in kg/m, surfacePerMeter in m^2/m
     * @returns {{contactConductance: number, sinkArea: number, timeConstant: number,
     *            heatUpTime: number, averageHeatUpRate: number,
     *            perAmbient: Array<{ambient: number, maxDissipation: number, netHeat: number,
     *            equilibriumTemp: number, sinkTemp: number, safe: boolean}>}}
     */
    calculate(wire, length, heatGeneration, config) {
        const { heatTransferCoefficient: h, insulation, ambientTemperatures } = THERMAL_DATA;

        const outerDiameter = (wire.diameter + 2 * insulation.thickness) / 1000; // m
        const exposedArea = (Math.PI * outerDiameter * length) / 2;
        const contactArea = outerDiameter * length;

        // connection layer in series with the wire's own insulation
        const insulationConductance = insulation.conductivity / (insulation.thickness / 1000); // W/m²K
        const contactConductance =
            1 / (1 / config.connection.conductance + 1 / insulationConductance);

        const gWireAir = h * exposedArea; // W/K, wire -> air
        const gContact = contactConductance * contactArea; // W/K, wire -> sink
        const sinkArea = config.surfacePerMeter * length * config.material.surfaceEfficiency;
        const gSinkAir = h * sinkArea; // W/K, sink -> air
        const gViaSink = gContact + gSinkAir > 0
            ? (gContact * gSinkAir) / (gContact + gSinkAir)
            : 0;
        const gTotal = gWireAir + gViaSink;

        // how quickly the sink mass warms up (lumped capacity)
        const heatCapacity = config.massPerMeter * length * config.material.specificHeat; // J/K
        const timeConstant = gSinkAir > 0 ? heatCapacity / gSinkAir : Infinity; // s

        // temperature rises above ambient are the same for every ambient
        const wireRise = gTotal > 0 ? heatGeneration / gTotal : Infinity;
        const sinkRise = gContact + gSinkAir > 0
            ? (gContact * wireRise) / (gContact + gSinkAir)
            : 0;

        // ~95 % of the final rise is reached after 3 time constants
        const heatUpTime = 3 * timeConstant; // s
        let averageHeatUpRate; // degC per minute
        if (!Number.isFinite(heatUpTime)) {
            averageHeatUpRate = 0; // never gets there
        } else if (heatUpTime === 0) {
            averageHeatUpRate = sinkRise > 0 ? Infinity : 0; // massless sink heats instantly
        } else {
            averageHeatUpRate = (0.95 * sinkRise) / (heatUpTime / 60);
        }

        const perAmbient = ambientTemperatures.map((ambient) => {
            const equilibriumTemp = ambient + wireRise;
            const sinkTemp = ambient + sinkRise;
            const maxDissipation = gTotal * (insulation.maxTemperature - ambient);
            return {
                ambient,
                maxDissipation,
                netHeat: heatGeneration - maxDissipation,
                equilibriumTemp,
                sinkTemp,
                safe: equilibriumTemp <= insulation.maxTemperature,
            };
        });

        return { contactConductance, sinkArea, timeConstant, heatUpTime, averageHeatUpRate, perAmbient };
    }
}
