class_name LifecycleComponent
extends Node

@export var lifecycle_state: LifecycleState

var is_dead: bool:
	get:
		if lifecycle_state:
			return lifecycle_state.is_dead
		return true

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	if not lifecycle_state:
		lifecycle_state = LifecycleState.new()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	lifecycle_state.tick(delta)
