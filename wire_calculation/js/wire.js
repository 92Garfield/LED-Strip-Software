import { AWG_DATA } from './data/awg-data.js';
import { MATERIAL_DATA } from './data/material-data.js';

export class Wire {
    /**
     * @param {number} crossSection conductor cross section in mm^2
     * @param {string} [label] display name
     */
    constructor(crossSection, label = '') {
        this.crossSection = crossSection;
        this.label = label;
    }

    static fromAwg(awg) {
        const entry = AWG_DATA.find((e) => e.awg === String(awg));
        if (!entry) {
            throw new Error(`Unknown AWG value: ${awg}`);
        }
        const wire = Wire.fromDiameter(entry.diameter);
        wire.label = `AWG ${entry.awg}`;
        return wire;
    }

    static fromDiameter(diameter) {
        return new Wire((Math.PI * diameter * diameter) / 4, `Ø ${diameter} mm`);
    }

    static fromCrossSection(crossSection) {
        return new Wire(crossSection, `${crossSection} mm²`);
    }

    /** conductor diameter in mm */
    get diameter() {
        return Math.sqrt((4 * this.crossSection) / Math.PI);
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
