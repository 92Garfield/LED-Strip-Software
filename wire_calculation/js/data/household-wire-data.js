// Common European household installation wires (230 V system, breakers up to 16 A).
// maxCurrent = typical continuous rating for fixed installation (installation method B/C).
export const HOUSEHOLD_WIRE_DATA = [
    { name: '0.75 mm² (light appliance cord)', crossSection: 0.75, maxCurrent: 6 },
    { name: '1.0 mm² (lighting circuit)',      crossSection: 1.0,  maxCurrent: 10 },
    { name: '1.5 mm² (lighting / sockets)',    crossSection: 1.5,  maxCurrent: 16 },
    { name: '2.5 mm² (socket circuits)',       crossSection: 2.5,  maxCurrent: 20 },
    { name: '4.0 mm² (heavy loads)',           crossSection: 4.0,  maxCurrent: 25 },
];
