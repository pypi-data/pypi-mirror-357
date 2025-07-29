from ..sensors.BinaryFOVSensor import BinaryFOVSensor
from ..sensors.BinaryLOSSensor import BinaryLOSSensor
from ..sensors.SensorSet import SensorSet


class SensorFactory:
    @staticmethod
    def create(d):
        sensors = []
        for s in d["sensors"]:
            if s["type"] == 'BinaryLOSSensor':
                sensors.append(BinaryLOSSensor.from_dict(s))
            elif s["type"] == 'BinaryFOVSensor':
                sensors.append(BinaryFOVSensor.from_dict(s))
            else:
                raise Exception(f"Parsing of Sensor {s['type']} not recognized.")

        return SensorSet(sensors, custom_state_decision=d["custom_state_decision"])
