class_name SignalConnectorAudio
extends AudioStreamPlayer3D

signal triggered

@export_enum("GlobalSignalBus") var node_name: String:
	set(val):
		node_name = val
@export_enum(
	"poop_spawned",
	"poop_cleaned",
	"creature_fed",
	"creature_died",
	"creature_petted",
	"creature_became_overfed",
	"creature_became_hungry",
	"creature_became_starving",
	"creature_became_lonely",
	"creature_became_abandoned",
)
var signal_name: String:
	set(val):
		signal_name = val

var _autoload_instance: Node


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	if Engine.is_editor_hint():
		return
	subscribe()
	triggered.connect(_on_signal_triggered)


func _on_signal_triggered():
	play()


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta: float) -> void:
	pass


func _on_autoload_signal_emitted(a = null, b = null, c = null, d = null):
	var received_args = [a, b, c, d]
	#for i in expected_args.size():
	#var expected_value = expected_args[i]
	#if expected_value != received_args[i]:
	#return
	triggered.emit()


func subscribe():
	# Validation check 1: Does the autoload exist?
	var root_ref = Engine.get_main_loop().root
	var autoload_node_path = "/root/" + node_name
	if not root_ref.has_node(autoload_node_path):
		printerr("Autoload node '", node_name, "' not found in the scene tree.")
		return
	_autoload_instance = root_ref.get_node(autoload_node_path)
	if _autoload_instance == null:
		printerr("Failed to get autoload instance: ", node_name)
		return

	# Validation check 2: Does it have the correct signal?
	if not _autoload_instance.has_signal(signal_name):
		printerr("Autoload '", node_name, "' does not have signal '", signal_name, "'.")
		return

	var error_code = _autoload_instance.connect(signal_name, _on_autoload_signal_emitted)
	if error_code == OK:
		print("Successfully subscribed to signal '", signal_name, "' on autoload '", node_name, "'")
	else:
		printerr(
			"Failed to connect to signal '",
			signal_name,
			"' on autoload '",
			node_name,
			"'. Error code: ",
			error_code
		)
