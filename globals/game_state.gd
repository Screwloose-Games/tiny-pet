extends Node

# Save game to user data
@export_file("*.tres") var save_file: String = "user://saved_game_state.tres"

@export var default_game_state: GameStateResource
var game_state: GameStateResource

var saved_game_state: GameStateResource

@onready var save_button: Button = %SaveButton
@onready var load_button: Button = %LoadButton
@onready var reset_button: Button = %ResetButton
# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	# Connect the button signals to the respective functions
	save_button.pressed.connect(save_game_state)
	load_button.pressed.connect(load_saved_game_state)
	reset_button.pressed.connect(reset_game_state_to_default)
	load_game_state()


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
	ResourceSaver.save(game_state, save_file, ResourceSaver.FLAG_REPLACE_SUBRESOURCE_PATHS)

func reset_game_state_to_default():
	ResourceLoader.load(default_game_state.resource_path, "", ResourceLoader.CACHE_MODE_REPLACE_DEEP)
	game_state = default_game_state.duplicate()
	save_game_state()
