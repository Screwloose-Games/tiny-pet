extends Button

func _ready() -> void:
	pressed.connect(func(): GameState.reset_game_state_to_default())
