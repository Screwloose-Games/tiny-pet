class_name SocialComponent
extends Node

signal petted

@onready var social_state: SocialState = GameState.game_state.social_state:
	get:
		return GameState.game_state.social_state


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	if not social_state:
		social_state = SocialState.new()


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	social_state.tick(delta)


func pet():
	petted.emit()
	social_state.pet()
