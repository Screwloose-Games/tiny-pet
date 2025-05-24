extends Button

const MASTER_AUDIO_MUS_INDEX = 0

@export var mute_icon: Texture2D
@export var unmute_icon: Texture2D

var _is_muted: bool = true

func _ready() -> void:
	button_pressed = true
	toggled.connect(_on_toggled)
	_on_toggled(_is_muted)

func _on_toggled(is_muted: bool):
	_is_muted = is_muted
	if is_muted:
		mute()
	else:
		unmute()

func mute():
	icon = mute_icon
	AudioServer.set_bus_mute(MASTER_AUDIO_MUS_INDEX, true)

func unmute():
	icon = unmute_icon
	AudioServer.set_bus_mute(MASTER_AUDIO_MUS_INDEX, false)
