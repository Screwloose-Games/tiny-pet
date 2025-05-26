class_name HungarComponent
extends Node

signal was_fed

@onready var hunger_state: HungerState = GameState.game_state.hunger_state:
	get:
		return GameState.game_state.hunger_state


func _ready() -> void:
	if not hunger_state:
		hunger_state = HungerState.new()


func _process(delta: float) -> void:
	hunger_state.tick(delta)


func feed():
	was_fed.emit()
	hunger_state.feed()
