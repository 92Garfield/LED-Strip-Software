export class OhmsLawCalculator {
    /**
     * @param {import('./wire.js').Wire} wire
     * @param {number} length wire length in m
     * @param {number} current in A
     * @returns {{resistance: number, voltageDrop: number, powerLoss: number, powerLossPerMeter: number}}
     */
    calculate(wire, length, current) {
        const resistance = wire.resistance(length);
        const voltageDrop = current * resistance;
        const powerLoss = current * current * resistance;
        return {
            resistance,
            voltageDrop,
            powerLoss,
            powerLossPerMeter: length > 0 ? powerLoss / length : 0,
        };
    }
}
