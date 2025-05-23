class_name CleanlinessState
extends Resource

signal state_changed(new_state: CleanState)

enum CleanState {
	CLEAN,
	DIRTY,
	FILTHY
}

# Current value
@export_range(0, 1, .01) var cleanliness: float = 1:
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

var poops: Array[Node]

func poop(poo: Poop):
	poops.append(poo)
	poo.tree_exited.connect(_on_poop_exited_scene.bind(poo))

func _on_poop_exited_scene(poo: Poop):
	poops.erase(poo)
	if poops.size() == 0:
		clean_completely()

func get_clean_state(value: float) -> CleanState:
	if value >= clean_threshold:
		return CleanState.CLEAN
	if value >= dirty_threshold:
		return CleanState.DIRTY
	return CleanState.FILTHY

func tick(delta: float) -> void:
	if poops.size() > 0:
		cleanliness -= cleanliness_down_rate * delta
		print("Cleanliness meter: ", cleanliness)

func clean(amount: float) -> void:
	cleanliness += amount

func clean_completely() -> void:
	cleanliness = 1
