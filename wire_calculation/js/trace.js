import { MATERIAL_DATA } from './data/material-data.js';
import { PCB_DATA } from './data/pcb-data.js';

/**
 * A rectangular PCB copper trace. Exposes the same electrical interface as
 * Wire (crossSection, label, resistancePerMeter, resistance) so the Ohm's law
 * and comparison calculators work on both.
 */
export class Trace {
    /**
     * @param {number} width trace width in mm
     * @param {{id: string, name: string, thickness: number}} copperWeight
     */
    constructor(width, copperWeight) {
        this.width = width;
        this.thickness = copperWeight.thickness; // mm
        this.copperWeight = copperWeight;
        this.crossSection = width * this.thickness; // mm^2
        this.label = `Trace ${width} mm × ${copperWeight.name.split(' (')[0]}`;
    }

    static fromWidth(width, copperWeightId) {
        const weight = PCB_DATA.copperWeights.find((w) => w.id === copperWeightId);
        if (!weight) {
            throw new Error(`Unknown copper weight: ${copperWeightId}`);
        }
        return new Trace(width, weight);
    }

    /** resistance per meter in Ohm (copper, 20 degC) */
    get resistancePerMeter() {
        return MATERIAL_DATA.copper.resistivity / this.crossSection;
    }

    /** total resistance in Ohm for a given length in m */
    resistance(length) {
        return this.resistancePerMeter * length;
    }
}