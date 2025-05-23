## Listens to status of hungar, social, cleanliness
## Tracks what states are warning state and what states are debuff states.
## For debuff states, has configurable debuff effects
## for each game tick, if there is some debuff effect, apply the debuff effect to the lifecycle component
class_name StatusDebuffSystem
extends Node

# References to state components
@export var hunger_state: HungerState
@export var cleanliness_state: CleanlinessState
@export var social_state: SocialState
@export var lifecycle_state: LifecycleState

# Debuff amounts per second (in years)
@export_range(0, 1, 0.1) var filthy_debuff: float = 0.1
@export_range(0, 1, 0.1) var overfed_debuff: float = 0.1
@export_range(0, 5, 0.1) var starving_debuff: float = 1
@export_range(0, 1, 0.1) var lonely_debuff: float = 0.1
@export_range(0, 5, 0.1) var abandoned_debuff: float = 0.5

func _ready() -> void:
	# Connect to state change signals
	if hunger_state:
		hunger_state.state_changed.connect(_on_hunger_state_changed)
	if cleanliness_state:
		cleanliness_state.state_changed.connect(_on_cleanliness_state_changed)
	if social_state:
		social_state.state_changed.connect(_on_social_state_changed)

func _process(delta: float) -> void:
	if not lifecycle_state or lifecycle_state.is_dead:
		return
	_apply_debuffs(delta)

func _apply_debuffs(delta: float) -> void:
	if not lifecycle_state:
		return
	_apply_hunger_debuffs(delta)
	_apply_cleanliness_debuffs(delta)
	_apply_social_debuffs(delta)

func _apply_hunger_debuffs(delta: float) -> void:
	if not hunger_state:
		return
	match hunger_state.fed_state:
		HungerState.FedState.OVERFED:
			lifecycle_state.reduce_life_span(overfed_debuff * delta)
		HungerState.FedState.STARVING:
			lifecycle_state.reduce_life_span(starving_debuff * delta)

func _apply_cleanliness_debuffs(delta: float) -> void:
	if not cleanliness_state:
		return
	match cleanliness_state.clean_state:
		CleanlinessState.CleanState.FILTHY:
			lifecycle_state.reduce_life_span(filthy_debuff * delta)

func _apply_social_debuffs(delta: float) -> void:
	if not social_state:
		return
	match social_state.social_state:
		SocialState.State.ABANDONED:
			lifecycle_state.reduce_life_span(abandoned_debuff * delta)
		SocialState.State.LONELY:
			lifecycle_state.reduce_life_span(lonely_debuff * delta)

func _on_hunger_state_changed(_new_state: HungerState.FedState) -> void:
	# Could add additional logic here if needed when hunger state changes
	pass

func _on_cleanliness_state_changed(_new_state: CleanlinessState.CleanState) -> void:
	# Could add additional logic here if needed when cleanliness state changes
	pass

func _on_social_state_changed(_new_state: SocialState.State) -> void:
	# Could add additional logic here if needed when social state changes
	pass
