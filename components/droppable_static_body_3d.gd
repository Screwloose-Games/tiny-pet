class_name DroppableStaticBody3D
extends StaticBody3D

signal dropped(draggable: DraggableStaticBody3D)

func drop(draggable: DraggableStaticBody3D):
	dropped.emit(draggable)
