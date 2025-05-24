class_name HungarComponent
extends Node

@export var hunger_state: HungerState

func _ready() -> void:
	if not hunger_state:
		hunger_state = HungerState.new()

func _process(delta: float) -> void:
	hunger_state.tick(delta)

func feed():
	hunger_state.feed()
