import { Wire } from './wire.js';
import { Trace } from './trace.js';
import { OhmsLawCalculator } from './ohms-law-calculator.js';
import { ThermalCalculator } from './thermal-calculator.js';
import { HeatsinkCalculator } from './heatsink-calculator.js';
import { TraceThermalCalculator } from './trace-thermal-calculator.js';
import { AWG_DATA } from './data/awg-data.js';
import { THERMAL_DATA } from './data/thermal-data.js';
import { HEATSINK_DATA } from './data/heatsink-data.js';
import { HOUSEHOLD_WIRE_DATA } from './data/household-wire-data.js';
import { PCB_DATA } from './data/pcb-data.js';

export class App {
    constructor() {
        this.ohmsLaw = new OhmsLawCalculator();
        this.thermal = new ThermalCalculator();
        this.heatsink = new HeatsinkCalculator();
        this.traceThermal = new TraceThermalCalculator();
        this.mainsVoltage = 230;
    }

    init() {
        this.el = {
            sizeMode: document.getElementById('size-mode'),
            awgField: document.getElementById('awg-field'),
            awgSelect: document.getElementById('awg-select'),
            sizeField: document.getElementById('size-field'),
            sizeLabel: document.getElementById('size-label'),
            sizeInput: document.getElementById('size-input'),
            traceFields: document.querySelectorAll('.trace-field'),
            traceWidth: document.getElementById('trace-width'),
            copperWeight: document.getElementById('copper-weight'),
            traceLayer: document.getElementById('trace-layer'),
            stepWireThermal: document.getElementById('step-wire-thermal'),
            stepTraceThermal: document.getElementById('step-trace-thermal'),
            traceThermalOutput: document.getElementById('trace-thermal-output'),
            lengthInput: document.getElementById('length-input'),
            currentInput: document.getElementById('current-input'),
            heatsinkMass: document.getElementById('heatsink-mass'),
            heatsinkSurface: document.getElementById('heatsink-surface'),
            heatsinkMaterial: document.getElementById('heatsink-material'),
            heatsinkConnection: document.getElementById('heatsink-connection'),
            inputSummary: document.getElementById('input-summary'),
            ohmsOutput: document.getElementById('ohms-output'),
            thermalOutput: document.getElementById('thermal-output'),
            comparisonOutput: document.getElementById('comparison-output'),
        };

        for (const entry of AWG_DATA) {
            const option = document.createElement('option');
            option.value = entry.awg;
            option.textContent = `AWG ${entry.awg}  (${entry.diameter} mm)`;
            this.el.awgSelect.appendChild(option);
        }
        this.el.awgSelect.value = '18';

        for (const weight of PCB_DATA.copperWeights) {
            const option = document.createElement('option');
            option.value = weight.id;
            option.textContent = weight.name;
            this.el.copperWeight.appendChild(option);
        }
        this.el.copperWeight.value = '1oz';
        for (const layer of PCB_DATA.ipc2221.layers) {
            const option = document.createElement('option');
            option.value = layer.id;
            option.textContent = layer.name;
            this.el.traceLayer.appendChild(option);
        }

        for (const material of HEATSINK_DATA.materials) {
            const option = document.createElement('option');
            option.value = material.id;
            option.textContent = material.name;
            this.el.heatsinkMaterial.appendChild(option);
        }
        for (const connection of HEATSINK_DATA.connections) {
            const option = document.createElement('option');
            option.value = connection.id;
            option.textContent = connection.name;
            this.el.heatsinkConnection.appendChild(option);
        }

        const rerun = () => this.update();
        this.el.sizeMode.addEventListener('change', () => {
            this.onModeChange();
            this.update();
        });
        for (const input of [this.el.awgSelect, this.el.sizeInput,
                             this.el.traceWidth, this.el.copperWeight, this.el.traceLayer,
                             this.el.lengthInput, this.el.currentInput,
                             this.el.heatsinkMass, this.el.heatsinkSurface,
                             this.el.heatsinkMaterial, this.el.heatsinkConnection]) {
            input.addEventListener('input', rerun);
        }

        this.onModeChange();
        this.update();
    }

    onModeChange() {
        const mode = this.el.sizeMode.value;
        this.el.awgField.classList.toggle('hidden', mode !== 'awg');
        this.el.sizeField.classList.toggle('hidden', mode === 'awg' || mode === 'trace');
        for (const field of this.el.traceFields) {
            field.classList.toggle('hidden', mode !== 'trace');
        }
        this.el.stepWireThermal.classList.toggle('hidden', mode === 'trace');
        this.el.stepTraceThermal.classList.toggle('hidden', mode !== 'trace');
        if (mode === 'diameter') {
            this.el.sizeLabel.textContent = 'Diameter (mm)';
        } else if (mode === 'crossSection') {
            this.el.sizeLabel.textContent = 'Cross section (mm²)';
        }
    }

    buildConductor() {
        const mode = this.el.sizeMode.value;
        if (mode === 'awg') {
            return Wire.fromAwg(this.el.awgSelect.value);
        }
        if (mode === 'trace') {
            const width = parseFloat(this.el.traceWidth.value);
            if (!(width > 0)) {
                throw new Error('Please enter a positive trace width.');
            }
            return Trace.fromWidth(width, this.el.copperWeight.value);
        }
        const value = parseFloat(this.el.sizeInput.value);
        if (!(value > 0)) {
            throw new Error('Please enter a positive wire size.');
        }
        return mode === 'diameter' ? Wire.fromDiameter(value) : Wire.fromCrossSection(value);
    }

    buildHeatsinkConfig() {
        const massPerMeter = parseFloat(this.el.heatsinkMass.value);
        const surfacePerMeter = parseFloat(this.el.heatsinkSurface.value);
        if (!(massPerMeter >= 0)) {
            throw new Error('Please enter a heatsink mass of 0 g/m or more.');
        }
        if (!(surfacePerMeter >= 0)) {
            throw new Error('Please enter a heatsink surface of 0 cm²/m or more.');
        }
        return {
            massPerMeter: massPerMeter / 1000, // g/m -> kg/m
            surfacePerMeter: surfacePerMeter / 10000, // cm²/m -> m²/m
            material: HEATSINK_DATA.materials.find((m) => m.id === this.el.heatsinkMaterial.value),
            connection: HEATSINK_DATA.connections.find((c) => c.id === this.el.heatsinkConnection.value),
        };
    }

    update() {
        const isTrace = this.el.sizeMode.value === 'trace';
        let conductor;
        let heatsinkConfig;
        const length = parseFloat(this.el.lengthInput.value);
        const current = parseFloat(this.el.currentInput.value);
        try {
            conductor = this.buildConductor();
            if (!isTrace) heatsinkConfig = this.buildHeatsinkConfig();
            if (!(length > 0)) throw new Error('Please enter a positive length.');
            if (!(current >= 0)) throw new Error('Please enter a current of 0 A or more.');
        } catch (err) {
            const msg = `<p class="error">${err.message}</p>`;
            this.el.inputSummary.innerHTML = msg;
            this.el.ohmsOutput.innerHTML = '';
            this.el.thermalOutput.innerHTML = '';
            this.el.traceThermalOutput.innerHTML = '';
            this.el.comparisonOutput.innerHTML = '';
            return;
        }

        this.renderInputSummary(conductor);
        const ohms = this.ohmsLaw.calculate(conductor, length, current);
        this.renderOhms(ohms, current);
        let traceThermal = null;
        if (isTrace) {
            traceThermal = this.traceThermal.calculate(conductor, current, this.el.traceLayer.value);
            this.renderTraceThermal(conductor, traceThermal, current);
        } else {
            const thermal = this.thermal.calculate(conductor, length, ohms.powerLoss);
            const heatsink = this.heatsink.calculate(conductor, length, ohms.powerLoss, heatsinkConfig);
            this.renderThermal(thermal, heatsink);
        }
        this.renderComparison(conductor, length, current, traceThermal);
    }

    renderInputSummary(conductor) {
        const sizeRows = conductor instanceof Trace
            ? `<tr><td>Trace width</td><td class="num value">${this.fmt(conductor.width, 2)} mm</td></tr>
               <tr><td>Copper thickness (${conductor.copperWeight.name.split(' (')[0]})</td><td class="num value">${this.fmt(conductor.thickness * 1000, 1)} µm</td></tr>`
            : `<tr><td>Conductor diameter</td><td class="num value">${this.fmt(conductor.diameter, 3)} mm</td></tr>`;
        this.el.inputSummary.innerHTML = `
            <table>
                <tr><td>Selected conductor</td><td class="num value">${conductor.label}</td></tr>
                ${sizeRows}
                <tr><td>Cross section</td><td class="num value">${this.fmt(conductor.crossSection, 3)} mm²</td></tr>
                <tr><td>Resistance per meter (copper, 20 °C)</td><td class="num value">${this.fmt(conductor.resistancePerMeter * 1000, 2)} mΩ/m</td></tr>
            </table>`;
    }

    renderOhms(ohms, current) {
        this.el.ohmsOutput.innerHTML = `
            <table>
                <tr><td>Total wire resistance</td><td class="num value">${this.fmt(ohms.resistance, 4)} Ω</td></tr>
                <tr><td>Voltage lost on wire (U = I·R)</td><td class="num value">${this.fmt(ohms.voltageDrop, 3)} V</td></tr>
                <tr><td>Power lost (P = I²·R)</td><td class="num value">${this.fmt(ohms.powerLoss, 2)} W</td></tr>
                <tr><td>Power lost per meter</td><td class="num value">${this.fmt(ohms.powerLossPerMeter, 3)} W/m</td></tr>
            </table>
            <p class="note">At ${this.fmt(current, 1)} A the wire behaves like a resistor in series with your load.</p>`;
    }

    renderThermal(thermal, heatsink) {
        const { insulation } = THERMAL_DATA;
        const row = (label, r, sinkTemp) => {
            const netClass = r.netHeat > 0 ? 'bad' : 'good';
            const status = r.safe
                ? '<span class="good">OK — stays below insulation limit</span>'
                : '<span class="bad">Overheats — exceeds insulation limit</span>';
            return `
                <tr>
                    <td>${r.ambient} °C</td>
                    <td>${label}</td>
                    <td class="num">${this.fmt(r.maxDissipation, 2)} W</td>
                    <td class="num ${netClass}">${this.fmt(r.netHeat, 2)} W</td>
                    <td class="num">${this.fmt(r.equilibriumTemp, 1)} °C</td>
                    <td class="num">${sinkTemp === null ? '—' : `${this.fmt(sinkTemp, 1)} °C`}</td>
                    <td>${status}</td>
                </tr>`;
        };
        const rows = thermal.perAmbient.map((bare, i) => {
            const mounted = heatsink.perAmbient[i];
            return row('Bare in air', bare, null)
                + row('On heatsink', mounted, mounted.sinkTemp);
        }).join('');

        this.el.thermalOutput.innerHTML = `
            <table>
                <tr><td>Heat generation (= ohmic power loss)</td><td class="num value">${this.fmt(thermal.heatGeneration, 2)} W</td></tr>
                <tr><td>Outer diameter incl. ${insulation.name}</td><td class="num value">${this.fmt(thermal.outerDiameter, 2)} mm</td></tr>
                <tr><td>Heat-exchange surface to air (bare)</td><td class="num value">${this.fmt(thermal.surfaceArea * 10000, 1)} cm²</td></tr>
                <tr><td>Effective heatsink surface</td><td class="num value">${this.fmt(heatsink.sinkArea * 10000, 1)} cm²</td></tr>
                <tr><td>Coupling into heatsink (incl. insulation)</td><td class="num value">${this.fmt(heatsink.contactConductance, 0)} W/m²K</td></tr>
                <tr><td>Heatsink warm-up time constant</td><td class="num value">${this.fmt(heatsink.timeConstant / 60, 1)} min</td></tr>
                <tr><td>Time to heat up (≈95 % of final rise)</td><td class="num value">${this.fmt(heatsink.heatUpTime / 60, 1)} min</td></tr>
                <tr><td>Average heat-up rate</td><td class="num value">${this.fmt(heatsink.averageHeatUpRate, 2)} °C/min</td></tr>
            </table>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Room temp.</th>
                            <th>Mounting</th>
                            <th class="num">Max heat sink*</th>
                            <th class="num">Net heat generation</th>
                            <th class="num">Wire equilibrium temp.</th>
                            <th class="num">Heatsink temp.</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
            <p class="note">* Heat the wire can shed with its surface at the insulation limit of
            ${insulation.maxTemperature} °C (still air, h = ${THERMAL_DATA.heatTransferCoefficient} W/m²K).
            Negative net heat means the wire settles below the limit at the shown equilibrium temperature.
            Heatsink model: wire glued along the heatsink over a contact strip as wide as the wire; the
            connection layer acts in series with the PVC insulation — the insulation itself is usually
            the bottleneck. The time constant tells how fast the heatsink mass warms up (~63 % of its
            final rise per time constant).</p>`;
    }

    renderTraceThermal(trace, result, current) {
        const { ipc2221 } = PCB_DATA;
        const ambientRows = result.perAmbient.map((r) => `
            <tr>
                <td>${r.ambient} °C</td>
                <td class="num">${this.fmt(result.tempRise, 1)} K</td>
                <td class="num">${this.fmt(r.traceTemp, 1)} °C</td>
            </tr>`).join('');
        const riseRows = result.perRise.map((r) => {
            const ok = current <= r.maxCurrent;
            const status = ok
                ? '<span class="good">OK — trace is wide enough</span>'
                : '<span class="bad">Too narrow for this current</span>';
            return `
                <tr>
                    <td>${r.rise} K</td>
                    <td class="num">${this.fmt(r.maxCurrent, 2)} A</td>
                    <td class="num">${this.fmt(r.requiredWidth, 2)} mm</td>
                    <td>${status}</td>
                </tr>`;
        }).join('');
        const chartWarning = result.withinChart ? '' : `
            <p class="error">Outside the IPC-2221 chart range (≤ ${ipc2221.maxCurrent} A,
            ≤ ${ipc2221.maxTempRise} K rise) — treat these numbers as rough extrapolation.</p>`;

        this.el.traceThermalOutput.innerHTML = `
            <table>
                <tr><td>Layer model</td><td class="num value">${result.layer.name}</td></tr>
                <tr><td>Temperature rise at ${this.fmt(current, 1)} A</td><td class="num value">${this.fmt(result.tempRise, 1)} K</td></tr>
            </table>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr><th>Room temp.</th><th class="num">Temp. rise</th><th class="num">Trace temp.</th></tr>
                    </thead>
                    <tbody>${ambientRows}</tbody>
                </table>
            </div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Allowed rise</th>
                            <th class="num">Max current (this trace)</th>
                            <th class="num">Required width @ ${this.fmt(current, 1)} A</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>${riseRows}</tbody>
                </table>
            </div>
            ${chartWarning}
            <p class="note">IPC-2221 chart fit (I = k·ΔT<sup>0.44</sup>·A<sup>0.725</sup>): a single trace
            in still air, no neighboring heat sources. Internal layers take half the current of external
            ones. A 10 K rise is conservative, 20–30 K is a common design choice. For high-current LED
            power rails, prefer wide polygon pours over minimum-width traces — the formula's assumptions
            get conservative for very wide geometries.</p>`;
    }

    renderComparison(userWire, length, current, traceThermal = null) {
        const wires = [
            { name: `Your ${traceThermal ? 'trace' : 'wire'} — ${userWire.label}`, wire: userWire, maxCurrent: null, highlight: true },
            ...HOUSEHOLD_WIRE_DATA.map((d) => ({
                name: d.name,
                wire: Wire.fromCrossSection(d.crossSection),
                maxCurrent: d.maxCurrent,
                highlight: false,
            })),
        ];

        const rows = wires.map((entry) => {
            const ohms = this.ohmsLaw.calculate(entry.wire, length, current);
            let equilibriumTemp;
            if (entry.highlight && traceThermal) {
                // IPC trace model instead of the round-wire-in-air model
                equilibriumTemp = traceThermal.perAmbient[0].traceTemp;
            } else {
                const thermal = this.thermal.calculate(entry.wire, length, ohms.powerLoss);
                equilibriumTemp = thermal.perAmbient[0].equilibriumTemp;
            }
            const dropPercent = (ohms.voltageDrop / this.mainsVoltage) * 100;
            let rating = '—';
            if (entry.maxCurrent !== null) {
                rating = current <= entry.maxCurrent
                    ? `<span class="good">≤ ${entry.maxCurrent} A ✓</span>`
                    : `<span class="bad">> ${entry.maxCurrent} A ✗</span>`;
            }
            return `
                <tr class="${entry.highlight ? 'row-highlight' : ''}">
                    <td>${entry.name}</td>
                    <td class="num">${this.fmt(entry.wire.crossSection, 2)}</td>
                    <td class="num">${this.fmt(ohms.voltageDrop, 3)}</td>
                    <td class="num">${this.fmt(dropPercent, 2)} %</td>
                    <td class="num">${this.fmt(ohms.powerLoss, 2)}</td>
                    <td class="num">${this.fmt(equilibriumTemp, 1)}</td>
                    <td>${rating}</td>
                </tr>`;
        }).join('');

        this.el.comparisonOutput.innerHTML = `
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Wire</th>
                            <th class="num">mm²</th>
                            <th class="num">Voltage drop (V)</th>
                            <th class="num">Drop @ 230 V</th>
                            <th class="num">Power loss (W)</th>
                            <th class="num">Equil. temp @ 25 °C</th>
                            <th>Rated for ${this.fmt(current, 1)} A?</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
            <p class="note">All wires evaluated with your length (${this.fmt(length, 1)} m) and current
            (${this.fmt(current, 1)} A). European household circuits run at 230 V with breakers up to 16 A;
            ratings are typical continuous limits for fixed installation.${traceThermal
                ? ' Your trace row uses the IPC-2221 trace model for its temperature; the household rows use the wire-in-air model.'
                : ''}</p>`;
    }

    fmt(value, digits = 2) {
        if (!Number.isFinite(value)) return '∞';
        return value.toLocaleString('en-US', {
            minimumFractionDigits: digits,
            maximumFractionDigits: digits,
        });
    }
}
