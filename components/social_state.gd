class_name SocialState
extends Resource

signal state_changed(new_state: State)

enum State {
	LOVED,
	LONELY,
	ABANDONED
}

# Current value
@export_range(0, 1, .01) var social_meter: float = 1.0:
	set(value):
		social_meter = clamp(value, 0.0, 1.0)
		social_state = get_social_state(value)

# Rate of change
@export_range(0, 1, .01) var social_down_rate: float = 0.01 # per second

# State thresholds
@export_range(0, 1, .01) var loved_threshold: float = 0.5
@export_range(0, 1, .01) var lonely_threshold: float = 0.3
@export_range(0, 1, .01) var pet_socialization_amount: float = 0.5

var social_state: State = State.LOVED:
	set(value):
		if value != social_state:
			social_state = value
			state_changed.emit(value)

func get_social_state(value: float) -> State:
	if value >= loved_threshold:
		return State.LOVED
	if value >= lonely_threshold:
		return State.LONELY
	return State.ABANDONED

# Call every frame
func tick(delta: float) -> void:
	social_meter -= social_down_rate * delta
	#print("Social meter: ", social_meter)

func pet():
	GlobalSignalBus.creature_petted.emit()
	socialize(pet_socialization_amount)

func socialize(amount: float) -> void:
	social_meter += amount
