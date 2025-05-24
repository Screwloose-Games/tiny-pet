class_name ClickableStaticBody3D
extends StaticBody3D

signal clicked

@export var hover_cursor: Texture2D
@export var cursor_hotspot: Vector2 = Vector2(12, 12)
@export var hover_delay: float = 0.1

var hover_delay_timer: Timer = Timer.new()


func _ready() -> void:
	add_child(hover_delay_timer)
	hover_delay_timer.one_shot = true
	hover_delay_timer.timeout.connect(func(): Input.set_custom_mouse_cursor(null))


func _mouse_enter() -> void:
	hover_delay_timer.stop()
	if hover_cursor:
		Input.set_custom_mouse_cursor(hover_cursor, Input.CURSOR_ARROW, cursor_hotspot)


func _mouse_exit() -> void:
	hover_delay_timer.start(hover_delay)


func _input_event(
	_camera: Node, event: InputEvent, _position: Vector3, _normal: Vector3, _shape_idx: int
) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		clicked.emit()
