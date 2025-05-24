class_name CreatureStatusIndicator
extends Sprite3D

@export var hunger_state_indicators: Dictionary[HungerState.FedState, Texture2D] = {}
@export var cleanliness_state_indicators: Dictionary[CleanlinessState.CleanState, Texture2D] = {}
@export var social_state_indicators: Dictionary[SocialState.State, Texture2D] = {}
@export var lifecycle_state_indicators: Dictionary[LifecycleState.LifeState, Texture2D] = {}

@export var state_indication_duration: float = 2.0

var current_states_to_indicate: Dictionary = {}
var current_state_index: int = 0
var state_timer: float = 0.0
var should_display: bool = false
var time_since_display_change: float = 0
var time_per_display: float = 0.5

@onready var hunger_state: HungerState = GameState.game_state.hunger_state:
	get:
		return GameState.game_state.hunger_state
@onready var social_state: SocialState = GameState.game_state.social_state:
	get:
		return GameState.game_state.social_state
@onready var cleanliness_state: CleanlinessState = GameState.game_state.cleanliness_state:
	get:
		return GameState.game_state.cleanliness_state
@onready var lifecycle_state: LifecycleState = GameState.game_state.lifecycle_state:
	get:
		return GameState.game_state.lifecycle_state

func _ready() -> void:
	# Connect to state change signals
	if hunger_state:
		hunger_state.state_changed.connect(_on_hunger_state_changed)
	if cleanliness_state:
		cleanliness_state.state_changed.connect(_on_cleanliness_state_changed)
	if social_state:
		social_state.state_changed.connect(_on_social_state_changed)
	if lifecycle_state:
		lifecycle_state.lifecycle_state_changed.connect(_on_lifecycle_state_changed)
	_update_states_to_indicate()


func handle_blink_display(delta: float):
	time_since_display_change += delta
	if time_since_display_change > time_per_display:
		time_since_display_change = 0
		visible = !visible


func _handle_dead():
	if lifecycle_state_indicators.has(LifecycleState.LifeState.DEAD):
		current_states_to_indicate[lifecycle_state] = lifecycle_state_indicators[
			LifecycleState.LifeState.DEAD
		]
		_update_current_indicator()


func _process(delta: float) -> void:
	if lifecycle_state and lifecycle_state.is_dead:
		return _handle_dead()
	if current_states_to_indicate.is_empty():
		texture = null
		visible = false
		return

	state_timer += delta
	handle_blink_display(delta)
	if state_timer >= state_indication_duration:
		state_timer = 0.0
		time_since_display_change = 0
		current_state_index = (current_state_index + 1) % current_states_to_indicate.size()
		_update_current_indicator()


func _update_states_to_indicate() -> void:
	current_states_to_indicate.clear()
	if lifecycle_state and lifecycle_state.is_dead:
		return _handle_dead()

	# Add other states if they have indicators
	if hunger_state and hunger_state_indicators.has(hunger_state.fed_state):
		current_states_to_indicate[hunger_state] = hunger_state_indicators[hunger_state.fed_state]

	if cleanliness_state and cleanliness_state_indicators.has(cleanliness_state.clean_state):
		current_states_to_indicate[cleanliness_state] = cleanliness_state_indicators[
			cleanliness_state.clean_state
		]

	if social_state and social_state_indicators.has(social_state.social_state):
		current_states_to_indicate[social_state] = social_state_indicators[
			social_state.social_state
		]

	if lifecycle_state and lifecycle_state_indicators.has(lifecycle_state.life_state):
		current_states_to_indicate[lifecycle_state] = lifecycle_state_indicators[
			lifecycle_state.life_state
		]

	_update_current_indicator()


func _update_current_indicator() -> void:
	var states = current_states_to_indicate.values()
	if current_states_to_indicate.is_empty() or current_state_index >= states.size():
		texture = null
		visible = false
		return

	texture = states[current_state_index]
	visible = true
	#print("Hunger state: ", hunger_state.fed_state, "Hunger value: ", hunger_state.fullness)
	#print(
		#"Cleanliness state: ",
		#cleanliness_state.clean_state,
		#"Cleanliness value: ",
		#cleanliness_state.cleanliness
	#)
	#print("Social state: ", social_state.social_state, "Social value: ", social_state.social_meter)
	#print(
		#"Lifecycle state: ",
		#lifecycle_state.life_state,
		#"Lifecycle value: ",
		#lifecycle_state.current_age
	#)


func _on_hunger_state_changed(_new_state: HungerState.FedState) -> void:
	_update_states_to_indicate()


func _on_cleanliness_state_changed(_new_state: CleanlinessState.CleanState) -> void:
	_update_states_to_indicate()


func _on_social_state_changed(_new_state: SocialState.State) -> void:
	_update_states_to_indicate()


func _on_lifecycle_state_changed(_new_state: LifecycleState.LifeState) -> void:
	_update_states_to_indicate()
