extends Node

# Save game to user data
@export_file("*.tres") var save_file: String = "user://saved_game_state.tres"

@export var default_game_state: GameStateResource
@export var autosave: bool = true
@export var autosave_interval_seconds: int = 5

var game_state: GameStateResource
var saved_game_state: GameStateResource
var _autosave_timer: Timer

@onready var save_button: Button = %SaveButton
@onready var load_button: Button = %LoadButton
@onready var reset_button: Button = %ResetButton


func _init() -> void:
	load_game_state()

func _enter_tree() -> void:
	if autosave:
		_autosave_timer = Timer.new()
		_autosave_timer.wait_time = autosave_interval_seconds
		_autosave_timer.autostart = true
		_autosave_timer.one_shot = false
		_autosave_timer.timeout.connect(save_game_state)
		add_child(_autosave_timer)


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	# Connect the button signals to the respective functions
	save_button.pressed.connect(save_game_state)
	load_button.pressed.connect(load_saved_game_state)
	reset_button.pressed.connect(reset_game_state_to_default)

func load_game_state() -> void:
	if ResourceLoader.exists(save_file):
		game_state = ResourceLoader.load(save_file)
	else:
		game_state = default_game_state.duplicate()

func load_saved_game_state() -> void:
	var loaded_state = ResourceLoader.load(save_file, "", ResourceLoader.CACHE_MODE_REPLACE_DEEP)
	if loaded_state:
		game_state = loaded_state.duplicate()

func save_game_state():
	if game_state == null:
		return
	ResourceSaver.save(game_state, save_file)
	print("Game state saved to: ", save_file)

func reset_game_state_to_default():
	ResourceLoader.load(default_game_state.resource_path, "", ResourceLoader.CACHE_MODE_REPLACE_DEEP)
	game_state = default_game_state.duplicate(true)
	save_game_state()
	get_tree().reload_current_scene()

func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		save_game_state()
		get_tree().quit()
