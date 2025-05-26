extends Node

signal pet_finished
signal finished_eating

enum CreatureState {
	EATING,
	IDLE,
	WALKING,
	HUNGER_FULL,
	HUNGER_HUNGRY,
	POOPING,
	PETTED,
	LONELY,
	ABANDONED,
}

const STATE_NAMES := {
	CreatureState.EATING: "EATING",
	CreatureState.IDLE: "IDLE",
	CreatureState.WALKING: "WALKING",
	CreatureState.HUNGER_FULL: "HUNGER_FULL",
	CreatureState.HUNGER_HUNGRY: "HUNGER_HUNGRY",
	CreatureState.POOPING: "POOPING",
	CreatureState.PETTED: "PETTED",
	CreatureState.LONELY: "LONELY",
	CreatureState.ABANDONED: "ABANDONED",
}

var state: CreatureState = CreatureState.IDLE:
	set(val):
		if state != val:
			state = val
			print("State changed to: %s" % STATE_NAMES.get(val, str(val)))

@onready var prefab_creature: Node3D = $".."
@onready var hunger_component: HungarComponent = %HungerComponent
@onready var social_component: SocialComponent = %SocialComponent
@onready var cleanliness_component: CleanlinessComponent = %CleanlinessComponent
@onready var lifecycle_component: LifecycleComponent = %LifecycleComponent
@onready var animation_tree: AnimationTree = %AnimationTree
@onready var animation_player: AnimationPlayer = $"../Model/AnimationPlayer"

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	prefab_creature.pooped.connect(_on_pooped)
	hunger_component.hunger_state.state_changed.connect(_on_hunger_state_changed)
	hunger_component.was_fed.connect(on_started_eating)
	social_component.social_state.state_changed.connect(_on_social_state_changed)
	social_component.petted.connect(_on_creature_petted)
	cleanliness_component.cleanliness_state.state_changed.connect(_on_clean_state_changed)
	lifecycle_component.lifecycle_state.lifecycle_state_changed.connect(_on_lifecycle_state_changed)
	animation_tree.animation_finished.connect(_on_animation_finished)
	# TODO: Connect to movement event for WALKING state if available

func _on_hunger_state_changed(new_state: HungerState.FedState):
	if new_state == HungerState.FedState.OVERFED:
		state = CreatureState.HUNGER_FULL
	elif new_state == HungerState.FedState.HUNGRY or new_state == HungerState.FedState.STARVING:
		state = CreatureState.HUNGER_HUNGRY
	elif new_state == HungerState.FedState.FULL:
		state = CreatureState.IDLE

func _on_social_state_changed(new_state: SocialState.State):
	if new_state == SocialState.State.LOVED:
		# If just petted, handled by _on_creature_petted
		pass
	elif new_state == SocialState.State.LONELY:
		state = CreatureState.LONELY
	elif new_state == SocialState.State.ABANDONED:
		state = CreatureState.ABANDONED

func _on_clean_state_changed(new_state: CleanlinessState.CleanState):
	if new_state == CleanlinessState.CleanState.FILTHY:
		state = CreatureState.IDLE  # Or a custom state if you add one for dirty/filthy

func _on_lifecycle_state_changed(new_state: LifecycleState.LifeState):
	if new_state == LifecycleState.LifeState.DEAD:
		state = CreatureState.IDLE  # Or a custom state if you add one for dead

func _on_pooped():
	state = CreatureState.POOPING

func _on_animation_finished(anim_name: StringName):
	match anim_name:
		"pet":
			pet_finished.emit()
		"eat":
			finished_eating.emit()

func _on_creature_petted():
	state = CreatureState.PETTED
	
	await pet_finished
	state = CreatureState.IDLE
	#await animation_tree.animation_started("idle")

# Placeholder for movement event
func on_started_walking():
	state = CreatureState.WALKING

func on_started_eating():
	await get_tree().process_frame
	if hunger_component.hunger_state.fed_state == HungerState.FedState.OVERFED:
		#animation_player.play("full")
		state = CreatureState.HUNGER_FULL
		
		pass
	else:
		#animation_player.play("eat")
		state = CreatureState.EATING
	await get_tree().process_frame
	#await get_tree().create_timer(0.1).timeout
	state = CreatureState.IDLE
	#await finished_eating
	#if hunger_component.hunger_state.fed_state == HungerState.FedState.OVERFED:
		#state = CreatureState.HUNGER_FULL
		#pass
	#else:
		#state = CreatureState.IDLE

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta: float) -> void:
	#if state != CreatureState.IDLE:
		#state = CreatureState.IDLE
	pass
