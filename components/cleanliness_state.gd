class_name CleanlinessState
extends Resource

signal state_changed(new_state: CleanState)

enum CleanState {
	CLEAN,
	DIRTY,
	FILTHY
}

# Current value
@export_range(0, 1, .01) var cleanliness: float = 0.7:
	set(value):
		cleanliness = clamp(value, 0.0, 1.0)
		clean_state = get_clean_state(value)

# Rate of change
@export_range(0, 1, .01) var cleanliness_down_rate: float = 0.01 # per second
@export_range(0, 1, .01) var poop_cleanliness_down_rate: float = 0.05 # per second when pooping

# State thresholds
@export_range(0, 1, .01) var clean_threshold: float = 0.7
@export_range(0, 1, .01) var dirty_threshold: float = 0.4

var clean_state: CleanState = CleanState.CLEAN:
	set(value):
		if value != clean_state:
			clean_state = value
			state_changed.emit(value)
var is_pooping: bool = false

func get_clean_state(value: float) -> CleanState:
	if value >= clean_threshold:
		return CleanState.CLEAN
	if value >= dirty_threshold:
		return CleanState.DIRTY
	return CleanState.FILTHY

# Call every frame
func tick(delta: float) -> void:
	cleanliness -= cleanliness_down_rate * delta

func clean(amount: float) -> void:
	cleanliness += amount
