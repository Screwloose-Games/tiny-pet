extends Node3D

signal petted
signal pooped
signal ate
signal cooed

@export_range(0, 120, 1) var seconds_per_poop: float = 10
@export var poop_scene: PackedScene
@export var max_poops: int = 1
@export var poop_group: String = "Poop"
@export var poop_location_marker: Marker3D

var time_since_last_poop: float = 0
var current_poop_count: int = 0

@onready var cleanliness_component: CleanlinessComponent = %CleanlinessComponent
@onready var clickable_static_body_3d: ClickableStaticBody3D = %ClickableStaticBody3D
@onready var social_component: SocialComponent = %SocialComponent

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	time_since_last_poop = seconds_per_poop
	clickable_static_body_3d.clicked.connect(_on_creature_clicked)

func _on_creature_clicked():
	social_component.pet()
	petted.emit()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	time_since_last_poop += delta
	var global_poops_count = get_tree().get_nodes_in_group(poop_group).size()
	if time_since_last_poop >= seconds_per_poop and global_poops_count < max_poops:
		spawn_poop()
		time_since_last_poop = 0

func spawn_poop():
	if not poop_scene or not poop_location_marker:
		return
	var poop_instance = poop_scene.instantiate()
	poop_location_marker.add_child(poop_instance)
	cleanliness_component.poop(poop_instance)
	poop_instance.add_to_group(poop_group)
	current_poop_count += 1
	pooped.emit()
