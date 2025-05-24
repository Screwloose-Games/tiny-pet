class_name GameStateResource
extends Resource

@export var default_hunger_state: HungerState
@export var default_cleanliness_state: CleanlinessState
@export var default_social_state: SocialState
@export var default_lifecycle_state: LifecycleState

var current_hunger_state: HungerState
var current_cleanliness_state: CleanlinessState
var current_social_state: SocialState
var current_lifecycle_state: LifecycleState

#func _init() -> void:
	#current_hunger_state = default_hunger_state.duplicate()
	#current_cleanliness_state = default_cleanliness_state.duplicate()
	#current_social_state = default_social_state.duplicate()
	#current_lifecycle_state = default_lifecycle_state.duplicate()
