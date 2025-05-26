class_name HungerState
extends Resource

signal state_changed(new_state: FedState)
signal was_overfed

enum FedState { OVERFED, FULL, HUNGRY, STARVING }

# Current value
@export_range(0, 1, .01) var fullness: float = 0.7:
	set(value):
		fullness = clamp(value, 0.0, 1.0)
		fed_state = get_fed_state(value)

# Rate of change
@export_range(0, 1, .01) var fullness_down_rate: float = 0.01  # per second

# State thresholds
@export_range(0, 1, .01) var overfed_threshold: float = 0.7
@export_range(0, 1, .01) var full_threshold: float = 0.5
@export_range(0, 1, .01) var hungry_threshold: float = 0.3
@export_range(0, 1, .01) var food_per_feed_action: float = 0.1

var save_location: String = ""

var fed_state: FedState = FedState.FULL:
	set(value):
		if value != fed_state:
			fed_state = value
			state_changed.emit(value)


func get_fed_state(value: float) -> FedState:
	if value > overfed_threshold:
		return FedState.OVERFED
	if value >= full_threshold:
		return FedState.FULL
	if value >= hungry_threshold:
		return FedState.HUNGRY
	return FedState.STARVING


# Call every frame
func tick(delta: float) -> void:
	fullness -= fullness_down_rate * delta


func feed(amount: float = food_per_feed_action) -> void:
	fullness += amount


func save():
	ResourceSaver.save(self, save_location)


func load_saved():
	load(save_location)


func update_from(other):
	for property in other.get_property_list():
		self[property.name] = other[property.name]
