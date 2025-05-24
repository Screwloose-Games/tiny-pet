class_name LevelState
# This script is used to manage the state of the level in the game.
extends Node

@export var lifecycle_state: LifecycleState
@export var hunger_state: HungerState
@export var cleanliness_state: CleanlinessState
@export var social_state: SocialState


func reset_level_state() -> void:
	# Reset the game state to its initial values.
	lifecycle_state.reset_state()
	hunger_state.reset_state()
	cleanliness_state.reset_state()
	social_state.reset_state()

func _ready() -> void:
	reset_level_state()
