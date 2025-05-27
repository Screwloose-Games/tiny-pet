extends Node

@export var mouse_sensitivity: float = 0.1

@export var min_pitch: float = -90
@export var max_pitch: float = 15

@export var min_yaw: float = 0
@export var max_yaw: float = 360

@onready var creature_phantom_camera_3d: PhantomCamera3D = %CreaturePhantomCamera3D


func _unhandled_input(event: InputEvent) -> void:
	if (
		creature_phantom_camera_3d.get_follow_mode()
		== creature_phantom_camera_3d.FollowMode.THIRD_PERSON
	):
		var active_pcam: PhantomCamera3D
		active_pcam = creature_phantom_camera_3d
		_set_pcam_rotation(creature_phantom_camera_3d, event)


func _set_pcam_rotation(pcam: PhantomCamera3D, event: InputEvent) -> void:
	if Input.is_action_just_released("MoveCamera"):
		Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

	if Input.is_action_pressed("MoveCamera"):
		if (
			creature_phantom_camera_3d.get_follow_mode()
			== creature_phantom_camera_3d.FollowMode.THIRD_PERSON
		):
			Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
		if event is InputEventMouseMotion:
			var pcam_rotation_degrees: Vector3
			pcam_rotation_degrees = pcam.get_third_person_rotation_degrees()
			pcam_rotation_degrees.x -= event.relative.y * mouse_sensitivity
			pcam_rotation_degrees.x = clampf(pcam_rotation_degrees.x, min_pitch, max_pitch)
			pcam_rotation_degrees.y -= event.relative.x * mouse_sensitivity
			pcam_rotation_degrees.y = wrapf(pcam_rotation_degrees.y, 0, 360)  # prevent negative values
			print(pcam_rotation_degrees.y)
			pcam_rotation_degrees.y = clampf(pcam_rotation_degrees.y, min_yaw, max_yaw)
			pcam.set_third_person_rotation_degrees(pcam_rotation_degrees)
