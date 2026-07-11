import { PCB_DATA } from './data/pcb-data.js';
import { THERMAL_DATA } from './data/thermal-data.js';

export class TraceThermalCalculator {
    /**
     * IPC-2221 trace heating model: I = k * dT^0.44 * A^0.725 with the
     * cross section A in mil^2. Solved three ways: temperature rise at the
     * given current, maximum current for standard rises, and the trace width
     * required to stay at those rises with the given current.
     *
     * @param {import('./trace.js').Trace} trace
     * @param {number} current in A
     * @param {string} layerId 'external' or 'internal'
     * @returns {{layer: {id: string, name: string, k: number}, tempRise: number,
     *            withinChart: boolean,
     *            perAmbient: Array<{ambient: number, traceTemp: number}>,
     *            perRise: Array<{rise: number, maxCurrent: number, requiredWidth: number}>}}
     */
    calculate(trace, current, layerId) {
        const { ipc2221, tempRises, mm2ToMil2 } = PCB_DATA;
        const layer = ipc2221.layers.find((l) => l.id === layerId);
        const { k } = layer;
        const b = ipc2221.currentExponent;
        const c = ipc2221.tempExponent;

        const areaMil2 = trace.crossSection * mm2ToMil2;

        // dT = (I / (k * A^b))^(1/c)
        const tempRise = current > 0
            ? Math.pow(current / (k * Math.pow(areaMil2, b)), 1 / c)
            : 0;

        const perAmbient = THERMAL_DATA.ambientTemperatures.map((ambient) => ({
            ambient,
            traceTemp: ambient + tempRise,
        }));

        const perRise = tempRises.map((rise) => {
            const maxCurrent = k * Math.pow(rise, c) * Math.pow(areaMil2, b);
            // A = (I / (k * dT^c))^(1/b), then width = A / thickness
            const requiredArea = current > 0
                ? Math.pow(current / (k * Math.pow(rise, c)), 1 / b) / mm2ToMil2
                : 0;
            return {
                rise,
                maxCurrent,
                requiredWidth: requiredArea / trace.thickness,
            };
        });

        const withinChart = current <= ipc2221.maxCurrent && tempRise <= ipc2221.maxTempRise;

        return { layer, tempRise, withinChart, perAmbient, perRise };
    }
}