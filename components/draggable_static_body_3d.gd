class_name DraggableStaticBody3D
extends StaticBody3D

signal clicked
signal drag_started
signal drag_ended

const DROP_COLLISION_LAYER = 1 << 8

static var is_being_dragged: bool = false
static var dragged_object: Node3D

# bitwise layer 9

@export var ray_length: float = 3000
@export var duplicate_on_drag: bool = true

var world_intersect_position: Vector3
var ignore_colliders: Array[CollisionObject3D] = []

func _ready() -> void:
	pass

func _process(_delta: float) -> void:
	if is_being_dragged:
		var ray_intersect: Dictionary = get_mouse_intersect(get_viewport().get_mouse_position())
		if ray_intersect:
			world_intersect_position = ray_intersect.position
		dragged_object.global_position = world_intersect_position

func _start_drag():
	if duplicate_on_drag:
		dragged_object = owner.duplicate()
		owner.add_sibling(dragged_object)
		dragged_object.tree_exited.connect(func(): is_being_dragged = false)
	else:
		dragged_object = owner
	is_being_dragged = true
	# get alll collision object 3d children of the dragged object:
	var col_children = dragged_object.find_children("*", "CollisionObject3D")
	ignore_colliders.clear()
	ignore_colliders.append_array(col_children)
	for child in col_children:
		child.tree_exited.connect(func(): ignore_colliders.erase(child))

func _stop_drag():
	is_being_dragged = false
	drag_ended.emit()
	_handle_drop()

func _handle_drop():
	var drop_area_collision: Dictionary = get_mouse_intersect(get_viewport().get_mouse_position(), true)
	var collider = drop_area_collision.get("collider")
	if collider is DroppableStaticBody3D:
		collider.drop(self)
		owner.queue_free.call_deferred()
	else:
		handle_not_droppable()

func get_object_to_drop():
	return owner

func handle_not_droppable():
	owner.queue_free.call_deferred()

func _input_event(_camera: Node, event: InputEvent, _position: Vector3, _normal: Vector3, _shape_idx: int) -> void:
	if event is InputEventMouse:
		var ray_intersect: Dictionary = get_mouse_intersect(event.position)
		if ray_intersect:
			world_intersect_position = ray_intersect.position
			print(world_intersect_position)
	if event is InputEventMouseButton:
		var left_button_pressed = event.button_index == MOUSE_BUTTON_LEFT && event.pressed
		var left_button_released = event.button_index == MOUSE_BUTTON_LEFT && !event.pressed
		if left_button_released and is_being_dragged:
			_stop_drag()
		elif left_button_pressed:
			_start_drag()

func get_mouse_intersect(mouse_pos: Vector2, drop_only: bool = false) -> Dictionary:
	var cam = get_viewport().get_camera_3d()
	var params = PhysicsRayQueryParameters3D.new()
	params.from = cam.project_ray_origin(mouse_pos)
	print("ray origin: ", params.from)
	params.to = cam.project_position(mouse_pos, ray_length)
	print("ray origin: ", params.from)
	# get all collision shapes that are children of
	var to_ignore = [self]
	to_ignore.append_array(ignore_colliders)
	if drop_only:
		params.collision_mask = DROP_COLLISION_LAYER
	params.exclude = to_ignore
	var worldspace = get_world_3d().direct_space_state
	return worldspace.intersect_ray(params)
