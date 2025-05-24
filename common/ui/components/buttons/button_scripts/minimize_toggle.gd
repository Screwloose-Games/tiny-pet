extends Button

@export var maxmimize_icon: Texture2D
@export var minimize_icon: Texture2D

var _is_minimized: bool = true


func _ready() -> void:
	button_pressed = true
	toggled.connect(_on_toggled)
	_on_toggled(_is_minimized)


func _on_toggled(is_minimized: bool):
	_is_minimized = is_minimized
	var screen_id = DisplayServer.window_get_current_screen()
	if is_minimized:
		var new_size = Vector2i(400, 300)
		get_window().size = new_size
		await get_tree().process_frame
		var current_window = DisplayServer.get_window_at_screen_position(get_local_mouse_position())
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED, current_window)
		DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_RESIZE_DISABLED, false)
		#DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, false)
		DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, true)

		# move to the bottom right corner of the screen
		var screen_size = DisplayServer.screen_get_size(screen_id)
		get_window().position = screen_size - new_size
		DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_TRANSPARENT, true)
		icon = minimize_icon
		get_window().size = new_size

	else:
		# maximize screen
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN, screen_id)
		DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_RESIZE_DISABLED, false)
		DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, true)
		DisplayServer.window_set_size(
			DisplayServer.screen_get_size(DisplayServer.window_get_current_screen())
		)
		DisplayServer.window_set_position(Vector2.ZERO)
		DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_TRANSPARENT, false)
		icon = maxmimize_icon
