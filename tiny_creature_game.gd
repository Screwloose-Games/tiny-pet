extends Node3D

const TARGET_SIZE := Vector2i(400, 300)

func _ready():


	# 4. Make it stay put.
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, true)
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_RESIZE_DISABLED, true)
	var viewport = get_viewport()
	viewport.transparent_bg = true
	viewport.set_transparent_background(true)
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_TRANSPARENT, true)
	DisplayServer.window_set_size(TARGET_SIZE)

	# 2. Work out the bottom-right corner of the current screen.
	var screen_id := DisplayServer.window_get_current_screen()
	var screen_size := DisplayServer.screen_get_size(screen_id)
	var target_pos := screen_size - TARGET_SIZE              # bottom-right pixel

	# 3. Move the window there.
	DisplayServer.window_set_position(target_pos)
	await get_tree().process_frame
	print(viewport.transparent_bg)
