"""Device handler for Climate Sense v1.0"""
from zigpy.profiles import zha
from zigpy.quirks import CustomCluster, CustomDevice
from zhaquirks import Bus, LocalDataCluster
from zigpy.zcl.clusters.measurement import RelativeHumidity, TemperatureMeasurement

from zigpy.zcl.clusters.general import (
    Basic,
    MultistateInput,
    DeviceTemperature,
    AnalogInput,
    OnOff,
    GreenPowerProxy
)

from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)

CUSTOM_DEVICE_TYPE = 0xFFFE
CUSTOM_MANUFACTURER = "Ilya Rakhlin"
CUSTOM_MODEL = "ClimateSense 1.0"

TEMPERATURE_REPORTED = "temperature_reported"
HUMIDITY_REPORTED = "humidity_reported"
CPU_TEMPERATURE_REPORTED = "cpu_temperature_reported"


class CustomAnalogTempHumidityCluster(CustomCluster, AnalogInput):
    """Analog input cluster, used to relay temperature and humidity to proper clusters"""

    cluster_id = AnalogInput.cluster_id

    def __init__(self, *args, **kwargs):
        """Init."""
        self._current_state = {}
        self._current_value = 0
        super().__init__(*args, **kwargs)

    def _update_attribute(self, attrid, value):
        updated_value = value
        if attrid == 85:
            updated_value
        if attrid == 28:
            if value == "%,45":
                updated_value = "%"
            if value == "C,45":
                updated_value = "C"
        super()._update_attribute(attrid, updated_value)

        if attrid == 85:
            self._current_value = value * 100
        if attrid == 28:
            if value == "%,45":
                h_value = self._current_value
                self.endpoint.device.humidity_bus.listener_event(HUMIDITY_REPORTED, h_value)
            if value == "C,45":
                t_value = self._current_value
                self.endpoint.device.temperature_bus.listener_event(TEMPERATURE_REPORTED, t_value)
            if value == "C":
                cput_value = self._current_value
                self.endpoint.device.cpu_temperature_bus.listener_event(CPU_TEMPERATURE_REPORTED, cput_value)


class HumidityMeasurementCluster(LocalDataCluster, RelativeHumidity):
    """Humidity measurement cluster to receive reports that are sent to the analog cluster."""

    cluster_id = RelativeHumidity.cluster_id
    MEASURED_VALUE_ID = 0x0000

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.endpoint.device.humidity_bus.add_listener(self)

    def humidity_reported(self, value):
        """Humidity reported."""
        self._update_attribute(self.MEASURED_VALUE_ID, value)


class DeviceTemperatureMeasurementCluster(LocalDataCluster, TemperatureMeasurement):

    cluster_id = TemperatureMeasurement.cluster_id
    MEASURED_VALUE_ID = 0x0000

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.endpoint.device.cpu_temperature_bus.add_listener(self)

    def cpu_temperature_reported(self, value):
        """Temperature reported."""
        self._update_attribute(self.MEASURED_VALUE_ID, value)


class TemperatureMeasurementCluster(LocalDataCluster, TemperatureMeasurement):
    """Temperature measurement cluster to receive reports that are sent to the analog cluster."""

    cluster_id = TemperatureMeasurement.cluster_id
    MEASURED_VALUE_ID = 0x0000

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.endpoint.device.temperature_bus.add_listener(self)

    def temperature_reported(self, value):
        """Temperature reported."""
        self._update_attribute(self.MEASURED_VALUE_ID, value)


class ClimateSense1(CustomDevice):
    """Climate Sense v1.0"""

    def __init__(self, *args, **kwargs):
        """Init device."""
        self.temperature_bus = Bus()
        self.humidity_bus = Bus()
        self.cpu_temperature_bus = Bus()
        super().__init__(*args, **kwargs)

    signature = {
        MODELS_INFO: [(CUSTOM_MANUFACTURER, CUSTOM_MODEL)],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: CUSTOM_DEVICE_TYPE,
                INPUT_CLUSTERS: [
                    Basic.cluster_id
                ],
                OUTPUT_CLUSTERS: [
                    Basic.cluster_id,
                    MultistateInput.cluster_id
                ],
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: CUSTOM_DEVICE_TYPE,
                INPUT_CLUSTERS: [AnalogInput.cluster_id],
                OUTPUT_CLUSTERS: [],
            },
            4: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: CUSTOM_DEVICE_TYPE,
                INPUT_CLUSTERS: [AnalogInput.cluster_id],
                OUTPUT_CLUSTERS: [],
            },
            6: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: CUSTOM_DEVICE_TYPE,
                INPUT_CLUSTERS: [OnOff.cluster_id],
                OUTPUT_CLUSTERS: [OnOff.cluster_id],
            },
            242: {
                # <SimpleDescriptor endpoint=242 profile=41440 device_type=102
                # device_version=0
                # input_clusters=[33]
                # output_clusters=[33]
                PROFILE_ID: 41440,
                DEVICE_TYPE: 97,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [GreenPowerProxy.cluster_id],
            }
        }
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: CUSTOM_DEVICE_TYPE,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    TemperatureMeasurementCluster,
                    HumidityMeasurementCluster
                ],
                OUTPUT_CLUSTERS: [
                    Basic.cluster_id,
                    MultistateInput.cluster_id
                ],
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: CUSTOM_DEVICE_TYPE,
                INPUT_CLUSTERS: [
                    CustomAnalogTempHumidityCluster,
                    DeviceTemperatureMeasurementCluster
                ],
                OUTPUT_CLUSTERS: [],
            },
            4: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: CUSTOM_DEVICE_TYPE,
                INPUT_CLUSTERS: [CustomAnalogTempHumidityCluster],
                OUTPUT_CLUSTERS: [],
            },
            6: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: CUSTOM_DEVICE_TYPE,
                INPUT_CLUSTERS: [OnOff.cluster_id],
                OUTPUT_CLUSTERS: [OnOff.cluster_id],
            },
            242: {
                # <SimpleDescriptor endpoint=242 profile=41440 device_type=102
                # device_version=0
                # input_clusters=[33]
                # output_clusters=[33]
                PROFILE_ID: 41440,
                DEVICE_TYPE: 97,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [GreenPowerProxy.cluster_id],
            }
        }
    }
