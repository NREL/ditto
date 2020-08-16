# -*- coding: utf-8 -*-
from enum import IntEnum, unique
from dataclasses import dataclass
from typing import List

# TODO: make this a type that understands timestamps
timestamp = str


@dataclass
class ModuleTape:
    gnuplot_path: str
    flush_interval: int
    csv_data_only: int
    csv_keep_clean: int
    delta_mode_needed: timestamp


@unique
class Unit(IntEnum):
    DEFAULT = 0
    ALL = 1
    NONE = 2


@unique
class Output(IntEnum):
    SCREEN = 0
    EPS = 1
    GIF = 2
    JPG = 3
    PDF = 4
    PNG = 5
    SVG = 6


@dataclass
class Recorder:
    property: str
    trigger: str
    file: str
    filetype: str
    mode: str
    multifile: str
    limit: int
    plotcommands: str
    xdata: str
    columns: str
    flush: int
    interval: float  # s
    output: Output
    header_units: Unit
    line_units: Unit


@dataclass
class Collector:
    property: str
    trigger: str
    file: str
    limit: int
    group: str
    flush: int
    interval: float  # s


@unique
class ComplexPart(IntEnum):
    NONE = 0
    REAL = 1
    IMAG = 2
    MAG = 3
    ANG_DEG = 4
    ANG_RAD = 5


@dataclass
class group_recorder:
    file: str
    group: str
    interval: float  # s
    flush_interval: float  # s
    strict: bool
    print_units: bool
    property: str
    limit: int
    complex_part: ComplexPart


@dataclass
class Histogram:
    filename: str
    filetype: str
    mode: str
    group: str
    bins: str
    property: str
    min: float
    max: float
    samplerate: float  # s
    countrate: float  # s
    bin_count: int
    limit: int


@dataclass
class Player:
    property: str
    file: str
    filetype: str
    mode: str
    loop: int


@dataclass
class Shaper:
    file: str
    filetype: str
    mode: str
    group: str
    property: str
    magnitude: float
    events: float


@unique
class ViolationFlag(IntEnum):
    ALLVIOLATIONS = 255
    VIOLATION8 = 128
    VIOLATION7 = 64
    VIOLATION6 = 32
    VIOLATION5 = 16
    VIOLATION4 = 8
    VIOLATION3 = 4
    VIOLATION2 = 2
    VIOLATION1 = 1
    VIOLATION0 = 0


@dataclass
class ViolationRecorder:
    file: str
    summary: str
    virtual_substation: str
    interval: float  # s
    flush_interval: float  # s
    strict: bool
    echo: bool
    limit: int
    violation_delay: int
    xfrmr_thermal_limit_upper: float
    xfrmr_thermal_limit_lower: float
    line_thermal_limit_upper: float
    line_thermal_limit_lower: float
    node_instantaneous_voltage_limit_upper: float
    node_instantaneous_voltage_limit_lower: float
    node_continuous_voltage_limit_upper: float
    node_continuous_voltage_limit_lower: float
    node_continuous_voltage_interval: float
    secondary_dist_voltage_rise_upper_limit: float
    secondary_dist_voltage_rise_lower_limit: float
    substation_breaker_A_limit: float
    substation_breaker_B_limit: float
    substation_breaker_C_limit: float
    substation_pf_lower_limit: float
    inverter_v_chng_per_interval_upper_bound: float
    inverter_v_chng_per_interval_lower_bound: float
    inverter_v_chng_interval: float
    violation_flag: List[ViolationFlag]


@unique
class Status(IntEnum):
    ERROR = 2
    OPEN = 1
    INIT = 0


@dataclass
class CsvReader:
    index: int
    city_name: str
    state_name: str
    lat_deg: float
    lat_min: float
    long_deg: float
    long_min: float
    low_temp: float
    high_temp: float
    peak_solar: float
    elevation: int
    status: Status
    timefmt: str
    timezone: str
    timezone_offset: float
    columns: str
    filename: str


@dataclass
class ModuleClimate:
    pass


@dataclass
class Weather:
    temperature: float  # degF
    humidity: float  # %
    solar_dir: float  # W/sf
    solar_direct: float  # W/sf
    solar_diff: float  # W/sf
    solar_diffuse: float  # W/sf
    solar_global: float  # W/sf
    global_horizontal_extra: float  # W/sf
    wind_speed: float  # mph
    wind_dir: float  # deg
    opq_sky_cov: float  # pu
    rainfall: float  # in/h
    snowdepth: float  # in
    pressure: float  # mbar
    month: int
    day: int
    hour: int
    minute: int
    second: int


@unique
class ImplicitEndUseSource(IntEnum):
    RBSA2014 = 2
    ELCAP2010 = 1
    ELCAP1990 = 0


@unique
class ImplicitEndUse(IntEnum):
    NONE = 0
    DRYER = 33554432
    CLOTHESWASHER = 16777216
    WATERHEATER = 1048576
    EVCHARGER = 524288
    RANGE = 262144
    REFRIGERATOR = 131072
    FREEZER = 65536
    MICROWAVE = 512
    DISHWASHER = 256
    OCCUPANCY = 4
    PLUGS = 2
    LIGHTS = 1


@dataclass
class ModuleResidential:
    default_line_voltage: complex  # [V]
    default_line_current: complex  # [A]
    default_outdoor_temperature: float  # [degF]
    default_humidity: float  # [%]
    default_solar: float  # [Btu/sf]
    default_etp_iterations: int
    ANSI_voltage_check: bool
    implicit_enduse_source: ImplicitEndUseSource
    implicit_enduses: List[ImplicitEndUse]
    house_low_temperature_warning: float  # [degF]
    house_high_temperature_warning: float  # [degF]
    thermostat_control_warning: float
    system_dwell_time: float  # [s]
    aux_cutin_temperature: float  # [degF]


@unique
class ResidentialEnduseConfiguration(IntEnum):
    IS220 = 1
    IS110 = 0


@unique
class ResidentialEnduseOverride(IntEnum):
    OFF = 2
    ON = 1
    NORMAL = 0


@unique
class ResidentialEndusePowerState(IntEnum):
    UNKNOWN = 2
    ON = 1
    OFF = 0


@dataclass
class Loadshape:
    pass


@dataclass
class Enduse:
    pass


@dataclass
class ResidentialEnduse:
    shape: Loadshape
    load: Enduse
    energy: complex  # [kVAh]
    power: complex  # [kVA]
    peak_demand: complex  # [kVA]
    heatgain: float  # [Btu/h]
    cumulative_heatgain: float  # [Btu]
    heatgain_fraction: float  # [pu]
    current_fraction: float  # [pu]
    impedance_fraction: float  # [pu]
    power_fraction: float  # [pu]
    power_factor: float
    configuration: ResidentialEnduseConfiguration
    constant_power: complex  # [kVA]
    constant_current: complex  # [kVA]
    constant_admittance: complex  # [kVA]
    voltage_factor: float  # [pu]
    breaker_amps: float  # [A]
    override: ResidentialEnduseOverride
    power_state: ResidentialEndusePowerState


@dataclass
class Appliance(ResidentialEnduse):
    powers: List[complex]
    impedances: List[complex]
    currents: List[complex]
    durations: List[float]
    transitions: List[float]
    heatgains: List[float]


@unique
class ClotheswasherState(IntEnum):
    SPIN4 = 9
    SPIN3 = 8
    SPIN2 = 7
    SPIN1 = 6
    WASH = 5
    PREWASH = 4
    STOPPED = 0


@unique
class ClotheswasherSpinMode(IntEnum):
    SMALLWASH = 4
    SPIN_WASH = 3
    SPIN_HIGH = 2
    SPIN_MEDIUM = 1
    SPIN_LOW = 0


@unique
class ClotheswasherWashMode(IntEnum):
    GENTLE = 2
    PERM_PRESS = 1
    NORMAL = 0


@dataclass
class Clotheswasher(ResidentialEnduse):
    motor_power: float  # [kW]
    circuit_split: float
    queue: float  # [unit]  # the total laundry accumulated
    demand: float  # [unit/day]  # the amount of laundry accumulating daily
    energy_meter: complex  # [kWh]
    stall_voltage: float  # [V]
    start_voltage: float  # [V]
    clothesWasherPower: float
    stall_impedance: complex  # [Ohm]
    trip_delay: float  # [s]
    reset_delay: float  # [s]
    Is_on: float
    normal_perc: float
    perm_press_perc: float
    NORMAL_PREWASH_POWER: float
    NORMAL_WASH_POWER: float
    NORMAL_SPIN_LOW_POWER: float
    NORMAL_SPIN_MEDIUM_POWER: float
    NORMAL_SPIN_HIGH_POWER: float
    NORMAL_SMALLWASH_POWER: float
    NORMAL_PREWASH_ENERGY: float
    NORMAL_WASH_ENERGY: float
    NORMAL_SPIN_LOW_ENERGY: float
    NORMAL_SPIN_MEDIUM_ENERGY: float
    NORMAL_SPIN_HIGH_ENERGY: float
    NORMAL_SMALLWASH_ENERGY: float
    PERMPRESS_PREWASH_POWER: float
    PERMPRESS_WASH_POWER: float
    PERMPRESS_SPIN_LOW_POWER: float
    PERMPRESS_SPIN_MEDIUM_POWER: float
    PERMPRESS_SPIN_HIGH_POWER: float
    PERMPRESS_SMALLWASH_POWER: float
    PERMPRESS_PREWASH_ENERGY: float
    PERMPRESS_WASH_ENERGY: float
    PERMPRESS_SPIN_LOW_ENERGY: float
    PERMPRESS_SPIN_MEDIUM_ENERGY: float
    PERMPRESS_SPIN_HIGH_ENERGY: float
    PERMPRESS_SMALLWASH_ENERGY: float
    GENTLE_PREWASH_POWER: float
    GENTLE_WASH_POWER: float
    GENTLE_SPIN_LOW_POWER: float
    GENTLE_SPIN_MEDIUM_POWER: float
    GENTLE_SPIN_HIGH_POWER: float
    GENTLE_SMALLWASH_POWER: float
    GENTLE_PREWASH_ENERGY: float
    GENTLE_WASH_ENERGY: float
    GENTLE_SPIN_LOW_ENERGY: float
    GENTLE_SPIN_MEDIUM_ENERGY: float
    GENTLE_SPIN_HIGH_ENERGY: float
    GENTLE_SMALLWASH_ENERGY: float
    queue_min: float  # [unit]
    queue_max: float  # [unit]
    clotheswasher_run_prob: float
    state: ClotheswasherState
    spin_mode: ClotheswasherSpinMode
    wash_mode: ClotheswasherWashMode


@unique
class DishwasherState(IntEnum):
    HEATEDDRY_ONLY = 7
    CONTROL_ONLY = 6
    COIL_ONLY = 3
    MOTOR_COIL_ONLY = 4
    MOTOR_ONLY = 5
    TRIPPED = 2
    STALLED = 1
    STOPPED = 0


@dataclass
class Dishwasher(ResidentialEnduse):
    control_power: float  # [W]
    dishwasher_coil_power_1: float  # [W]
    dishwasher_coil_power_2: float  # [W]
    dishwasher_coil_power_3: float  # [W]
    motor_power: float  # [W]
    circuit_split: float
    queue: float  # [unit]  # number of loads accumulated
    stall_voltage: float  # [V]
    start_voltage: float  # [V]
    stall_impedance: complex  # [Ohm]
    trip_delay: float  # [s]
    reset_delay: float  # [s]
    total_power: float  # [W]
    state: DishwasherState
    energy_baseline: float  # [kWh]
    energy_used: float  # [kWh]
    control_check1: bool
    control_check2: bool
    control_check3: bool
    control_check4: bool
    control_check5: bool
    control_check6: bool
    control_check7: bool
    control_check8: bool
    control_check9: bool
    control_check10: bool
    control_check11: bool
    control_check12: bool
    control_check_temp: bool
    motor_only_check1: bool
    motor_only_check2: bool
    motor_only_check3: bool
    motor_only_check4: bool
    motor_only_check5: bool
    motor_only_check6: bool
    motor_only_check7: bool
    motor_only_check8: bool
    motor_only_check9: bool
    motor_only_temp1: bool
    motor_only_temp2: bool
    motor_coil_only_check1: bool
    motor_coil_only_check2: bool
    heateddry_check1: bool
    heateddry_check2: bool
    coil_only_check1: bool
    coil_only_check2: bool
    coil_only_check3: bool
    Heateddry_option_check: bool
    queue_min: float  # [unit]
    queue_max: float  # [unit]
    pulse_interval_1: float  # [s]
    pulse_interval_2: float  # [s]
    pulse_interval_3: float  # [s]
    pulse_interval_4: float  # [s]
    pulse_interval_5: float  # [s]
    pulse_interval_6: float  # [s]
    pulse_interval_7: float  # [s]
    pulse_interval_8: float  # [s]
    pulse_interval_9: float  # [s]
    pulse_interval_10: float  # [s]
    pulse_interval_11: float  # [s]
    pulse_interval_12: float  # [s]
    pulse_interval_13: float  # [s]
    pulse_interval_14: float  # [s]
    pulse_interval_15: float  # [s]
    pulse_interval_16: float  # [s]
    pulse_interval_17: float  # [s]
    pulse_interval_18: float  # [s]
    pulse_interval_19: float  # [s]
    dishwasher_run_prob: float
    energy_needed: float  # [kWh]
    dishwasher_demand: float  # [kWh]
    daily_dishwasher_demand: float  # [kWh]
    actual_dishwasher_demand: float  # [kWh]
    motor_on_off: float
    motor_coil_on_off: float
    is_240: bool  # load is 220/240 V (across both phases)


@dataclass
class DryerState:
    CONTROL_ONLY = 5
    MOTOR_COIL_ONLY = 3
    MOTOR_ONLY = 4
    TRIPPED = 2
    STALLED = 1
    STOPPED = 0


@dataclass
class Dryer(ResidentialEnduse):
    motor_power: float  # [W]
    dryer_coil_power: float  # [W]
    controls_power: float  # [W]
    circuit_split: float
    queue: float  # [unit]  # number of loads accumulated
    queue_min: float  # [unit]
    queue_max: float  # [unit]
    stall_voltage: float  # [V]
    start_voltage: float  # [V]
    stall_impedance: complex  # [Ohm]
    trip_delay: float  # [s]
    reset_delay: float  # [s]
    total_power: float  # [W]
    state: DryerState
    energy_baseline: float  # [kWh]
    energy_used: float  # [kWh]
    next_t: float
    control_check: bool
    motor_only_check1: bool
    motor_only_check2: bool
    motor_only_check3: bool
    motor_only_check4: bool
    motor_only_check5: bool
    motor_only_check6: bool
    dryer_on: bool
    dryer_ready: bool
    dryer_check: bool
    motor_coil_only_check1: bool
    motor_coil_only_check2: bool
    motor_coil_only_check3: bool
    motor_coil_only_check4: bool
    motor_coil_only_check5: bool
    motor_coil_only_check6: bool
    dryer_run_prob: float
    dryer_turn_on: float
    pulse_interval_1: float  # [s]
    pulse_interval_2: float  # [s]
    pulse_interval_3: float  # [s]
    pulse_interval_4: float  # [s]
    pulse_interval_5: float  # [s]
    pulse_interval_6: float  # [s]
    pulse_interval_7: float  # [s]
    energy_needed: float  # [kWh]
    daily_dryer_demand: float  # [kWh]
    actual_dryer_demand: float  # [kWh]
    motor_on_off: float
    motor_coil_on_off: float
    is_240: bool  # load is 220/240 V (across both phases)


@unique
class EVChargerState(IntEnum):
    WORK = 1
    HOME = 0
    UNKNOWN = 4294967295


@unique
class EVChargerChargerType(IntEnum):
    HIGH = 2
    MEDIUM = 1
    LOW = 0


@unique
class EVChargerVehicleType(IntEnum):
    HYBRID = 1
    ELECTRIC = 0


@dataclass
class EVCharger(ResidentialEnduse):
    charger_type: EVChargerChargerType
    vehicle_type: EVChargerVehicleType
    state: EVChargerState
    p_go_home: float  # [unit/h]
    p_go_work: float  # [unit/h]
    work_dist: float  # [mile]
    capacity: float  # [kWh]
    charge: float  # [unit]
    charge_at_work: bool
    charge_throttle: float  # [unit]
    charger_efficiency: float  # [unit]  # Efficiency of the charger in terms of energy in to battery stored
    power_train_efficiency: float  # [mile/kWh]  # Miles per kWh of battery charge
    mileage_classification: float  # [mile]  # Miles expected range on battery only
    demand_profile: str


@unique
class EVChargerDeterministicVehicleLocation(IntEnum):
    DRIVING_WORK = 4
    DRIVING_HOME = 3
    WORK = 2
    HOME = 1
    UNKNOWN = 0


@dataclass
class EVChargerDeterministic(ResidentialEnduse):
    charge_rate: float  # [W]  # Current demanded charge rate of the vehicle
    variation_mean: float  # [s]  # Mean of normal variation of schedule variation
    variation_std_dev: float  # [s]  # Standard deviation of normal variation of schedule times
    variation_trip_mean: float  # [mile]  # Mean of normal variation of trip distance variation
    variation_trip_std_dev: float  # [mile]  # Standard deviation of normal variation of trip distance
    mileage_classification: float  # [mile]  # Mileage classification of electric vehicle
    work_charging_available: bool  # Charging available when at work
    data_file: str  # Path to .CSV file with vehicle travel information
    vehicle_index: int  # Index of vehicles in file this particular vehicle's data
    vehicle_location: EVChargerDeterministicVehicleLocation
    travel_distance: float  # [mile]  # Distance vehicle travels from home to home
    arrival_at_work: float  # Time vehicle arrives at work - HHMM
    duration_at_work: float  # [s]  # Duration the vehicle remains at work
    arrival_at_home: float  # Time vehicle arrives at home - HHMM
    duration_at_home: float  # [s]  # Duration the vehicle remains at home
    battery_capacity: float  # [kWh]  # Current capacity of the battery in kWh
    battery_SOC: float  # [%]  # State of charge of battery
    battery_size: float  # [kWh]  # Full capacity of battery
    mileage_efficiency: float  # [mile/kWh]  # Efficiency of drive train in mile/kWh
    maximum_charge_rate: float  # [W]  # Maximum output rate of charger in kW
    charging_efficiency: float  # [unit]  # Efficiency of charger (ratio) when charging


@unique
class FreezerState(IntEnum):
    ON = 1
    OFF = 0


@dataclass
class Freezer(ResidentialEnduse):
    size: float  # [cf]
    rated_capacity: float  # [Btu/h]
    temperature: float  # [degF]
    setpoint: float  # [degF]
    deadband: float  # [degF]
    next_time: timestamp
    output: float
    event_temp: float
    UA: float  # [Btu/degF*h]
    state: FreezerState


@unique
class HouseIncludeSolarQuadrant(IntEnum):
    W = 16
    S = 8
    E = 4
    N = 2
    H = 1
    NONE = 0


@unique
class HouseHeatingCOPCurve(IntEnum):
    CURVED = 3
    LINEAR = 2
    FLAT = 1
    DEFAULT = 0


@unique
class HouseHeatingCAPCurve(IntEnum):
    CURVED = 3
    LINEAR = 2
    FLAT = 1
    DEFAULT = 0


@unique
class HouseCoolingCOPCurve(IntEnum):
    CURVED = 3
    LINEAR = 2
    FLAT = 1
    DEFAULT = 0


@unique
class HouseCoolingCAPCurve(IntEnum):
    CURVED = 3
    LINEAR = 2
    FLAT = 1
    DEFAULT = 0


@unique
class HouseThermostatMode(IntEnum):
    COOL = 3
    HEAT = 2
    AUTO = 1
    OFF = 0


@unique
class HouseSystemType(IntEnum):
    RESISTIVE = 16
    TWOSTAGE = 8
    FORCEDAIR = 4
    AIRCONDITIONING = 2
    GAS = 1
    NONE = 0


@unique
class HouseAuxilaryStrategy(IntEnum):
    LOCKOUT = 4
    TIMER = 2
    DEADBAND = 1
    NONE = 0


@unique
class HouseSystemMode(IntEnum):
    AUX = 3
    COOL = 4
    OFF = 1
    HEAT = 2
    UNKNOWN = 0


@unique
class HouseHeatingSystemType(IntEnum):
    RESISTANCE = 4
    HEAT_PUMP = 3
    GAS = 2
    NONE = 1


@unique
class HouseCoolingSystemType(IntEnum):
    HEAT_PUMP = 2
    ELECTRIC = 2
    NONE = 1


@unique
class HouseAuxiliarySystemType(IntEnum):
    ELECTRIC = 2
    NONE = 1


@unique
class HouseFanType(IntEnum):
    TWO_SPEED = 3
    ONE_SPEED = 2
    NONE = 1


@unique
class HouseThermalIntegrityLevel(IntEnum):
    UNKNOWN = 7
    VERY_GOOD = 6
    GOOD = 5
    ABOVE_NORMAL = 4
    NORMAL = 3
    BELOW_NORMAL = 2
    LITTLE = 1
    VERY_LITTLE = 0


@unique
class HouseGlassType(IntEnum):
    LOW_E_GLASS = 2
    GLASS = 1
    OTHER = 0


@unique
class HouseWindowFrame(IntEnum):
    INSULATED = 4
    WOOD = 3
    THERMAL_BREAK = 2
    ALUMINIUM = 1
    ALUMINUM = 1
    NONE = 0


@unique
class HouseGlazingTreatment(IntEnum):
    HIGH_S = 5
    LOW_S = 4
    REFL = 3
    ABS = 2
    CLEAR = 1
    OTHER = 0


@unique
class HouseGlazingLayers(IntEnum):
    OTHER = 4
    THREE = 3
    TWO = 2
    ONE = 1


@unique
class HouseMotorModel(IntEnum):
    FULL = 2
    BASIC = 1
    NONE = 0


@unique
class HouseMotorEfficiency(IntEnum):
    VERY_GOOD = 4
    GOOD = 3
    AVERAGE = 2
    POOR = 1
    VERY_POOR = 0


@unique
class HousePanelConfiguration(IntEnum):
    IS220 = 1
    IS110 = 0


@unique
class HouseThermostatControl(IntEnum):
    NONE = 2
    BAND = 1
    FULL = 0


@dataclass
class HousePanel:
    pass


@dataclass
class House(ResidentialEnduse):
    weather: object  # reference to the climate object
    floor_area: float  # [sf]  # home conditioned floor area
    gross_wall_area: float  # [sf]  # gross outdoor wall area
    ceiling_height: float  # [ft]  # average ceiling height
    aspect_ratio: float  # aspect ratio of the home's footprint
    envelope_UA: float  # [Btu/degF*h]  # overall UA of the home's envelope
    window_wall_ratio: float  # ratio of window area to wall area
    number_of_doors: float  # ratio of door area to wall area
    exterior_wall_fraction: float  # ratio of exterior wall area to total wall area
    interior_exterior_wall_ratio: float  # ratio of interior to exterior walls
    exterior_ceiling_fraction: float  # ratio of external ceiling sf to floor area
    exterior_floor_fraction: float  # ratio of floor area used in UA calculation
    window_shading: float  # transmission coefficient through window due to glazing
    window_exterior_transmission_coefficient: float  # coefficient for the amount of energy that passes through window
    solar_heatgain_factor: float  # product of the window area, window transmitivity, and the window exterior transmission coefficient
    airchange_per_hour: float  # [unit/h]  # number of air-changes per hour
    airchange_UA: float  # [Btu/degF*h]  # additional UA due to air infiltration
    UA: float  # [Btu/degF*h]  # the total UA
    internal_gain: float  # [Btu/h]  # internal heat gains
    solar_gain: float  # [Btu/h]  # solar heat gains
    incident_solar_radiation: float  # [Btu/h*sf]  # average incident solar radiation hitting the house
    heat_cool_gain: float  # [Btu/h]  # system heat gains(losses)
    include_solar_quadrant: HouseIncludeSolarQuadrant  # bit set for determining which solar incidence quadrants should be included in the solar heatgain
    horizontal_diffuse_solar_radiation: float  # [Btu/h*sf]  # incident solar radiation hitting the top of the house
    north_incident_solar_radiation: float  # [Btu/h*sf]  # incident solar radiation hitting the north side of the house
    northwest_incident_solar_radiation: float  # [Btu/h*sf]  # incident solar radiation hitting the northwest side of the house
    west_incident_solar_radiation: float  # [Btu/h*sf]  # incident solar radiation hitting the west side of the house
    southwest_incident_solar_radiation: float  # [Btu/h*sf]  # incident solar radiation hitting the southwest side of the house
    south_incident_solar_radiation: float  # [Btu/h*sf]  # incident solar radiation hitting the south side of the house
    southeast_incident_solar_radiation: float  # [Btu/h*sf]  # incident solar radiation hitting the southeast side of the house
    east_incident_solar_radiation: float  # [Btu/h*sf]  # incident solar radiation hitting the east side of the house
    northeast_incident_solar_radiation: float  # [Btu/h*sf]  # incident solar radiation hitting the northeast side of the house
    heating_cop_curve: HouseHeatingCOPCurve  # Defines the function type to use for the adjusted heating COP as a function of outside air temperature.
    heating_cap_curve: HouseHeatingCAPCurve  # Defines the function type to use for the adjusted heating capacity as a function of outside air temperature.
    cooling_cop_curve: HouseCoolingCAPCurve  # Defines the function type to use for the adjusted cooling COP as a function of outside air temperature.
    cooling_cap_curve: HouseCoolingCAPCurve  # Defines the function type to use for the adjusted cooling capacity as a function of outside air temperature.
    use_latent_heat: bool  # Boolean for using the heat latency of the air to the humidity when cooling.
    include_fan_heatgain: bool  # Boolean to choose whether to include the heat generated by the fan in the ETP model.
    thermostat_deadband: float  # [degF]  # deadband of thermostat control
    dlc_offset: float  # [degF]  # used as a cap to offset the thermostat deadband for direct load control applications
    thermostat_cycle_time: int  # minimum time in seconds between thermostat updates
    thermostat_off_cycle_time: int  # the minimum amount of time the thermostat cycle must stay in the off state
    thermostat_on_cycle_time: int  # the minimum amount of time the thermostat cycle must stay in the on state
    thermostat_last_cycle_time: timestamp  # last time the thermostat changed state
    heating_setpoint: float  # [degF]  # thermostat heating setpoint
    cooling_setpoint: float  # [degF]  # thermostat cooling setpoint
    design_heating_setpoint: float  # [degF]  # system design heating setpoint
    design_cooling_setpoint: float  # [degF]  # system design cooling setpoint
    over_sizing_factor: float  # over sizes the heating and cooling system from standard specifications (0.2 ='s 120% sizing)
    simulate_window_openings: bool  # activates a representation of an occupant opening a window and de-activating the HVAC system
    is_window_open: float  # defines the state of the window opening, 1=open, 2=closed
    window_low_temperature_cutoff: float  # [degF]  # lowest temperature at which the window opening might occur
    window_high_temperature_cutoff: float  # [degF]  # highest temperature at which the window opening might occur
    window_quadratic_coefficient: float  # quadratic coefficient for describing function between low and high temperature cutoffs
    window_linear_coefficient: float  # linear coefficient for describing function between low and high temperature cutoffs
    window_constant_coefficient: float  # constant coefficient for describing function between low and high temperature cutoffs
    window_temperature_delta: float  # change in outdoor temperature required to update the window opening model
    design_heating_capacity: float  # [Btu/h]  # system heating capacity
    design_cooling_capacity: float  # [Btu/h]  # system cooling capacity
    cooling_design_temperature: float  # [degF]  # system cooling design temperature
    heating_design_temperature: float  # [degF]  # system heating design temperature
    design_peak_solar: float  # [Btu/h*sf]  # system design solar load
    design_internal_gains: float  # [W/sf]  # system design internal gains
    air_heat_fraction: float  # [pu]  # fraction of heat gain/loss that goes to air (as opposed to mass)
    mass_solar_gain_fraction: float  # [pu]  # fraction of the heat gain/loss from the solar gains that goes to the mass
    mass_internal_gain_fraction: float  # [pu]  # fraction of heat gain/loss from the internal gains that goes to the mass
    auxiliary_heat_capacity: float  # [Btu/h]  # installed auxiliary heating capacity
    aux_heat_deadband: float  # [degF]  # temperature offset from standard heat activation to auxiliary heat activation
    aux_heat_temperature_lockout: float  # [degF]  # temperature at which auxiliary heat will not engage above
    aux_heat_time_delay: float  # [s]  # time required for heater to run until auxiliary heating engages
    cooling_supply_air_temp: float  # [degF]  # temperature of air blown out of the cooling system
    heating_supply_air_temp: float  # [degF]  # temperature of air blown out of the heating system
    duct_pressure_drop: float  # [inH2O]  # end-to-end pressure drop for the ventilation ducts, in inches of water
    fan_design_power: float  # [W]  # designed maximum power draw of the ventilation fan
    fan_low_power_fraction: float  # [pu]  # fraction of ventilation fan power draw during low-power mode (two-speed only)
    fan_power: float  # [kW]  # current ventilation fan power draw
    fan_design_airflow: float  # [cfm]  # designed airflow for the ventilation system
    fan_impedance_fraction: float  # [pu]  # Impedance component of fan ZIP load
    fan_power_fraction: float  # [pu]  # Power component of fan ZIP load
    fan_current_fraction: float  # [pu]  # Current component of fan ZIP load
    fan_power_factor: float  # [pu]  # Power factor of the fan load
    heating_demand: float  # [kW]  # the current power draw to run the heating system
    cooling_demand: float  # [kW]  # the current power draw to run the cooling system
    heating_COP: float  # [pu]  # system heating performance coefficient
    cooling_COP: float  # [Btu/kWh]  # system cooling performance coefficient
    air_temperature: float  # [degF]  # indoor air temperature
    outdoor_temperature: float  # [degF]  # outdoor air temperature
    outdoor_rh: float  # [%]  # outdoor relative humidity
    mass_heat_capacity: float  # [Btu/degF]  # interior mass heat capacity
    mass_heat_coeff: float  # [Btu/degF*h]  # interior mass heat exchange coefficient
    mass_temperature: float  # [degF]  # interior mass temperature
    air_volume: float  # [cf]  # air volume
    air_mass: float  # [lb]  # air mass
    air_heat_capacity: float  # [Btu/degF]  # air thermal mass
    latent_load_fraction: float  # [pu]  # fractional increase in cooling load due to latent heat
    total_thermal_mass_per_floor_area: float  # [Btu/degF*sf]
    interior_surface_heat_transfer_coeff: float  # [Btu/h*degF*sf]
    number_of_stories: float  # number of stories within the structure
    is_AUX_on: float  # logic statement to determine population statistics - is the AUX on? 0 no, 1 yes
    is_HEAT_on: float  # logic statement to determine population statistics - is the HEAT on? 0 no, 1 yes
    is_COOL_on: float  # logic statement to determine population statistics - is the COOL on? 0 no, 1 yes
    thermal_storage_present: float  # logic statement for determining if energy storage is present
    thermal_storage_in_use: float  # logic statement for determining if energy storage is being utilized
    thermostat_mode: HouseThermostatMode  # tells the thermostat whether it is even allowed to heat or cool the house.
    system_type: HouseSystemType  # heating/cooling system type/options
    auxiliary_strategy: HouseAuxilaryStrategy  # auxiliary heating activation strategies
    system_mode: HouseSystemMode  # heating/cooling system operation state
    last_system_mode: HouseSystemMode  # heating/cooling system operation state
    heating_system_type: HouseHeatingSystemType
    cooling_system_type: HouseCoolingSystemType
    auxiliary_system_type: HouseAuxilaryStrategy
    fan_type: HouseFanType
    thermal_integrity_level: HouseThermalIntegrityLevel  # default envelope UA settings
    glass_type: HouseGlassType  # glass used in the windows
    window_frame: HouseWindowFrame  # type of window frame
    glazing_treatment: HouseGlazingTreatment  # the treatment to increase the reflectivity of the exterior windows
    glazing_layers: HouseGlazingLayers  # number of layers of glass in each window
    motor_model: HouseMotorModel  # indicates the level of detail used in modelling the hvac motor parameters
    motor_efficiency: HouseMotorEfficiency  # when using motor model, describes the efficiency of the motor
    last_mode_timer: int
    hvac_motor_efficiency: float  # [unit]  # when using motor model, percent efficiency of hvac motor
    hvac_motor_loss_power_factor: float  # [unit]  # when using motor model, power factor of motor losses
    Rroof: float  # [degF*sf*h/Btu]  # roof R-value
    Rwall: float  # [degF*sf*h/Btu]  # wall R-value
    Rfloor: float  # [degF*sf*h/Btu]  # floor R-value
    Rwindows: float  # [degF*sf*h/Btu]  # window R-value
    Rdoors: float  # [degF*sf*h/Btu]  # door R-value
    hvac_breaker_rating: float  # [A]  # determines the amount of current the HVAC circuit breaker can handle
    hvac_power_factor: float  # [unit]  # power factor of hvac
    hvac_load: float  # [kW]  # heating/cooling system load
    last_heating_load: float  # [kW]  # stores the previous heating/cooling system load
    last_cooling_load: float  # [kW]  # stores the previous heating/cooling system load
    hvac_power: complex  # [kVA]  # describes hvac load complex power consumption
    total_load: float  # [kW]  # total panel enduse load
    enduse: HousePanel  # the enduse load description
    panel_energy: complex  # [kVAh]  # the total energy consumed since the last meter reading
    panel_power: complex  # [kVA]  # the total power consumption of the load
    panel_peak_demand: complex  # [kVA]  # the peak power consumption since the last meter reading
    panel_heatgain: float  # [Btu/h]  # the heat transferred from the enduse to the parent
    panel_cumulative_heatgain: float  # [Btu]  # the cumulative heatgain from the enduse to the parent
    panel_heatgain_fraction: float  # [pu]  # the fraction of the heat that goes to the parent
    panel_current_fraction: float  # [pu]  # the fraction of total power that is constant current
    panel_impedance_fraction: float  # [pu]  # the fraction of total power that is constant impedance
    panel_power_fraction: float  # [pu]  # the fraction of the total power that is constant power
    panel_power_factor: float  # the power factor of the load
    panel_constant_power: complex  # [kVA]  # the constant power portion of the total load
    panel_constant_current: complex  # [kVA]  # the constant current portion of the total load
    panel_constant_admittance: complex  # [kVA]  # the constant admittance portion of the total load
    panel_voltage_factor: float  # [pu]  # the voltage change factor
    panel_breaker_amps: float  # [A]  # the rated breaker amperage
    panel_configuration: HousePanelConfiguration  # the load configuration options
    design_internal_gain_density: float  # [W/sf]  # average density of heat generating devices in the house
    compressor_on: bool
    compressor_count: int
    hvac_last_on: timestamp
    hvac_last_off: timestamp
    hvac_period_length: float  # [s]
    hvac_duty_cycle: float
    thermostat_control: HouseThermostatControl  # determine level of internal thermostatic control


@unique
class MicrowaveState(IntEnum):
    ON = 1
    OFF = 0


@dataclass
class Microwave(ResidentialEnduse):
    installed_power: float  # [kW]  # rated microwave power level
    standby_power: float  # [kW]  # standby microwave power draw (unshaped only)
    circuit_split: float
    state: MicrowaveState  # on/off state of the microwave
    cycle_length: float  # [s]  # length of the combined on/off cycle between uses
    runtime: float  # [s]  #
    state_time: float  # [s]  #


@dataclass
class OccupantLoad(ResidentialEnduse):
    number_of_occupants: int
    occupancy_fraction: float  # [unit]
    heatgain_per_person: float  # [Btu/h]


@dataclass
class PlugLoad(ResidentialEnduse):
    circuit_split: float
    demand: float  # [unit]
    installed_power: float  # [kW]  # installed plugs capacity
    actual_power: complex  # [kVA]  # actual power demand


@unique
class RangeHeatMode(IntEnum):
    GASHEAT = 1
    ELECTRIC = 0


@unique
class RangeLocation(IntEnum):
    GARAGE = 1
    INSIDE = 0


@unique
class RangeStateCooktop(IntEnum):
    CT_TRIPPED = 6
    CT_STALLED = 5
    STAGE_8_ONLY = 4
    STAGE_7_ONLY = 3
    STAGE_6_ONLY = 2
    CT_STOPPED = 1


@dataclass
class Range(ResidentialEnduse):
    oven_volume: float  # [gal]  # the volume of the oven
    oven_UA: float  # [Btu/degF*h]  # the UA of the oven (surface area divided by R-value)
    oven_diameter: float  # [ft]  # the diameter of the oven
    oven_demand: float  # [gpm]  # the hot food take out from the oven
    heating_element_capacity: float  # [kW]  # the power of the heating element
    inlet_food_temperature: float  # [degF]  # the inlet temperature of the food
    heat_mode: RangeHeatMode  # the energy source for heating the oven
    location: RangeLocation  # whether the range is inside or outside
    oven_setpoint: float  # [degF]  # the temperature around which the oven will heat its contents
    thermostat_deadband: float  # [degF]  # the degree to heat the food in the oven, when needed
    temperature: float  # [degF]  # the outlet temperature of the oven
    height: float  # [ft]  # the height of the oven
    food_density: float  # food density
    specificheat_food: float
    queue_cooktop: float  # [unit]  # number of loads accumulated
    queue_oven: float  # [unit]  # number of loads accumulated
    queue_min: float  # [unit]
    queue_max: float  # [unit]
    time_cooktop_operation: float
    time_cooktop_setting: float
    cooktop_run_prob: float
    oven_run_prob: float
    cooktop_coil_setting_1: float  # [kW]
    cooktop_coil_setting_2: float  # [kW]
    cooktop_coil_setting_3: float  # [kW]
    total_power_oven: float  # [kW]
    total_power_cooktop: float  # [kW]
    total_power_range: float  # [kW]
    demand_cooktop: float  # [unit/day]  # number of loads accumulating daily
    demand_oven: float  # [unit/day]  # number of loads accumulating daily
    stall_voltage: float  # [V]
    start_voltage: float  # [V]
    stall_impedance: complex  # [Ohm]
    trip_delay: float  # [s]
    reset_delay: float  # [s]
    time_oven_operation: float  # [s]
    time_oven_setting: float  # [s]
    state_cooktop: RangeStateCooktop
    cooktop_energy_baseline: float  # [kWh]
    cooktop_energy_used: float
    Toff: float
    Ton: float
    cooktop_interval_setting_1: float  # [s]
    cooktop_interval_setting_2: float  # [s]
    cooktop_interval_setting_3: float  # [s]
    cooktop_energy_needed: float  # [kWh]
    heat_needed: bool
    oven_check: bool
    remainon: bool
    cooktop_check: bool
    actual_load: float  # [kW]  # the actual load based on the current voltage across the coils
    previous_load: float  # [kW]  # the actual load based on current voltage stored for use in controllers
    actual_power: complex  # [kVA]  # the actual power based on the current voltage across the coils
    is_range_on: float  # simple logic output to determine state of range (1-on, 0-off)


@unique
class RefrigeratorDefrostCriterion(IntEnum):
    COMPRESSOR_TIME = 3
    DOOR_OPENINGS = 2
    TIMED = 1


@unique
class RefrigeratorState(IntEnum):
    COMPRESSSOR_ON_NORMAL = 3
    COMPRESSSOR_ON_LONG = 4
    COMPRESSSOR_OFF_NORMAL = 2
    DEFROST = 1


@dataclass
class Refrigerator(ResidentialEnduse):
    size: float  # [cf]  # volume of the refrigerator
    rated_capacity: float  # [Btu/h]
    temperature: float  # [degF]
    setpoint: float  # [degF]
    deadband: float  # [degF]
    cycle_time: float  # [s]
    output: float
    event_temp: float
    UA: float  # [Btu/degF*h]
    compressor_off_normal_energy: float
    compressor_off_normal_power: float  # [W]
    compressor_on_normal_energy: float
    compressor_on_normal_power: float  # [W]
    defrost_energy: float
    defrost_power: float  # [W]
    icemaking_energy: float
    icemaking_power: float  # [W]
    ice_making_probability: float
    FF_Door_Openings: int
    door_opening_energy: int
    door_opening_power: int
    DO_Thershold: float
    dr_mode_double: float
    energy_needed: float
    energy_used: float
    refrigerator_power: float
    icemaker_running: bool
    check_DO: int
    is_240: bool
    defrostDelayed: float
    long_compressor_cycle_due: bool
    long_compressor_cycle_time: float
    long_compressor_cycle_power: float
    long_compressor_cycle_energy: float
    long_compressor_cycle_threshold: float
    defrost_criterion: RefrigeratorDefrostCriterion
    run_defrost: bool
    door_opening_criterion: float
    compressor_defrost_time: float
    delay_defrost_time: float
    daily_door_opening: int
    state: RefrigeratorState


@unique
class ThermalStorageDischargeScheduleType(IntEnum):
    EXTERNAL = 1
    INTERNAL = 0


@unique
class ThermalStorageRechargeScheduleType(IntEnum):
    EXTERNAL = 1
    INTERNAL = 0


@dataclass
class ThermalStorage(ResidentialEnduse):
    total_capacity: float  # [Btu]  # total storage capacity of unit
    stored_capacity: float  # [Btu]  # amount of capacity that is stored
    recharge_power: float  # [kW]  # installed compressor power usage
    discharge_power: float  # [kW]  # installed pump power usage
    recharge_pf: float  # installed compressor power factor
    discharge_pf: float  # installed pump power factor
    discharge_schedule_type: ThermalStorageDischargeScheduleType  # Scheduling method for discharging
    recharge_schedule_type: ThermalStorageRechargeScheduleType  # Scheduling method for charging
    recharge_time: float  # Flag indicating if recharging is available at the current time (1 or 0)
    discharge_time: float  # Flag indicating if discharging is available at the current time (1 or 0)
    discharge_rate: float  # [Btu/h]  # rating of discharge or cooling
    SOC: float  # [%] state of charge as percentage of total capacity
    k: float  # [W/m/K]  # coefficient of thermal conductivity (W/m/K)


@unique
class WaterHeaterWaterHeaterModel(IntEnum):
    NONE = 3
    FORTRAN = 2
    TWONODE = 1
    ONEZNODE = 0


@unique
class WaterHeaterHeatMode(IntEnum):
    HEAT_PUMP = 2
    GASHEAT = 1
    ELECTRIC = 0


@unique
class WaterHeaterLocation(IntEnum):
    GARAGE = 1
    INSIDE = 0


@unique
class WaterHeaterCurrentTankStatus(IntEnum):
    EMPTY = 2
    PARTIAL = 1
    FULL = 0


@unique
class WaterHeaterLoadState(IntEnum):
    STABLE = 2
    RECOVERING = 1
    DEPLETING = 0


@unique
class WaterHeaterREOverride(IntEnum):
    OV_OFF = 2
    OV_NORMAL = 0
    OV_ON = 1


@dataclass
class WaterHeater(ResidentialEnduse):
    tank_volume: float  # [gal]  # the volume of water in the tank when it is full
    tank_UA: float  # [Btu*h/degF]  # the UA of the tank (surface area divided by R-value)
    tank_diameter: float  # [ft]  # the diameter of the water heater tank
    tank_height: float  # [ft]  # the height of the water heater tank
    water_demand: float  # [gpm]  # the hot water draw from the water heater
    heating_element_capacity: float  # [kW]  # the power of the heating element
    inlet_water_temperature: float  # [degF]  # the inlet temperature of the water tank
    waterheater_model: WaterHeaterWaterHeaterModel  # the water heater model to use
    heat_mode: WaterHeaterHeatMode  # the energy source for heating the water heater
    location: WaterHeaterLocation  # whether the water heater is inside or outside
    tank_setpoint: float  # [degF]  # the temperature around which the water heater will heat its contents
    thermostat_deadband: float  # [degF]  # the degree to heat the water tank, when needed
    temperature: float  # [degF]  # the outlet temperature of the water tank
    height: float  # [ft]  # the height of the hot water column within the water tank
    demand: complex  # [kVA]  # the water heater power consumption
    actual_load: float  # [kW]  # the actual load based on the current voltage across the coils
    previous_load: float  # [kW]  # the actual load based on current voltage stored for use in controllers
    actual_power: complex  # [kVA]  # the actual power based on the current voltage across the coils
    is_waterheater_on: float  # simple logic output to determine state of waterheater (1-on, 0-off)
    gas_fan_power: float  # [kW]  # load of a running gas waterheater
    gas_standby_power: float  # [kW]  # load of a gas waterheater in standby
    heat_pump_coefficient_of_performance: float  # [Btu/kWh]  # current COP of the water heater pump - currently calculated internally and not an input
    Tcontrol: float  # [degF]  # in heat pump operation, defines the blended temperature used for turning on and off HP - currently calculated internally and not an input
    current_tank_status: WaterHeaterCurrentTankStatus
    dr_signal: float  # the on/off signal to send to the fortran waterheater model
    COP: float  # the cop of the fortran heat pump water heater model.
    operating_mode: float  # the operating mode the fortran water heater should be using.
    fortran_sim_time: float  # [s]  # the amount of time the fortran model should simulate.
    waterheater_power: float  # [kW]  # the current power draw from the fortran water heater.
    load_state: WaterHeaterLoadState
    re_override: WaterHeaterREOverride  # the override setting for the water heater


@dataclass
class ZIPLoad(ResidentialEnduse):
    pass


@unique
class ModulePowerFlowSolverMethod(IntEnum):
    NR = 2
    GS = 1
    FBS = 0


@unique
class ModulePowerFlowNRMatrixOutputInterval(IntEnum):
    ALL = 3
    PER_CALL = 2
    ONCE = 1
    NEVER = 0


@dataclass
class ModulePowerFlow:
    show_matrix_values: bool
    primary_voltage_ratio: float
    nominal_frequency: float
    require_voltage_control: bool
    geographic_degree: float
    fault_impedance: complex
    ground_impedance: complex
    warning_underfrequency: float
    warning_overfrequency: float
    warning_undervoltage: float
    warning_overvoltage: float
    warning_voltageangle: float
    maximum_voltage_error: float
    solver_method: ModulePowerFlowSolverMethod
    NR_matrix_file: str
    NR_matrix_output_interval: ModulePowerFlowNRMatrixOutputInterval
    NR_matrix_output_references: bool
    line_capacitance: bool
    line_limits: bool
    lu_solver: str
    NR_iteration_limit: int
    NR_deltamode_iteration_limit: int
    NR_superLU_procs: int
    default_maximum_voltage_error: float
    default_maximum_power_error: float
    NR_admit_change: bool
    enable_subsecond_models: bool  # Enable deltamode capabilities within the powerflow module
    all_powerflow_delta: bool  # Forces all powerflow objects that are capable to participate in deltamode
    deltamode_timestep: float  # [ns]  # Desired minimum timestep for deltamode-related simulations
    deltamode_extra_function: int
    current_frequency: float  # [Hz]  # Current system-level frequency of the powerflow system
    master_frequency_update: bool  # Tracking variable to see if an object has become the system frequency updater
    enable_frequency_dependence: bool  # Flag to enable frequency-based variations in impedance values of lines and loads
    default_resistance: float
    enable_inrush: bool  # Flag to enable in-rush calculations for lines and transformers in deltamode
    low_voltage_impedance_level: float  # Lower limit of voltage (in per-unit) at which all load types are converted to impedance for in-rush calculations
    enable_mesh_fault_current: bool  # Flag to enable mesh-based fault current calculations
    market_price_name: str


@unique
class BillDumpMeterType(IntEnum):
    METER = 1
    TRIPLEX_METER = 0


class BillDump(IntEnum):
    group: str  # the group ID to output data for (all nodes if empty)
    runtime: timestamp  # the time to check voltage data
    filename: str  # the file to dump the voltage data into
    runcount: int  # the number of times the file has been written to
    meter_type: BillDumpMeterType  # describes whether to collect from 3-phase or S-phase meters


@unique
class PowerFlowObjectPhases(IntEnum):
    A = 1
    B = 2
    C = 4
    D = 256
    N = 8
    S = 112
    G = 128


@dataclass
class PowerFlowObject:
    phases: List[PowerFlowObjectPhases]
    nominal_voltage: float  # [V]


@unique
class NodeBusType(IntEnum):
    SWING_PQ = 3
    SWING = 2
    PV = 1
    PQ = 0


@unique
class NodeBusFlag(IntEnum):
    ISSOURCE = 2
    HASSOURCE = 1


@unique
class NodeFrequencyMeasureType(IntEnum):
    PLL = 3
    SIMPLE = 2
    NONE = 1


@unique
class NodeServiceStatus(IntEnum):
    OUT_OF_SERVICE = 0
    IN_SERVICE = 1


class Node(PowerFlowObject):
    bustype: NodeBusType  # defines whether the node is a PQ, PV, or SWING node
    busflags: List[NodeBusFlag]  # flag indicates node has a source for voltage, i.e. connects to the swing node
    reference_bus: object  # reference bus from which frequency is defined
    maximum_voltage_error: float  # [V]  # convergence voltage limit or convergence criteria
    voltage_A: complex  # [V]  # bus voltage, Phase A to ground
    voltage_B: complex  # [V]  # bus voltage, Phase B to ground
    voltage_C: complex  # [V]  # bus voltage, Phase C to ground
    voltage_AB: complex  # [V]  # line voltages, Phase AB
    voltage_BC: complex  # [V]  # line voltages, Phase BC
    voltage_CA: complex  # [V]  # line voltages, Phase CA
    mean_repair_time: float  # [s]  # Time after a fault clears for the object to be back in service
    frequency_measure_type: NodeFrequencyMeasureType  # PLL frequency measurement
    sfm_T: float  # [s]  # Transducer time constant for simplified frequency measurement (seconds)
    pll_Kp: float  # [pu]  # Proportional gain of PLL frequency measurement
    pll_Ki: float  # [pu]  # Integration gain of PLL frequency measurement
    measured_angle_A: float  # [rad]  # bus angle measurement, phase A
    measured_frequency_A: float  # [Hz]  # frequency measurement, phase A
    measured_angle_B: float  # [rad]  # bus angle measurement, phase B
    measured_frequency_B: float  # [Hz]  # frequency measurement, phase B
    measured_angle_C: float  # [rad]  # bus angle measurement, phase C
    measured_frequency_C: float  # [Hz]  # frequency measurement, phase C
    measured_frequency: float  # [Hz]  # frequency measurement - average of present phases
    service_status: NodeServiceStatus  # In and out of service flag
    service_status_double: float  # In and out of service flag - type float - will indiscriminately override service_status - useful for schedules
    previous_uptime: float  # [min]  # Previous time between disconnects of node in minutes
    current_uptime: float  # [min]  # Current time since last disconnect of node in minutes
    Norton_dynamic: bool  # Flag to indicate a Norton-equivalent connection -- used for generators and deltamode
    GFA_enable: bool  # Disable/Enable Grid Friendly Applicance(TM)-type functionality
    GFA_freq_low_trip: float  # [Hz]  # Low frequency trip point for Grid Friendly Appliance(TM)-type functionality
    GFA_freq_high_trip: float  # [Hz]  # High frequency trip point for Grid Friendly Appliance(TM)-type functionality
    GFA_volt_low_trip: float  # [pu]  # Low voltage trip point for Grid Friendly Appliance(TM)-type functionality
    GFA_volt_high_trip: float  # [pu]  # High voltage trip point for Grid Friendly Appliance(TM)-type functionality
    GFA_reconnect_time: float  # [s]  # Reconnect time for Grid Friendly Appliance(TM)-type functionality
    GFA_freq_disconnect_time: float  # [s]  # Frequency violation disconnect time for Grid Friendly Appliance(TM)-type functionality
    GFA_volt_disconnect_time: float  # [s]  # Voltage violation disconnect time for Grid Friendly Appliance(TM)-type functionality
    GFA_status: bool  # Low frequency trip point for Grid Friendly Appliance(TM)-type functionality
    topological_parent: object  # topological parent as per GLM configuration


@unique
class CapacitorPhase(IntEnum):
    N = 8
    D = 256
    C = 4
    B = 2
    A = 1


@unique
class CapacitorSwitch(IntEnum):
    CLOSED = 1
    OPEN = 0


@unique
class CapacitorControl(IntEnum):
    CURRENT = 4
    VARVOLT = 3
    VOLT = 2
    VAR = 1
    MANUAL = 0


@unique
class CapacitorControlLevel(IntEnum):
    INDIVIDUAL = 1
    BANK = 0


@dataclass
class Capacitor(Node):
    pt_phase: List[CapacitorPhase]  # Phase(s) that the PT is on, used as measurement points for control
    phases_connected: List[CapacitorPhase]  # phases capacitors connected to
    switchA: CapacitorSwitch  # capacitor A switch open or close
    switchB: CapacitorSwitch  # capacitor B switch open or close
    switchC: CapacitorSwitch  # capacitor C switch open or close
    control: CapacitorControl  # control operation strategy
    cap_A_switch_count: float  # number of switch operations on Phase A
    cap_B_switch_count: float  # number of switch operations on Phase B
    cap_C_switch_count: float  # number of switch operations on Phase C
    voltage_set_high: float  # [V]  # Turn off if voltage is above this set point
    voltage_set_low: float  # [V]  # Turns on if voltage is below this set point
    VAr_set_high: float  # [VAr]  # high VAR set point for VAR control (turn off)
    VAr_set_low: float  # [VAr]  # low VAR set point for VAR control (turn on)
    current_set_low: float  # [A]  # high current set point for current control mode (turn on)
    current_set_high: float  # [A]  # low current set point for current control mode (turn off)
    capacitor_A: float  # [VAr]  # Capacitance value for phase A or phase AB
    capacitor_B: float  # [VAr]  # Capacitance value for phase B or phase BC
    capacitor_C: float  # [VAr]  # Capacitance value for phase C or phase CA
    cap_nominal_voltage: float  # [V]  # Nominal voltage for the capacitor. Used for calculation of capacitance value
    time_delay: float  # [s]  # control time delay
    dwell_time: float  # [s]  # Time for system to remain constant before a state change will be passed
    lockout_time: float  # [s]  # Time for capacitor to remain locked out from further switching operations (VARVOLT control)
    remote_sense: object  # Remote object for sensing values used for control schemes
    remote_sense_B: object  # Secondary Remote object for sensing values used for control schemes (VARVOLT uses two)
    control_level: CapacitorControlLevel  # define bank or individual control


@unique
class CurrDumpMode(IntEnum):
    polar = 1
    rect = 0


@dataclass
class CurrDump:
    group: str  # the group ID to output data for (all links if empty)
    runtime: timestamp  # the time to check current data
    filename: str  # the file to dump the current data into
    runcount: int  # the number of times the file has been written to
    mode: CurrDumpMode


@dataclass
class Emissions:
    Nuclear_Order: float
    Hydroelectric_Order: float
    Solarthermal_Order: float
    Biomass_Order: float
    Wind_Order: float
    Coal_Order: float
    Naturalgas_Order: float
    Geothermal_Order: float
    Petroleum_Order: float
    Naturalgas_Max_Out: float  # [kWh]
    Coal_Max_Out: float  # [kWh]
    Biomass_Max_Out: float  # [kWh]
    Geothermal_Max_Out: float  # [kWh]
    Hydroelectric_Max_Out: float  # [kWh]
    Nuclear_Max_Out: float  # [kWh]
    Wind_Max_Out: float  # [kWh]
    Petroleum_Max_Out: float  # [kWh]
    Solarthermal_Max_Out: float  # [kWh]
    Naturalgas_Out: float  # [kWh]
    Coal_Out: float  # [kWh]
    Biomass_Out: float  # [kWh]
    Geothermal_Out: float  # [kWh]
    Hydroelectric_Out: float  # [kWh]
    Nuclear_Out: float  # [kWh]
    Wind_Out: float  # [kWh]
    Petroleum_Out: float  # [kWh]
    Solarthermal_Out: float  # [kWh]
    Naturalgas_Conv_Eff: float  # [Btu/kWh]
    Coal_Conv_Eff: float  # [Btu/kWh]
    Biomass_Conv_Eff: float  # [Btu/kWh]
    Geothermal_Conv_Eff: float  # [Btu/kWh]
    Hydroelectric_Conv_Eff: float  # [Btu/kWh]
    Nuclear_Conv_Eff: float  # [Btu/kWh]
    Wind_Conv_Eff: float  # [Btu/kWh]
    Petroleum_Conv_Eff: float  # [Btu/kWh]
    Solarthermal_Conv_Eff: float  # [Btu/kWh]
    Naturalgas_CO2: float  # [lb/Btu]
    Coal_CO2: float  # [lb/Btu]
    Biomass_CO2: float  # [lb/Btu]
    Geothermal_CO2: float  # [lb/Btu]
    Hydroelectric_CO2: float  # [lb/Btu]
    Nuclear_CO2: float  # [lb/Btu]
    Wind_CO2: float  # [lb/Btu]
    Petroleum_CO2: float  # [lb/Btu]
    Solarthermal_CO2: float  # [lb/Btu]
    Naturalgas_SO2: float  # [lb/Btu]
    Coal_SO2: float  # [lb/Btu]
    Biomass_SO2: float  # [lb/Btu]
    Geothermal_SO2: float  # [lb/Btu]
    Hydroelectric_SO2: float  # [lb/Btu]
    Nuclear_SO2: float  # [lb/Btu]
    Wind_SO2: float  # [lb/Btu]
    Petroleum_SO2: float  # [lb/Btu]
    Solarthermal_SO2: float  # [lb/Btu]
    Naturalgas_NOx: float  # [lb/Btu]
    Coal_NOx: float  # [lb/Btu]
    Biomass_NOx: float  # [lb/Btu]
    Geothermal_NOx: float  # [lb/Btu]
    Hydroelectric_NOx: float  # [lb/Btu]
    Nuclear_NOx: float  # [lb/Btu]
    Wind_NOx: float  # [lb/Btu]
    Petroleum_NOx: float  # [lb/Btu]
    Solarthermal_NOx: float  # [lb/Btu]
    Naturalgas_emissions_CO2: float  # [lb]
    Naturalgas_emissions_SO2: float  # [lb]
    Naturalgas_emissions_NOx: float  # [lb]
    Coal_emissions_CO2: float  # [lb]
    Coal_emissions_SO2: float  # [lb]
    Coal_emissions_NOx: float  # [lb]
    Biomass_emissions_CO2: float  # [lb]
    Biomass_emissions_SO2: float  # [lb]
    Biomass_emissions_NOx: float  # [lb]
    Geothermal_emissions_CO2: float  # [lb]
    Geothermal_emissions_SO2: float  # [lb]
    Geothermal_emissions_NOx: float  # [lb]
    Hydroelectric_emissions_CO2: float  # [lb]
    Hydroelectric_emissions_SO2: float  # [lb]
    Hydroelectric_emissions_NOx: float  # [lb]
    Nuclear_emissions_CO2: float  # [lb]
    Nuclear_emissions_SO2: float  # [lb]
    Nuclear_emissions_NOx: float  # [lb]
    Wind_emissions_CO2: float  # [lb]
    Wind_emissions_SO2: float  # [lb]
    Wind_emissions_NOx: float  # [lb]
    Petroleum_emissions_CO2: float  # [lb]
    Petroleum_emissions_SO2: float  # [lb]
    Petroleum_emissions_NOx: float  # [lb]
    Solarthermal_emissions_CO2: float  # [lb]
    Solarthermal_emissions_SO2: float  # [lb]
    Solarthermal_emissions_NOx: float  # [lb]
    Total_emissions_CO2: float  # [lb]
    Total_emissions_SO2: float  # [lb]
    Total_emissions_NOx: float  # [lb]
    Total_energy_out: float  # [kWh]
    Region: float
    cycle_interval: float  # [s]


@unique
class FaultCheckCheckMode(IntEnum):
    ALL = 2
    ONCHANGE = 1
    SINGLE = 0


@dataclass
class FaultCheck:
    check_mode: FaultCheckCheckMode  # Frequency of fault checks
    output_filename: str  # Output filename for list of unsupported nodes
    reliability_mode: bool  # General flag indicating if fault_check is operating under faulting or restoration mode -- reliability set this
    strictly_radial: bool  # Flag to indicate if a system is known to be strictly radial -- uses radial assumptions for reliability alterations
    full_output_file: bool  # Flag to indicate if the output_filename report contains both supported and unsupported nodes -- if false, just does unsupported
    grid_association: bool  # Flag to indicate if multiple, distinct grids are allowed in a GLM, or if anything not attached to the master swing is removed
    eventgen_object: object  # Link to generic eventgen object to handle unexpected faults


@unique
class FrequencyGeneratorFrequencyMode(IntEnum):
    AUTO = 1
    OFF = 0


@dataclass
class FrequencyGenerator:
    Frequency_Mode: FrequencyGeneratorFrequencyMode  # Frequency object operations mode
    Frequency: float  # [Hz]  # Instantaneous frequency value
    FreqChange: float  # [Hz/s]  # Frequency change from last timestep
    Deadband: float  # [Hz]  # Frequency deadband of the governor
    Tolerance: float  # [%]  # % threshold a power difference must be before it is cared about
    M: float  # [pu*s]  # Inertial constant of the system
    D: float  # [%] Load-damping constant
    Rated_power: float  # [W]  # Rated power of system (base power)
    Gen_power: float  # [W]  # Mechanical power equivalent
    Load_power: float  # [W]  # Last sensed load value
    Gov_delay: float  # [s]  # Governor delay time
    Ramp_rate: float  # [W/s]  # Ramp ideal ramp rate
    Low_Freq_OI: float  # [Hz]  # Low frequency setpoint for GFA devices
    High_Freq_OI: float  # [Hz]  # High frequency setpoint for GFA devices
    avg24: float  # [Hz]  # Average of last 24 hourly instantaneous measurements
    std24: float  # [Hz]  # Standard deviation of last 24 hourly instantaneous measurements
    avg168: float  # [Hz]  # Average of last 168 hourly instantaneous measurements
    std168: float  # [Hz]  # Standard deviation of last 168 hourly instantaneous measurements
    Num_Resp_Eqs: int  # Total number of equations the response can contain


@unique
class LinkStatus(IntEnum):
    OPEN = 0
    CLOSED = 1


@unique
class LinkFlowDirection(IntEnum):
    CN = 768
    CR = 512
    CF = 256
    BN = 48
    BR = 32
    BF = 16
    AN = 3
    AR = 2
    AF = 1
    UNKNOWN = 0


@dataclass
class Link(PowerFlowObject):
    status: LinkStatus  #
    from_: object  # from_node - source node
    to: object  # to_node - load node
    power_in: complex  # [VA]  # power flow in (w.r.t from node)
    power_out: complex  # [VA]  # power flow out (w.r.t to node)
    power_out_real: float  # [W]  # power flow out (w.r.t to node), real
    power_losses: complex  # [VA]  # power losses
    power_in_A: complex  # [VA]  # power flow in (w.r.t from node), phase A
    power_in_B: complex  # [VA]  # power flow in (w.r.t from node), phase B
    power_in_C: complex  # [VA]  # power flow in (w.r.t from node), phase C
    power_out_A: complex  # [VA]  # power flow out (w.r.t to node), phase A
    power_out_B: complex  # [VA]  # power flow out (w.r.t to node), phase B
    power_out_C: complex  # [VA]  # power flow out (w.r.t to node), phase C
    power_losses_A: complex  # [VA]  # power losses, phase A
    power_losses_B: complex  # [VA]  # power losses, phase B
    power_losses_C: complex  # [VA]  # power losses, phase C
    current_out_A: complex  # [A]  # current flow out of link (w.r.t. to node), phase A
    current_out_B: complex  # [A]  # current flow out of link (w.r.t. to node), phase B
    current_out_C: complex  # [A]  # current flow out of link (w.r.t. to node), phase C
    current_in_A: complex  # [A]  # current flow to link (w.r.t from node), phase A
    current_in_B: complex  # [A]  # current flow to link (w.r.t from node), phase B
    current_in_C: complex  # [A]  # current flow to link (w.r.t from node), phase C
    fault_current_in_A: complex  # [A]  # fault current flowing in, phase A
    fault_current_in_B: complex  # [A]  # fault current flowing in, phase B
    fault_current_in_C: complex  # [A]  # fault current flowing in, phase C
    fault_current_out_A: complex  # [A]  # fault current flowing out, phase A
    fault_current_out_B: complex  # [A]  # fault current flowing out, phase B
    fault_current_out_C: complex  # [A]  # fault current flowing out, phase C
    flow_direction: List[LinkFlowDirection]  # flag used for describing direction of the flow of power
    mean_repair_time: float  # [s]  # Time after a fault clears for the object to be back in service
    continuous_rating: float  # [A]  # Continuous rating for this link object (set individual line segments
    emergency_rating: float  # [A]  # Emergency rating for this link object (set individual line segments
    inrush_convergence_value: float  # [V]  # Tolerance, as change in line voltage drop between iterations, for deltamode in-rush completion


@unique
class FusePhaseStatus(IntEnum):
    GOOD = 1
    BLOWN = 0


@unique
class FuseRepairDistType(IntEnum):
    EXPONENTIAL = 1
    NONE = 0


@dataclass
class Fuse(Link):
    phase_A_status: FusePhaseStatus
    phase_B_status: FusePhaseStatus
    phase_C_status: FusePhaseStatus
    repair_dist_type: FuseRepairDistType
    current_limit: float  # [A]
    mean_replacement_time: float  # [s]
    fuse_resistance: float  # [Ohm]  # The resistance value of the fuse when it is not blown.


@dataclass
class ImpedanceDump:
    group: str  # the group ID to output data for (all links if empty)
    filename: str  # the file to dump the current data into
    runtime: timestamp  # the time to check voltage data
    runcount: int  # the number of times the file has been written to


@dataclass
class Line:
    configuration: object
    length: float  # [ft]


@dataclass
class LineConfiguration:
    conductor_A: object
    conductor_B: object
    conductor_C: object
    conductor_N: object
    spacing: object
    z11: complex  # [Ohm/mile]
    z12: complex  # [Ohm/mile]
    z13: complex  # [Ohm/mile]
    z21: complex  # [Ohm/mile]
    z22: complex  # [Ohm/mile]
    z23: complex  # [Ohm/mile]
    z31: complex  # [Ohm/mile]
    z32: complex  # [Ohm/mile]
    z33: complex  # [Ohm/mile]
    c11: float  # [nF/mile]
    c12: float  # [nF/mile]
    c13: float  # [nF/mile]
    c21: float  # [nF/mile]
    c22: float  # [nF/mile]
    c23: float  # [nF/mile]
    c31: float  # [nF/mile]
    c32: float  # [nF/mile]
    c33: float  # [nF/mile]
    rating_summer_continuous: float  # [A]  # amp rating in summer, continuous
    rating_summer_emergency: float  # [A]  # amp rating in summer, short term
    rating_winter_continuous: float  # [A]  # amp rating in winter, continuous
    rating_winter_emergency: float  # [A]  # amp rating in winter, short term


@dataclass
class LineSpacing:
    distance_AB: float  # [ft]
    distance_BC: float  # [ft]
    distance_AC: float  # [ft]
    distance_AN: float  # [ft]
    distance_BN: float  # [ft]
    distance_CN: float  # [ft]
    distance_AE: float  # [ft]  # distance between phase A wire and earth
    distance_BE: float  # [ft]  # distance between phase B wire and earth
    distance_CE: float  # [ft]  # distance between phase C wire and earth
    distance_NE: float  # [ft]  # distance between neutral wire and earth


@unique
class LoadLoadClass(IntEnum):
    A = 4
    I = 3
    C = 2
    R = 1
    U = 0


@dataclass
class Load(Node):
    load_class: LoadLoadClass  # Flag to track load type, not currently used for anything except sorting
    constant_power_A: complex  # [VA]  # constant power load on phase A, specified as VA
    constant_power_B: complex  # [VA]  # constant power load on phase B, specified as VA
    constant_power_C: complex  # [VA]  # constant power load on phase C, specified as VA
    constant_power_A_real: float  # [W]  # constant power load on phase A, real only, specified as W
    constant_power_B_real: float  # [W]  # constant power load on phase B, real only, specified as W
    constant_power_C_real: float  # [W]  # constant power load on phase C, real only, specified as W
    constant_power_A_reac: float  # [VAr]  # constant power load on phase A, imaginary only, specified as VAr
    constant_power_B_reac: float  # [VAr]  # constant power load on phase B, imaginary only, specified as VAr
    constant_power_C_reac: float  # [VAr]  # constant power load on phase C, imaginary only, specified as VAr
    constant_current_A: complex  # [A]  # constant current load on phase A, specified as Amps
    constant_current_B: complex  # [A]  # constant current load on phase B, specified as Amps
    constant_current_C: complex  # [A]  # constant current load on phase C, specified as Amps
    constant_current_A_real: float  # [A]  # constant current load on phase A, real only, specified as Amps
    constant_current_B_real: float  # [A]  # constant current load on phase B, real only, specified as Amps
    constant_current_C_real: float  # [A]  # constant current load on phase C, real only, specified as Amps
    constant_current_A_reac: float  # [A]  # constant current load on phase A, imaginary only, specified as Amps
    constant_current_B_reac: float  # [A]  # constant current load on phase B, imaginary only, specified as Amps
    constant_current_C_reac: float  # [A]  # constant current load on phase C, imaginary only, specified as Amps
    constant_impedance_A: complex  # [Ohm]  # constant impedance load on phase A, specified as Ohms
    constant_impedance_B: complex  # [Ohm]  # constant impedance load on phase B, specified as Ohms
    constant_impedance_C: complex  # [Ohm]  # constant impedance load on phase C, specified as Ohms
    constant_impedance_A_real: float  # [Ohm]  # constant impedance load on phase A, real only, specified as Ohms
    constant_impedance_B_real: float  # [Ohm]  # constant impedance load on phase B, real only, specified as Ohms
    constant_impedance_C_real: float  # [Ohm]  # constant impedance load on phase C, real only, specified as Ohms
    constant_impedance_A_reac: float  # [Ohm]  # constant impedance load on phase A, imaginary only, specified as Ohms
    constant_impedance_B_reac: float  # [Ohm]  # constant impedance load on phase B, imaginary only, specified as Ohms
    constant_impedance_C_reac: float  # [Ohm]  # constant impedance load on phase C, imaginary only, specified as Ohms
    constant_power_AN: complex  # [VA]  # constant power wye-connected load on phase A, specified as VA
    constant_power_BN: complex  # [VA]  # constant power wye-connected load on phase B, specified as VA
    constant_power_CN: complex  # [VA]  # constant power wye-connected load on phase C, specified as VA
    constant_power_AN_real: float  # [W]  # constant power wye-connected load on phase A, real only, specified as W
    constant_power_BN_real: float  # [W]  # constant power wye-connected load on phase B, real only, specified as W
    constant_power_CN_real: float  # [W]  # constant power wye-connected load on phase C, real only, specified as W
    constant_power_AN_reac: float  # [VAr]  # constant power wye-connected load on phase A, imaginary only, specified as VAr
    constant_power_BN_reac: float  # [VAr]  # constant power wye-connected load on phase B, imaginary only, specified as VAr
    constant_power_CN_reac: float  # [VAr]  # constant power wye-connected load on phase C, imaginary only, specified as VAr
    constant_current_AN: complex  # [A]  # constant current wye-connected load on phase A, specified as Amps
    constant_current_BN: complex  # [A]  # constant current wye-connected load on phase B, specified as Amps
    constant_current_CN: complex  # [A]  # constant current wye-connected load on phase C, specified as Amps
    constant_current_AN_real: float  # [A]  # constant current wye-connected load on phase A, real only, specified as Amps
    constant_current_BN_real: float  # [A]  # constant current wye-connected load on phase B, real only, specified as Amps
    constant_current_CN_real: float  # [A]  # constant current wye-connected load on phase C, real only, specified as Amps
    constant_current_AN_reac: float  # [A]  # constant current wye-connected load on phase A, imaginary only, specified as Amps
    constant_current_BN_reac: float  # [A]  # constant current wye-connected load on phase B, imaginary only, specified as Amps
    constant_current_CN_reac: float  # [A]  # constant current wye-connected load on phase C, imaginary only, specified as Amps
    constant_impedance_AN: complex  # [Ohm]  # constant impedance wye-connected load on phase A, specified as Ohms
    constant_impedance_BN: complex  # [Ohm]  # constant impedance wye-connected load on phase B, specified as Ohms
    constant_impedance_CN: complex  # [Ohm]  # constant impedance wye-connected load on phase C, specified as Ohms
    constant_impedance_AN_real: float  # [Ohm]  # constant impedance wye-connected load on phase A, real only, specified as Ohms
    constant_impedance_BN_real: float  # [Ohm]  # constant impedance wye-connected load on phase B, real only, specified as Ohms
    constant_impedance_CN_real: float  # [Ohm]  # constant impedance wye-connected load on phase C, real only, specified as Ohms
    constant_impedance_AN_reac: float  # [Ohm]  # constant impedance wye-connected load on phase A, imaginary only, specified as Ohms
    constant_impedance_BN_reac: float  # [Ohm]  # constant impedance wye-connected load on phase B, imaginary only, specified as Ohms
    constant_impedance_CN_reac: float  # [Ohm]  # constant impedance wye-connected load on phase C, imaginary only, specified as Ohms
    constant_power_AB: complex  # [VA]  # constant power delta-connected load on phase A, specified as VA
    constant_power_BC: complex  # [VA]  # constant power delta-connected load on phase B, specified as VA
    constant_power_CA: complex  # [VA]  # constant power delta-connected load on phase C, specified as VA
    constant_power_AB_real: float  # [W]  # constant power delta-connected load on phase A, real only, specified as W
    constant_power_BC_real: float  # [W]  # constant power delta-connected load on phase B, real only, specified as W
    constant_power_CA_real: float  # [W]  # constant power delta-connected load on phase C, real only, specified as W
    constant_power_AB_reac: float  # [VAr]  # constant power delta-connected load on phase A, imaginary only, specified as VAr
    constant_power_BC_reac: float  # [VAr]  # constant power delta-connected load on phase B, imaginary only, specified as VAr
    constant_power_CA_reac: float  # [VAr]  # constant power delta-connected load on phase C, imaginary only, specified as VAr
    constant_current_AB: complex  # [A]  # constant current delta-connected load on phase A, specified as Amps
    constant_current_BC: complex  # [A]  # constant current delta-connected load on phase B, specified as Amps
    constant_current_CA: complex  # [A]  # constant current delta-connected load on phase C, specified as Amps
    constant_current_AB_real: float  # [A]  # constant current delta-connected load on phase A, real only, specified as Amps
    constant_current_BC_real: float  # [A]  # constant current delta-connected load on phase B, real only, specified as Amps
    constant_current_CA_real: float  # [A]  # constant current delta-connected load on phase C, real only, specified as Amps
    constant_current_AB_reac: float  # [A]  # constant current delta-connected load on phase A, imaginary only, specified as Amps
    constant_current_BC_reac: float  # [A]  # constant current delta-connected load on phase B, imaginary only, specified as Amps
    constant_current_CA_reac: float  # [A]  # constant current delta-connected load on phase C, imaginary only, specified as Amps
    constant_impedance_AB: complex  # [Ohm]  # constant impedance delta-connected load on phase A, specified as Ohms
    constant_impedance_BC: complex  # [Ohm]  # constant impedance delta-connected load on phase B, specified as Ohms
    constant_impedance_CA: complex  # [Ohm]  # constant impedance delta-connected load on phase C, specified as Ohms
    constant_impedance_AB_real: float  # [Ohm]  # constant impedance delta-connected load on phase A, real only, specified as Ohms
    constant_impedance_BC_real: float  # [Ohm]  # constant impedance delta-connected load on phase B, real only, specified as Ohms
    constant_impedance_CA_real: float  # [Ohm]  # constant impedance delta-connected load on phase C, real only, specified as Ohms
    constant_impedance_AB_reac: float  # [Ohm]  # constant impedance delta-connected load on phase A, imaginary only, specified as Ohms
    constant_impedance_BC_reac: float  # [Ohm]  # constant impedance delta-connected load on phase B, imaginary only, specified as Ohms
    constant_impedance_CA_reac: float  # [Ohm]  # constant impedance delta-connected load on phase C, imaginary only, specified as Ohms
    measured_voltage_A: complex  # current measured voltage on phase A
    measured_voltage_B: complex  # current measured voltage on phase B
    measured_voltage_C: complex  # current measured voltage on phase C
    measured_voltage_AB: complex  # current measured voltage on phases AB
    measured_voltage_BC: complex  # current measured voltage on phases BC
    measured_voltage_CA: complex  # current measured voltage on phases CA
    phase_loss_protection: bool  # Trip all three phases of the load if a fault occurs
    base_power_A: float  # [VA]  # in similar format as ZIPload, this represents the nominal power on phase A before applying ZIP fractions
    base_power_B: float  # [VA]  # in similar format as ZIPload, this represents the nominal power on phase B before applying ZIP fractions
    base_power_C: float  # [VA]  # in similar format as ZIPload, this represents the nominal power on phase C before applying ZIP fractions
    power_pf_A: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase A constant power portion of load
    current_pf_A: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase A constant current portion of load
    impedance_pf_A: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase A constant impedance portion of load
    power_pf_B: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase B constant power portion of load
    current_pf_B: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase B constant current portion of load
    impedance_pf_B: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase B constant impedance portion of load
    power_pf_C: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase C constant power portion of load
    current_pf_C: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase C constant current portion of load
    impedance_pf_C: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase C constant impedance portion of load
    power_fraction_A: float  # [pu]  # this is the constant power fraction of base power on phase A
    current_fraction_A: float  # [pu]  # this is the constant current fraction of base power on phase A
    impedance_fraction_A: float  # [pu]  # this is the constant impedance fraction of base power on phase A
    power_fraction_B: float  # [pu]  # this is the constant power fraction of base power on phase B
    current_fraction_B: float  # [pu]  # this is the constant current fraction of base power on phase B
    impedance_fraction_B: float  # [pu]  # this is the constant impedance fraction of base power on phase B
    power_fraction_C: float  # [pu]  # this is the constant power fraction of base power on phase C
    current_fraction_C: float  # [pu]  # this is the constant current fraction of base power on phase C
    impedance_fraction_C: float  # [pu]  # this is the constant impedance fraction of base power on phase C


@unique
class LoadTrackerOperation(IntEnum):
    ANGLE = 3
    MAGNITUDE = 2
    IMAGINARY = 1
    REAL = 0


@dataclass
class LoadTracker:
    target: object  # target object to track the load of
    target_property: str  # property on the target object representing the load
    operation: LoadTrackerOperation  # operation to perform on complex property types
    full_scale: float  # magnitude of the load at full load, used for feed-forward control
    setpoint: float  # load setpoint to track to
    deadband: float  # percentage deadband
    damping: float  # load setpoint to track to
    output: float  # output scaling value
    feedback: float  # the feedback signal, for reference purposes


@unique
class MeterBillMode(IntEnum):
    TIERED_RTP = 4
    HOURLY = 3
    TIERED = 2
    UNIFORM = 1
    NONE = 0


@dataclass
class Meter:
    measured_real_energy: float  # [Wh]  # metered real energy consumption, cummalitive
    measured_reactive_energy: float  # [VAh]  # metered reactive energy consumption, cummalitive
    measured_power: complex  # [VA]  # metered real power
    measured_power_A: complex  # [VA]  # metered complex power on phase A
    measured_power_B: complex  # [VA]  # metered complex power on phase B
    measured_power_C: complex  # [VA]  # metered complex power on phase C
    measured_demand: float  # [W]  # greatest metered real power during simulation
    measured_real_power: float  # [W]  # metered real power
    measured_reactive_power: float  # [VAr]  # metered reactive power
    meter_power_consumption: complex  # [VA]  # metered power used for operating the meter; standby and communication losses
    measured_voltage_A: complex  # [V]  # measured line-to-neutral voltage on phase A
    measured_voltage_B: complex  # [V]  # measured line-to-neutral voltage on phase B
    measured_voltage_C: complex  # [V]  # measured line-to-neutral voltage on phase C
    measured_voltage_AB: complex  # [V]  # measured line-to-line voltage on phase AB
    measured_voltage_BC: complex  # [V]  # measured line-to-line voltage on phase BC
    measured_voltage_CA: complex  # [V]  # measured line-to-line voltage on phase CA
    measured_current_A: complex  # [A]  # measured current on phase A
    measured_current_B: complex  # [A]  # measured current on phase B
    measured_current_C: complex  # [A]  # measured current on phase C
    customer_interrupted: bool  # Reliability flag - goes active if the customer is in an 'interrupted' state
    customer_interrupted_secondary: bool  # Reliability flag - goes active if the customer is in an 'secondary interrupted' state - i.e., momentary
    monthly_bill: float  # [$]  # Accumulator for the current month's bill
    previous_monthly_bill: float  # [$]  # Total monthly bill for the previous month
    previous_monthly_energy: float  # [kWh]  # Total monthly energy for the previous month
    monthly_fee: float  # [$] Once a month flat fee for customer hook-up
    monthly_energy: float  # [kWh]  # Accumulator for the current month's energy consumption
    bill_mode: MeterBillMode  # Billing structure desired
    power_market: object  # Market (auction object) where the price is being received from
    bill_day: int  # day of month bill is to be processed (currently limited to days 1-28)
    price: float  # [$/kWh]  # current price of electricity
    price_base: float  # [$/kWh]  # Used only in TIERED_RTP mode to describe the price before the first tier
    first_tier_price: float  # [$/kWh]  # price of electricity between first tier and second tier energy usage
    first_tier_energy: float  # [kWh]  # switching point between base price and first tier price
    second_tier_price: float  # [$/kWh]  # price of electricity between second tier and third tier energy usage
    second_tier_energy: float  # [kWh]  # switching point between first tier price and second tier price
    third_tier_price: float  # [$/kWh]  # price of electricity when energy usage exceeds third tier energy usage
    third_tier_energy: float  # [kWh]  # switching point between second tier price and third tier price


@dataclass
class Motor(Node):
    pass


@dataclass
class OverheadLine(PowerFlowObject):
    configuration: object
    length: float  # [ft]


@dataclass
class OverheadLineConductor:
    geometric_mean_radius: float  # [ft]  # radius of the conductor
    resistance: float  # [Ohm/mile]  # resistance in Ohms/mile of the conductor
    diameter: float  # [in]  # Diameter of line for capacitance calculations
    rating.summer.continuous: float  # [A]  # Continuous summer amp rating
    rating.summer.emergency: float  # [A]  # Emergency summer amp rating
    rating.winter.continuous: float  # [A]  # Continuous winter amp rating
    rating.winter.emergency: float  # [A]  # Emergency winter amp rating


@dataclass
class PowerMetrics:
    SAIFI: float  # Displays annual SAIFI values as per IEEE 1366-2003
    SAIFI_int: float  # Displays SAIFI values over the period specified by base_time_value as per IEEE 1366-2003
    SAIDI: float  # Displays annual SAIDI values as per IEEE 1366-2003
    SAIDI_int: float  # Displays SAIDI values over the period specified by base_time_value as per IEEE 1366-2003
    CAIDI: float  # Displays annual CAIDI values as per IEEE 1366-2003
    CAIDI_int: float  # Displays SAIDI values over the period specified by base_time_value as per IEEE 1366-2003
    ASAI: float  # Displays annual AISI values as per IEEE 1366-2003
    ASAI_int: float  # Displays AISI values over the period specified by base_time_value as per IEEE 1366-2003
    MAIFI: float  # Displays annual MAIFI values as per IEEE 1366-2003
    MAIFI_int: float  # Displays MAIFI values over the period specified by base_time_value as per IEEE 1366-2003
    base_time_value: float  # [s]  # time period over which _int values are claculated


@dataclass
class PowerFlowLibrary:
    pass


@dataclass
class PQLoad(Load):
    weather: object
    T_nominal: float  # [degF]
    Zp_T: float  # [ohm/degF]
    Zp_H: float  # [ohm/%]
    Zp_S: float  # [ohm*h/Btu]
    Zp_W: float  # [ohm/mph]
    Zp_R: float  # [ohm*h/in]
    Zp: float  # [ohm]
    Zq_T: float  # [F/degF]
    Zq_H: float  # [F/%]
    Zq_S: float  # [F*h/Btu]
    Zq_W: float  # [F/mph]
    Zq_R: float  # [F*h/in]
    Zq: float  # [F]
    Im_T: float  # [A/degF]
    Im_H: float  # [A/%]
    Im_S: float  # [A*h/Btu]
    Im_W: float  # [A/mph]
    Im_R: float  # [A*h/in]
    Im: float  # [A]
    Ia_T: float  # [deg/degF]
    Ia_H: float  # [deg/%]
    Ia_S: float  # [deg*h/Btu]
    Ia_W: float  # [deg/mph]
    Ia_R: float  # [deg*h/in]
    Ia: float  # [deg]
    Pp_T: float  # [W/degF]
    Pp_H: float  # [W/%]
    Pp_S: float  # [W*h/Btu]
    Pp_W: float  # [W/mph]
    Pp_R: float  # [W*h/in]
    Pp: float  # [W]
    Pq_T: float  # [VAr/degF]
    Pq_H: float  # [VAr/%]
    Pq_S: float  # [VAr*h/Btu]
    Pq_W: float  # [VAr/mph]
    Pq_R: float  # [VAr*h/in]
    Pq: float  # [VAr]
    input_temp: float  # [degF]
    input_humid: float  # [%]
    input_solar: float  # [Btu/h]
    input_wind: float  # [mph]
    input_rain: float  # [in/h]
    output_imped_p: float  # [Ohm]
    output_imped_q: float  # [Ohm]
    output_current_m: float  # [A]
    output_current_a: float  # [deg]
    output_power_p: float  # [W]
    output_power_q: float  # [VAr]
    output_impedance: complex  # [ohm]
    output_current: complex  # [A]
    output_power: complex  # [VA]


@unique
class SwitchPhaseState(IntEnum):
    CLOSED = 1
    OPEN = 0


@unique
class SwitchOperatingMode(IntEnum):
    BANKED = 1
    INDIVIDUAL = 0


@dataclass
class Switch(Link):
    phase_A_state: SwitchPhaseState  # Defines the current state of the phase A switch
    phase_B_state: SwitchPhaseState  # Defines the current state of the phase B switch
    phase_C_state: SwitchPhaseState  # Defines the current state of the phase C switch
    operating_mode: SwitchOperatingMode  # Defines whether the switch operates in a banked or per-phase control mode
    switch_resistance: float  # [Ohm]  # The resistance value of the switch when it is not blown.


@dataclass
class Recloser(Switch):
    retry_time: float  # [s]  # the amount of time in seconds to wait before the recloser attempts to close
    max_number_of_tries: float  # the number of times the recloser will try to close before permanently opening
    number_of_tries: float  # Current number of tries recloser has attempted


@dataclass
class Regulator(Link):
    configuration: object  # reference to the regulator_configuration object used to determine regulator properties
    tap_A: int  # current tap position of tap A
    tap_B: int  # current tap position of tap B
    tap_C: int  # current tap position of tap C
    tap_A_change_count: float  # count of all physical tap changes on phase A since beginning of simulation (plus initial value)
    tap_B_change_count: float  # count of all physical tap changes on phase B since beginning of simulation (plus initial value)
    tap_C_change_count: float  # count of all physical tap changes on phase C since beginning of simulation (plus initial value)
    sense_node: object  # Node to be monitored for voltage control in remote sense mode
    regulator_resistance: float  # [Ohm]  # The resistance value of the regulator when it is not blown.


@unique
class RegulatorConfigurationConnectType(IntEnum):
    CLOSED_DELTA = 5
    OPEN_DELTA_CABA = 4
    OPEN_DELTA_BCAC = 3
    OPEN_DELTA_ABBC = 2
    WYE_WYE = 1
    UNKNOWN = 0


@unique
class RegulatorConfigurationControlLevel(IntEnum):
    BANK = 2
    INDIVIDUAL = 1


@unique
class RegulatorConfigurationControl(IntEnum):
    REMOTE_NODE = 3
    LINE_DROP_COMP = 4
    OUTPUT_VOLTAGE = 2
    MANUAL = 1


@unique
class RegulatorConfigurationReverseFlowControl(IntEnum):
    LOCK_CURRENT_POSITION = 2
    LOCK_NEUTRAL = 1
    LOCK_NONE = 0


@unique
class RegulatorConfigurationType(IntEnum):
    B = 2
    A = 1


@unique
class RegulatorConfigurationPhase(IntEnum):
    C = 4
    B = 2
    A = 1


@dataclass
class RegulatorConfiguration:
    connect_type: RegulatorConfigurationConnectType  # Designation of connection style
    band_center: float  # [V]  # band center setting of regulator control
    band_width: float  # [V]  # band width setting of regulator control
    time_delay: float  # [s]  # mechanical time delay between tap changes
    dwell_time: float  # [s]  # time delay before a control action of regulator control
    raise_taps: int  # number of regulator raise taps, or the maximum raise voltage tap position
    lower_taps: int  # number of regulator lower taps, or the minimum lower voltage tap position
    current_transducer_ratio: float  # [pu]  # primary rating of current transformer
    power_transducer_ratio: float  # [pu]  # potential transformer rating
    compensator_r_setting_A: float  # [V]  # Line Drop Compensation R setting of regulator control (in volts) on Phase A
    compensator_r_setting_B: float  # [V]  # Line Drop Compensation R setting of regulator control (in volts) on Phase B
    compensator_r_setting_C: float  # [V]  # Line Drop Compensation R setting of regulator control (in volts) on Phase C
    compensator_x_setting_A: float  # [V]  # Line Drop Compensation X setting of regulator control (in volts) on Phase A
    compensator_x_setting_B: float  # [V]  # Line Drop Compensation X setting of regulator control (in volts) on Phase B
    compensator_x_setting_C: float  # [V]  # Line Drop Compensation X setting of regulator control (in volts) on Phase C
    CT_phase: RegulatorConfigurationPhase  # phase(s) monitored by CT
    PT_phase: RegulatorConfigurationPhase  # phase(s) monitored by PT
    regulation: float  # regulation of voltage regulator in %
    control_level: RegulatorConfigurationControlLevel  # Designates whether control is on per-phase or banked level
    control: RegulatorConfigurationControl  # Type of control used for regulating voltage
    reverse_flow_control: RegulatorConfigurationReverseFlowControl  # Type of control used when power is flowing in reverse through the regulator
    type: RegulatorConfigurationType  # Defines regulator type
    tap_pos_A: int  # initial tap position of phase A
    tap_pos_B: int  # initial tap position of phase B
    tap_pos_C: int  # initial tap position of phase C


@dataclass
class Restoration:
    reconfig_attempts: int  # Number of reconfigurations/timestep to try before giving up
    reconfig_iteration_limit: int  # Number of iterations to let PF go before flagging this as a bad reconfiguration
    source_vertex: object  # Source vertex object for reconfiguration
    faulted_section: object  # Faulted section for reconfiguration
    feeder_power_limit: str  # Comma-separated power limit (VA) for feeders during reconfiguration
    feeder_power_links: str  # Comma-separated list of link-based objects for monitoring power through
    feeder_vertex_list: str  # Comma-separated object list that defines the feeder vertices
    microgrid_power_limit: str  # Comma-separated power limit (complex VA) for microgrids during reconfiguration
    microgrid_power_links: str  # Comma-separated list of link-based objects for monitoring power through
    microgrid_vertex_list: str  # Comma-separated object list that defines the microgrid vertices
    lower_voltage_limit: float  # [pu]  # Lower voltage limit for the reconfiguration validity checks - per unit
    upper_voltage_limit: float  # [pu]  # Upper voltage limit for the reconfiguration validity checks - per unit
    output_filename: str  # Output text file name to describe final or attempted switching operations
    generate_all_scenarios: bool  # Flag to determine if restoration reconfiguration and continues, or explores the full space


@unique
class SectionalizerPhaseState(IntEnum):
    CLOSED = 1
    OPEN = 0


@unique
class SectionalizerOperatingMode(IntEnum):
    BANKED = 1
    INDIVIDUAL = 0


@dataclass
class Sectionalizer(Switch):
    phase_A_state: SectionalizerPhaseState  # Defines the current state of the phase A switch
    phase_B_state: SectionalizerPhaseState  # Defines the current state of the phase B switch
    phase_C_state: SectionalizerPhaseState  # Defines the current state of the phase C switch
    operating_mode: SectionalizerOperatingMode  # Defines whether the switch operates in a banked or per-phase control mode
    switch_resistance: float  # [Ohm]  # The resistance value of the switch when it is not blown.


@dataclass
class SeriesReactor(Link):
    phase_A_impedance: complex  # [Ohm]  # Series impedance of reactor on phase A
    phase_A_resistance: float  # [Ohm]  # Resistive portion of phase A's impedance
    phase_A_reactance: float  # [Ohm]  # Reactive portion of phase A's impedance
    phase_B_impedance: complex  # [Ohm]  # Series impedance of reactor on phase B
    phase_B_resistance: float  # [Ohm]  # Resistive portion of phase B's impedance
    phase_B_reactance: float  # [Ohm]  # Reactive portion of phase B's impedance
    phase_C_impedance: complex  # [Ohm]  # Series impedance of reactor on phase C
    phase_C_resistance: float  # [Ohm]  # Resistive portion of phase C's impedance
    phase_C_reactance: float  # [Ohm]  # Reactive portion of phase C's impedance
    rated_current_limit: float  # [A]  # Rated current limit for the reactor


@unique
class SubstationReferencePhase(IntEnum):
    PHASE_C = 2
    PHASE_B = 1
    PHASE_A = 0


@dataclass
class Substation(Node):
    zero_sequence_voltage: complex  # [V]  # The zero sequence representation of the voltage for the substation object.
    positive_sequence_voltage: complex  # [V]  # The positive sequence representation of the voltage for the substation object.
    negative_sequence_voltage: complex  # [V]  # The negative sequence representation of the voltage for the substation object.
    base_power: float  # [VA]  # The 3 phase VA power rating of the substation.
    power_convergence_value: float  # [VA]  # Default convergence criterion before power is posted to pw_load objects if connected, otherwise ignored
    reference_phase: SubstationReferencePhase  # The reference phase for the positive sequence voltage.
    transmission_level_constant_power_load: complex  # [VA]  # the average constant power load to be posted directly to the pw_load object.
    transmission_level_constant_current_load: complex  # [A]  # the average constant current load at nominal voltage to be posted directly to the pw_load object.
    transmission_level_constant_impedance_load: complex  # [Ohm]  # the average constant impedance load at nominal voltage to be posted directly to the pw_load object.
    average_distribution_load: complex  # [VA]  # The average of the loads on all three phases at the substation object.
    distribution_power_A: complex  # [VA]
    distribution_power_B: complex  # [VA]
    distribution_power_C: complex  # [VA]
    distribution_voltage_A: complex  # [V]
    distribution_voltage_B: complex  # [V]
    distribution_voltage_C: complex  # [V]
    distribution_voltage_AB: complex  # [V]
    distribution_voltage_BC: complex  # [V]
    distribution_voltage_CA: complex  # [V]
    distribution_current_A: complex  # [A]
    distribution_current_B: complex  # [A]
    distribution_current_C: complex  # [A]
    distribution_real_energy: float  # [Wh]


@dataclass
class Transformer(Link):
    configuration: object  # Configuration library used for transformer setup
    climate: object  # climate object used to describe thermal model ambient temperature
    ambient_temperature: float  # [degC]  # ambient temperature in degrees C
    top_oil_hot_spot_temperature: float  # [degC]  # top-oil hottest-spot temperature, degrees C
    winding_hot_spot_temperature: float  # [degC]  # winding hottest-spot temperature, degrees C
    percent_loss_of_life: float  # the percent loss of life
    aging_constant: float  # the aging rate slope for the transformer insulation
    use_thermal_model: bool  # boolean to enable use of thermal model
    transformer_replacement_count: float  # counter of the number times the transformer has been replaced due to lifetime failure
    aging_granularity: float  # [s]  # maximum timestep before updating thermal and aging model in seconds
    phase_A_primary_flux_value: float  # [Wb]  # instantaneous magnetic flux in phase A on the primary side of the transformer during saturation calculations
    phase_B_primary_flux_value: float  # [Wb]  # instantaneous magnetic flux in phase B on the primary side of the transformer during saturation calculations
    phase_C_primary_flux_value: float  # [Wb]  # instantaneous magnetic flux in phase C on the primary side of the transformer during saturation calculations
    phase_A_secondary_flux_value: float  # [Wb]  # instantaneous magnetic flux in phase A on the secondary side of the transformer during saturation calculations
    phase_B_secondary_flux_value: float  # [Wb]  # instantaneous magnetic flux in phase B on the secondary side of the transformer during saturation calculations
    phase_C_secondary_flux_value: float  # [Wb]  # instantaneous magnetic flux in phase C on the secondary side of the transformer during saturation calculations


@unique
class TransformerConfigurationConnectType(IntEnum):
    SINGLE_PHASE_CENTER_TAPPED = 5
    SINGLE_PHASE = 4
    DELTA_GWYE = 3
    DELTA_DELTA = 2
    WYE_WYE = 1
    UNKNOWN = 0


@unique
class TransformerConfigurationInstallType(IntEnum):
    VAULT = 3
    PADMOUNT = 2
    POLETOP = 1
    UNKNOWN = 0


@unique
class TransformerConfigurationCoolantType(IntEnum):
    DRY = 2
    MINERAL_OIL = 1
    UNKNOWN = 0


@unique
class TransformerConfigurationCoolingType(IntEnum):
    DFOW = 6
    DFOA = 5
    NDFOW = 4
    NDFOA = 3
    FA = 2
    OA = 1
    UNKNOWN = 0


@unique
class TransformerConfigurationMagnetizationLocation(IntEnum):
    BOTH = 3
    SECONDARY = 2
    PRIMARY = 1
    NONE = 0


@dataclass
class TransformerConfiguration:
    connect_type: TransformerConfigurationConnectType  # connect type enum: Wye-Wye, single-phase, etc.
    install_type: TransformerConfigurationInstallType  # Defines location of the transformer installation
    coolant_type: TransformerConfigurationCoolantType  # coolant type, used in life time model
    cooling_type: TransformerConfigurationCoolingType  # type of coolant fluid used in life time model
    primary_voltage: float  # [V]  # primary voltage level in L-L value kV
    secondary_voltage: float  # [V]  # secondary voltage level kV
    power_rating: float  # [kVA]  # kVA rating of transformer, total
    powerA_rating: float  # [kVA]  # kVA rating of transformer, phase A
    powerB_rating: float  # [kVA]  # kVA rating of transformer, phase B
    powerC_rating: float  # [kVA]  # kVA rating of transformer, phase C
    resistance: float  # [pu*Ohm]  # Series impedance, pu, real
    reactance: float  # [pu*Ohm]  # Series impedance, pu, imag
    impedance: complex  # [pu*Ohm]  # Series impedance, pu
    resistance1: float  # [pu*Ohm]  # Secondary series impedance (only used when you want to define each individual winding seperately, pu, real
    reactance1: float  # [pu*Ohm]  # Secondary series impedance (only used when you want to define each individual winding seperately, pu, imag
    impedance1: complex  # [pu*Ohm]  # Secondary series impedance (only used when you want to define each individual winding seperately, pu
    resistance2: float  # [pu*Ohm]  # Secondary series impedance (only used when you want to define each individual winding seperately, pu, real
    reactance2: float  # [pu*Ohm]  # Secondary series impedance (only used when you want to define each individual winding seperately, pu, imag
    impedance2: complex  # [pu*Ohm]  # Secondary series impedance (only used when you want to define each individual winding seperately, pu
    shunt_resistance: float  # [pu*Ohm]  # Shunt impedance on primary side, pu, real
    shunt_reactance: float  # [pu*Ohm]  # Shunt impedance on primary side, pu, imag
    shunt_impedance: complex  # [pu*Ohm]  # Shunt impedance on primary side, pu
    core_coil_weight: float  # [lb]  # The weight of the core and coil assembly in pounds
    tank_fittings_weight: float  # [lb]  # The weight of the tank and fittings in pounds
    oil_volume: float  # [gal]  # The number of gallons of oil in the transformer
    rated_winding_time_constant: float  # [h]  # The rated winding time constant in hours
    rated_winding_hot_spot_rise: float  # [degC]  # winding hottest-spot rise over ambient temperature at rated load, degrees C
    rated_top_oil_rise: float  # [degC]  # top-oil hottest-spot rise over ambient temperature at rated load, degrees C
    no_load_loss: float  # [pu]  # Another method of specifying transformer impedances, defined as per unit power values (shunt)
    full_load_loss: float  # [pu]  # Another method of specifying transformer impedances, defined as per unit power values (shunt and series)
    reactance_resistance_ratio: float  # the reactance to resistance ratio (X/R)
    installed_insulation_life: float  # [h]  # the normal lifetime of the transformer insulation at rated load, hours
    magnetization_location: TransformerConfigurationMagnetizationLocation  # winding to place magnetization influence for in-rush calculations
    inrush_saturation_enabled: bool  # flag to include saturation effects during inrush calculations
    L_A: float  # [pu]  # Air core inductance of transformer
    phi_K: float  # [pu]  # Knee flux value where the air core inductance interstes the flux axis of the saturation curve
    phi_M: float  # [pu]  # Peak magnetization flux at rated voltage of the saturation curve
    I_M: float  # [pu]  # Peak magnetization current at rated voltage of the saturation curve
    T_D: float  # Inrush decay time constant for inrush current


@dataclass
class TriplexLine:
    pass


@dataclass
class TriplexLineConductor:
    resistance: float  # [Ohm/mile]  # resistance of cable in ohm/mile
    geometric_mean_radius: float  # [ft]  # geometric mean radius of the cable
    rating_summer_continuous: float  # [A]  # amp ratings for the cable during continuous operation in summer
    rating_summer_emergency: float  # [A]  # amp ratings for the cable during short term operation in summer
    rating_winter_continuous: float  # [A]  # amp ratings for the cable during continuous operation in winter
    rating_winter_emergency: float  # [A]  # amp ratings for the cable during short term operation in winter


@dataclass
class TriplexLineConfiguration:
    conductor_1: object  # conductor type for phase 1
    conductor_2: object  # conductor type for phase 2
    conductor_N: object  # conductor type for phase N
    insulation_thickness: float  # [in]  # thickness of insulation around cabling
    diameter: float  # [in]  # total diameter of cable
    spacing: object  # defines the line spacing configuration
    z11: complex  # [Ohm/mile]  # phase 1 self-impedance, used for direct entry of impedance values
    z12: complex  # [Ohm/mile]  # phase 1-2 induced impedance, used for direct entry of impedance values
    z21: complex  # [Ohm/mile]  # phase 2-1 induced impedance, used for direct entry of impedance values
    z22: complex  # [Ohm/mile]  # phase 2 self-impedance, used for direct entry of impedance values
    rating_summer_continuous: float  # [A]  # amp rating in summer, continuous
    rating_summer_emergency: float  # [A]  # amp rating in summer, short term
    rating_winter_continuous: float  # [A]  # amp rating in winter, continuous
    rating_winter_emergency: float  # [A]  # amp rating in winter, short term


@unique
class TriplexNodeBusType(IntEnum):
    SWING_PQ = 3
    SWING = 2
    PV = 1
    PQ = 0


@unique
class TriplexNodeBusFlag(IntEnum):
    ISSOURCE = 2
    HASSOURCE = 1


@unique
class TriplexNodeServiceStatus(IntEnum):
    OUT_OF_SERVICE = 0
    IN_SERVICE = 1


@dataclass
class TriplexNode(PowerFlowObject):
    bustype: TriplexNodeBusType  # defines whether the node is a PQ, PV, or SWING node
    busflags: List[TriplexNodeBusFlag]  # flag indicates node has a source for voltage, i.e. connects to the swing node
    reference_bus: object  # reference bus from which frequency is defined
    maximum_voltage_error: float  # [V]  # convergence voltage limit or convergence criteria
    voltage_1: complex  # [V]  # bus voltage, phase 1 to ground
    voltage_2: complex  # [V]  # bus voltage, phase 2 to ground
    voltage_N: complex  # [V]  # bus voltage, phase N to ground
    voltage_12: complex  # [V]  # bus voltage, phase 1 to 2
    voltage_1N: complex  # [V]  # bus voltage, phase 1 to N
    voltage_2N: complex  # [V]  # bus voltage, phase 2 to N
    current_1: complex  # [A]  # constant current load on phase 1, also acts as accumulator
    current_2: complex  # [A]  # constant current load on phase 2, also acts as accumulator
    current_N: complex  # [A]  # constant current load on phase N, also acts as accumulator
    current_1_real: float  # [A]  # constant current load on phase 1, real
    current_2_real: float  # [A]  # constant current load on phase 2, real
    current_N_real: float  # [A]  # constant current load on phase N, real
    current_1_reac: float  # [A]  # constant current load on phase 1, imag
    current_2_reac: float  # [A]  # constant current load on phase 2, imag
    current_N_reac: float  # [A]  # constant current load on phase N, imag
    current_12: complex  # [A]  # constant current load on phase 1 to 2
    current_12_real: float  # [A]  # constant current load on phase 1 to 2, real
    current_12_reac: float  # [A]  # constant current load on phase 1 to 2, imag
    power_1: complex  # [VA]  # constant power on phase 1 (120V)
    power_2: complex  # [VA]  # constant power on phase 2 (120V)
    power_12: complex  # [VA]  # constant power on phase 1 to 2 (240V)
    power_1_real: float  # [W]  # constant power on phase 1, real
    power_2_real: float  # [W]  # constant power on phase 2, real
    power_12_real: float  # [W]  # constant power on phase 1 to 2, real
    power_1_reac: float  # [VAr]  # constant power on phase 1, imag
    power_2_reac: float  # [VAr]  # constant power on phase 2, imag
    power_12_reac: float  # [VAr]  # constant power on phase 1 to 2, imag
    shunt_1: complex  # [S]  # constant shunt impedance on phase 1
    shunt_2: complex  # [S]  # constant shunt impedance on phase 2
    shunt_12: complex  # [S]  # constant shunt impedance on phase 1 to 2
    impedance_1: complex  # [Ohm]  # constant series impedance on phase 1
    impedance_2: complex  # [Ohm]  # constant series impedance on phase 2
    impedance_12: complex  # [Ohm]  # constant series impedance on phase 1 to 2
    impedance_1_real: float  # [Ohm]  # constant series impedance on phase 1, real
    impedance_2_real: float  # [Ohm]  # constant series impedance on phase 2, real
    impedance_12_real: float  # [Ohm]  # constant series impedance on phase 1 to 2, real
    impedance_1_reac: float  # [Ohm]  # constant series impedance on phase 1, imag
    impedance_2_reac: float  # [Ohm]  # constant series impedance on phase 2, imag
    impedance_12_reac: float  # [Ohm]  # constant series impedance on phase 1 to 2, imag
    house_present: bool  # boolean for detecting whether a house is attached, not an input
    service_status: TriplexNodeServiceStatus  # In and out of service flag
    service_status_double: float  # In and out of service flag - type float - will indiscriminately override service_status - useful for schedules
    previous_uptime: float  # [min]  # Previous time between disconnects of node in minutes
    current_uptime: float  # [min]  # Current time since last disconnect of node in minutes
    topological_parent: object  # topological parent as per GLM: configuration


@unique
class TriplexLoadLoadClass(IntEnum):
    A = 4
    I = 3
    C = 2
    R = 1
    U = 0


@dataclass
class TriplexLoad(TriplexNode):
    load_class: TriplexLoadLoadClass  # Flag to track load type, not currently used for anything except sorting
    constant_power_1: complex  # [VA]  # constant power load on split phase 1, specified as VA
    constant_power_2: complex  # [VA]  # constant power load on split phase 2, specified as VA
    constant_power_12: complex  # [VA]  # constant power load on split phase 12, specified as VA
    constant_power_1_real: float  # [W]  # constant power load on spit phase 1, real only, specified as W
    constant_power_2_real: float  # [W]  # constant power load on phase 2, real only, specified as W
    constant_power_12_real: float  # [W]  # constant power load on phase 12, real only, specified as W
    constant_power_1_reac: float  # [VAr]  # constant power load on phase 1, imaginary only, specified as VAr
    constant_power_2_reac: float  # [VAr]  # constant power load on phase 2, imaginary only, specified as VAr
    constant_power_12_reac: float  # [VAr]  # constant power load on phase 12, imaginary only, specified as VAr
    constant_current_1: complex  # [A]  # constant current load on phase 1, specified as Amps
    constant_current_2: complex  # [A]  # constant current load on phase 2, specified as Amps
    constant_current_12: complex  # [A]  # constant current load on phase 12, specified as Amps
    constant_current_1_real: float  # [A]  # constant current load on phase 1, real only, specified as Amps
    constant_current_2_real: float  # [A]  # constant current load on phase 2, real only, specified as Amps
    constant_current_12_real: float  # [A]  # constant current load on phase 12, real only, specified as Amps
    constant_current_1_reac: float  # [A]  # constant current load on phase 1, imaginary only, specified as Amps
    constant_current_2_reac: float  # [A]  # constant current load on phase 2, imaginary only, specified as Amps
    constant_current_12_reac: float  # [A]  # constant current load on phase 12, imaginary only, specified as Amps
    constant_impedance_1: complex  # [Ohm]  # constant impedance load on phase 1, specified as Ohms
    constant_impedance_2: complex  # [Ohm]  # constant impedance load on phase 2, specified as Ohms
    constant_impedance_12: complex  # [Ohm]  # constant impedance load on phase 12, specified as Ohms
    constant_impedance_1_real: float  # [Ohm]  # constant impedance load on phase 1, real only, specified as Ohms
    constant_impedance_2_real: float  # [Ohm]  # constant impedance load on phase 2, real only, specified as Ohms
    constant_impedance_12_real: float  # [Ohm]  # constant impedance load on phase 12, real only, specified as Ohms
    constant_impedance_1_reac: float  # [Ohm]  # constant impedance load on phase 1, imaginary only, specified as Ohms
    constant_impedance_2_reac: float  # [Ohm]  # constant impedance load on phase 2, imaginary only, specified as Ohms
    constant_impedance_12_reac: float  # [Ohm]  # constant impedance load on phase 12, imaginary only, specified as Ohms
    measured_voltage_1: complex  # [V]  # measured voltage on phase 1
    measured_voltage_2: complex  # [V]  # measured voltage on phase 2
    measured_voltage_12: complex  # [V]  # measured voltage on phase 12
    base_power_1: float  # [VA]  # in similar format as ZIPload, this represents the nominal power on phase 1 before applying ZIP fractions
    base_power_2: float  # [VA]  # in similar format as ZIPload, this represents the nominal power on phase 2 before applying ZIP fractions
    base_power_12: float  # [VA]  # in similar format as ZIPload, this represents the nominal power on phase 12 before applying ZIP fractions
    power_pf_1: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase 1 constant power portion of load
    current_pf_1: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase 1 constant current portion of load
    impedance_pf_1: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase 1 constant impedance portion of load
    power_pf_2: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase 2 constant power portion of load
    current_pf_2: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase 2 constant current portion of load
    impedance_pf_2: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase 2 constant impedance portion of load
    power_pf_12: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase 12 constant power portion of load
    current_pf_12: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase 12 constant current portion of load
    impedance_pf_12: float  # [pu]  # in similar format as ZIPload, this is the power factor of the phase 12 constant impedance portion of load
    power_fraction_1: float  # [pu]  # this is the constant power fraction of base power on phase 1
    current_fraction_1: float  # [pu]  # this is the constant current fraction of base power on phase 1
    impedance_fraction_1: float  # [pu]  # this is the constant impedance fraction of base power on phase 1
    power_fraction_2: float  # [pu]  # this is the constant power fraction of base power on phase 2
    current_fraction_2: float  # [pu]  # this is the constant current fraction of base power on phase 2
    impedance_fraction_2: float  # [pu]  # this is the constant impedance fraction of base power on phase 2
    power_fraction_12: float  # [pu]  # this is the constant power fraction of base power on phase 12
    current_fraction_12: float  # [pu]  # this is the constant current fraction of base power on phase 12
    impedance_fraction_12: float  # [pu]  # this is the constant impedance fraction of base power on phase 12


@unique
class TriplexMeterBillMode(IntEnum):
    TIERED_RTP = 4
    HOURLY = 3
    TIERED = 2
    UNIFORM = 1
    NONE = 0


@dataclass
class TriplexMeter(TriplexNode):
    measured_real_energy: float  # [Wh]  # metered real energy consumption
    measured_reactive_energy: float  # [VAh]  # metered reactive energy consumption
    measured_power: complex  # [VA]  # metered power
    indiv_measured_power_1: complex  # [VA]  # metered power, phase 1
    indiv_measured_power_2: complex  # [VA]  # metered power, phase 2
    indiv_measured_power_N: complex  # [VA]  # metered power, phase N
    measured_demand: float  # [W]  # metered demand (peak of power)
    measured_real_power: float  # [W]  # metered real power
    measured_reactive_power: float  # [VAr]  # metered reactive power
    meter_power_consumption: complex  # [VA]  # power consumed by meter operation
    measured_voltage_1: complex  # [V]  # measured voltage, phase 1 to ground
    measured_voltage_2: complex  # [V]  # measured voltage, phase 2 to ground
    measured_voltage_N: complex  # [V]  # measured voltage, phase N to ground
    measured_current_1: complex  # [A]  # measured current, phase 1
    measured_current_2: complex  # [A]  # measured current, phase 2
    measured_current_N: complex  # [A]  # measured current, phase N
    customer_interrupted: bool  # Reliability flag - goes active if the customer is in an interrupted state
    customer_interrupted_secondary: bool  # Reliability flag - goes active if the customer is in a secondary interrupted state - i.e., momentary
    monthly_bill: float  # [$]  # Accumulator for the current month's bill
    previous_monthly_bill: float  # [$]  # Total monthly bill for the previous month
    previous_monthly_energy: float  # [kWh]  #
    monthly_fee: float  # [$]  # Total monthly energy for the previous month
    monthly_energy: float  # [kWh]  # Accumulator for the current month's energy
    bill_mode: TriplexMeterBillMode  # Designates the bill mode to be used
    power_market: object  # Designates the auction object where prices are read from for bill mode
    bill_day: int  # Day bill is to be processed (assumed to occur at midnight of that day)
    price: float  # [$/kWh]  # Standard uniform pricing
    price_base: float  # [$/kWh]  # Used only in TIERED_RTP mode to describe the price before the first tier
    first_tier_price: float  # [$/kWh]  # first tier price of energy between first and second tier energy
    first_tier_energy: float  # [kWh]  # price of energy on tier above price or price base
    second_tier_price: float  # [$/kWh]  # first tier price of energy between second and third tier energy
    second_tier_energy: float  # [kWh]  # price of energy on tier above first tier
    third_tier_price: float  # [$/kWh]  # first tier price of energy greater than third tier energy
    third_tier_energy: float  # [kWh]  # price of energy on tier above second tier


@dataclass
class UndergroundLine(Line):
    pass


@dataclass
class UndergroundLineConductor:
    outer_diameter: float  # [in]  # Outer diameter of conductor and sheath
    conductor_gmr: float  # [ft]  # Geometric mean radius of the conductor
    conductor_diameter: float  # [in]  # Diameter of conductor
    conductor_resistance: float  # [Ohm/mile]  # Resistance of conductor in ohm/mile
    neutral_gmr: float  # [ft]  # Geometric mean radius of an individual neutral conductor/strand
    neutral_diameter: float  # [in]  # Diameter of individual neutral conductor/strand of concentric neutral
    neutral_resistance: float  # [Ohm/mile]  # Resistance of an individual neutral conductor/strand in ohm/mile
    neutral_strands: int  # Number of cable strands in neutral conductor
    shield_thickness: float  # [in]  # The thickness of Tape shield in inches
    shield_diameter: float  # [in]  # The outside diameter of Tape shield in inches
    insulation_relative_permitivitty: float  # [unit]  # Permitivitty of insulation, relative to air
    shield_gmr: float  # [ft]  # Geometric mean radius of shielding sheath
    shield_resistance: float  # [Ohm/mile]  # Resistance of shielding sheath in ohms/mile
    rating_summer_continuous: float  # [A]  # amp rating in summer, continuous
    rating_summer_emergency: float  # [A]  # amp rating in summer, short term
    rating_winter_continuous: float  # [A]  # amp rating in winter, continuous
    rating_winter_emergency: float  # [A]  # amp rating in winter, short term


@unique
class VoltVarControlControlMethod(IntEnum):
    STANDBY = 0
    ACTIVE = 1


@unique
class VoltVarControlPhase(IntEnum):
    C = 4
    B = 2
    A = 1


@dataclass
class VoltVarControl:
    control_method: VoltVarControlControlMethod  # IVVC activated or in standby
    capacitor_delay: float  # [s]  # Default capacitor time delay - overridden by local defintions
    regulator_delay: float  # [s]  # Default regulator time delay - overriden by local definitions
    desired_pf: float  # Desired power-factor magnitude at the substation transformer or regulator
    d_max: float  # Scaling constant for capacitor switching on - typically 0.3 - 0.6
    d_min: float  # Scaling constant for capacitor switching off - typically 0.1 - 0.4
    substation_link: object  # Substation link, transformer, or regulator to measure power factor
    pf_phase: List[VoltVarControlPhase]  # Phase to include in power factor monitoring
    regulator_list: str  # List of voltage regulators for the system, separated by commas
    capacitor_list: str  # List of controllable capacitors on the system separated by commas
    voltage_measurements: str  # List of voltage measurement devices, separated by commas
    minimum_voltages: str  # Minimum voltages allowed for feeder, separated by commas
    maximum_voltages: str  # Maximum voltages allowed for feeder, separated by commas
    desired_voltages: str  # Desired operating voltages for the regulators, separated by commas
    max_vdrop: str  # Maximum voltage drop between feeder and end measurements for each regulator, separated by commas
    high_load_deadband: str  # High loading case voltage deadband for each regulator, separated by commas
    low_load_deadband: str  # Low loading case voltage deadband for each regulator, separated by commas
    pf_signed: bool  # Set to true to consider the sign on the power factor.  Otherwise, it just maintains the deadband of +/-desired_pf


@unique
class VoltDumpMode(IntEnum):
    polar = 1
    rect = 0


@dataclass
class VoltDump:
    group: str  # the group ID to output data for (all nodes if empty)
    runtime: timestamp  # the time to check voltage data
    filename: str  # the file to dump the voltage data into
    file: str  # the file to dump the voltage data into
    runcount: int  # the number of times the file has been written to
    mode: VoltDumpMode  # dumps the voltages in either polar or rectangular notation
