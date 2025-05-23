class_name Poop
extends Node3D

signal cleaned

@onready var clickable_static_body_3d: ClickableStaticBody3D = %ClickableStaticBody3D

func _ready() -> void:
	clickable_static_body_3d.clicked.connect(_on_clicked)
	GlobalSignalBus.poop_spawned.emit()

func clean():
	cleaned.emit()
	GlobalSignalBus.poop_cleaned.emit()
	queue_free.call_deferred()

func _on_clicked():
	clean()
