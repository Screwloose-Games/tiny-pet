extends Node3D

@export var ray_length: float = 1000.0

var dragging_collider
var do_drag: bool = false
var mouse_position: Vector2

func _process(_delta: float) -> void:
	if dragging_collider:
		dragging_collider.global_position = mouse_position


func _input(event: InputEvent) -> void:
	var intersect = get_mouse_intersect(event.position)
	if event is InputEventMouse:
		if intersect:
			mouse_position = intersect.position

	if event is InputEventMouseButton:
		var left_pressed: bool = event.button_index == MOUSE_BUTTON_LEFT && event.pressed
		var left_released: bool = event.button_index == MOUSE_BUTTON_LEFT && !event.pressed

		if left_released:
			do_drag = false
			drag_and_drop(intersect)

		elif left_pressed:
			do_drag = true
			drag_and_drop(intersect)

func drag_and_drop(intersect: Dictionary) -> void:
	if !dragging_collider and do_drag:
		if intersect.has("collider"):
			dragging_collider = intersect.collider
			dragging_collider.set_collision_layer(0)  # disable collisions
	elif dragging_collider:
		dragging_collider.set_collision_layer(1)  # restore collisions
		dragging_collider = null

func get_mouse_intersect(mouse_pos: Vector2) -> Dictionary:
	var cam = get_viewport().get_camera_3d()
	var params = PhysicsRayQueryParameters3D.new()
	params.from = cam.project_ray_origin(mouse_pos)
	params.to = cam.project_position(mouse_pos, ray_length)
	var worldspace = get_world_3d().direct_space_state
	return worldspace.intersect_ray(params)
