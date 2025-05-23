class_name CleanlinessComponent
extends Node

@export var cleanliness_state: CleanlinessState

func poop(poop: Poop):
	if cleanliness_state:
		cleanliness_state.poop(poop)

func _ready() -> void:
	if not cleanliness_state:
		cleanliness_state = CleanlinessState.new()

func _process(delta: float) -> void:
	cleanliness_state.tick(delta) 
