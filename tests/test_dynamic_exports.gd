@tool
extends Node3D

signal sample

var node_name: String:
	set(val): 
		node_name = val
		update_signal_options(node_name)
var signal_name: String:
	set(val):
		signal_name = val
		_on_signal_name_updated(signal_name)
var expected_args: Dictionary[String, Variant] = {}

var _signal_name_options: Array[StringName] = []
var _signal_options: Array[Dictionary] = []

var _current_signal_data: Dictionary = {}

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass

func get_current_signal_args() -> Dictionary:
	var arg_dictionary = {}
	var current_args: Array[Dictionary] = _current_signal_data["args"]
	print(current_args)
	for arg_index in current_args.size():
		var current_arg_dict: Dictionary = current_args[arg_index]
		arg_dictionary[current_arg_dict["name"]] = null
	return arg_dictionary

func _get_property_list() -> Array[Dictionary]:
	# get globals and return a list of global autoload node names as strings options for the node_name property
	var autoloads = []
	for autoload in get_tree().root.get_children():
		if autoload != get_tree().get_current_scene():
			autoloads.push_back(autoload)
	var node_names = []
	for signal_data in get_signal_list():
		node_names.append(signal_data.name)
	for node: Node in autoloads:
		if node.name != "Global":
			node_names.append(node.name)

	#var test_enum = load("res://globals/environment_manager.gd")
	#var final_enum = test_enum.get("ItemType")
	

	var properties: Array[Dictionary] = [
		{
			"name": "node_name",
			"type": TYPE_STRING,
			"hint": PROPERTY_HINT_ENUM,
			"hint_string": ",".join(list_autoloads()),
			"usage": PROPERTY_USAGE_DEFAULT
		},
		{
			"name": "signal_name",
			"type": TYPE_STRING,
			"hint": PROPERTY_HINT_ENUM,
			"hint_string": ",".join(_signal_name_options),
			"usage": PROPERTY_USAGE_DEFAULT
		},
	]
	
	
	
	
	if _current_signal_data:
		

			
		#data_to_append.merge({
			#"name": "args",
			#"usage": PROPERTY_USAGE_DEFAULT
		#})
		#hint_string = "%d:%d:" % [TYPE_STRING, TYPE_FLOAT]
		
		properties.append({
			"name": "expected_args",
			"type": TYPE_DICTIONARY,
			"hint": PROPERTY_HINT_DICTIONARY_TYPE,
			"hint_string": "person:%d:%d:" % [TYPE_STRING, TYPE_FLOAT],
			"usage": PROPERTY_USAGE_DEFAULT
		})
			#"hint_string": "String,float",
	#
	return properties

func update_signal_options(autoload_name: StringName):
	var singleton: String = ProjectSettings.get_setting("autoload/" + autoload_name)
	if singleton is String:
		singleton = singleton.trim_prefix("*")
	
	var signals = get_signals_by_script_path(singleton)
	if _signal_name_options != signals:
		_signal_name_options = signals
		_signal_options.clear()
		print("Apeending signals to _signal_options", signals)
		_signal_options.append_array(get_signal_data_by_script_path(singleton))
		signal_name = ""
		notify_property_list_changed()

func _on_signal_name_updated(signal_name: String):
	var current_signal_data: Dictionary
	var current_signal_data_index = _signal_options.find_custom(func(signal_data: Dictionary): return signal_data.name == signal_name)

	if current_signal_data_index != -1:
		current_signal_data = _signal_options[current_signal_data_index]
	_current_signal_data =  current_signal_data

	expected_args.clear()
	expected_args.merge(get_current_signal_args())
	notify_property_list_changed()
	

func get_signals_by_script_path(script_path: String):
	var signals: Array[StringName] = []
	var signal_list: Array[Dictionary] = get_signal_data_by_script_path(script_path)
	for signal_info in signal_list:
		signals.append(signal_info.name)
	return signals

func get_signal_data_by_script_path(script_path: String):
	var signals: Array[StringName] = []
	var resource
	var script = load(script_path)
	if script is PackedScene:
		resource = script.instantiate()
	else:
		resource = script
	return resource.get_signal_list()


func list_autoloads():
	var autoloads = []
	for property in ProjectSettings.get_property_list():
		var name = property.name
		if name.begins_with("autoload/"):
			var autoload_name = name.get_slice("/", 1)
			var autoload_value = ProjectSettings.get_setting(name)
			#autoloads[autoload_name] = autoload_value
			autoloads.append(autoload_name)
	return autoloads
