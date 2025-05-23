class_name LifecycleComponent
extends Node

@export var lifecycle_state: LifecycleState
@export var hunger_component: Node
@export var social_component: Node
@export var cleanliness_component: Node

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	if not lifecycle_state:
		lifecycle_state = LifecycleState.new()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	lifecycle_state.tick(delta)
