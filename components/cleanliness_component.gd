class_name CleanlinessComponent
extends Node

@onready var cleanliness_state: CleanlinessState = GameState.game_state.cleanliness_state:
	get:
		return GameState.game_state.cleanliness_state


func poop(poo: Poop):
	if cleanliness_state:
		cleanliness_state.poop(poo)


func _ready() -> void:
	if not cleanliness_state:
		cleanliness_state = CleanlinessState.new()


func _process(delta: float) -> void:
	cleanliness_state.tick(delta)

func is_unclean():
	return cleanliness_state.is_unclean()
