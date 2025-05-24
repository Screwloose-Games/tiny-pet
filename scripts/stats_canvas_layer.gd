extends CanvasLayer

@onready var lifecycle_state: LifecycleState = GameState.game_state.lifecycle_state:
	get:
		return GameState.game_state.lifecycle_state

@onready var creature_age_value_label: Label = %CreatureAgeValueLabel
@onready var restart_button: Button = %RestartButton

func _ready() -> void:
	lifecycle_state.lifecycle_state_changed.connect(_on_life_state_changed)
	restart_button.pressed.connect(_on_restart_button_pressed)
	hide()

func _on_restart_button_pressed():
	GameState.reset_game_state_to_default()

func _on_life_state_changed(life_state: LifecycleState.LifeState):
	if life_state == LifecycleState.LifeState.DEAD:
		show()

func _process(delta: float) -> void:
	creature_age_value_label.text = str(int(lifecycle_state.current_age))
