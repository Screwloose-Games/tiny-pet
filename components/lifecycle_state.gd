class_name LifecycleState
extends Resource

signal lifecycle_state_changed(lifecycle_state: LifeState)
signal age_changed(new_age: float)
signal died

enum LifeState {
	EGG,
	BABY,
	YOUNG,
	ADULT,
	OLD,
	DEAD
}
# Age tracking
@export_range(0, 100, 0.1) var current_age: float = 0.0:
	set(value):
		if value != current_age:
			current_age = value
			age_changed.emit(value)
			life_state = get_life_state()

@export_range(0, 100, 0.1) var life_span: float = 80.0

# Life stage thresholds (in years)
@export_range(0, 100, 0.1) var egg_threshold: float = 1.0
@export_range(0, 100, 0.1) var baby_threshold: float = 3.0
@export_range(0, 100, 0.1) var young_threshold: float = 10.0
@export_range(0, 100, 0.1) var adult_threshold: float = 40.0
@export_range(0, 100, 0.1) var old_threshold: float = 60.0

@export_range(0.1, 120, 0.1) var seconds_per_year: float = 1.0

var life_state: LifeState = get_life_state():
	set(value):
		if value != life_state:
			life_state = value
			lifecycle_state_changed.emit(value)
			if value == LifeState.DEAD:
				died.emit()

var is_dead: bool = false:
	get:
		return life_state == LifeState.DEAD

func get_life_state() -> LifeState:
	if current_age <= egg_threshold:
		return LifeState.EGG
	if current_age <= baby_threshold:
		return LifeState.BABY
	if current_age <= young_threshold:
		return LifeState.YOUNG
	if current_age <= adult_threshold:
		return LifeState.ADULT
	if current_age <= old_threshold:
		return LifeState.OLD
	return LifeState.DEAD

func tick(delta: float) -> void:
	if not is_dead:
		current_age += delta / seconds_per_year
		if current_age >= life_span:
			die()

func die():
	life_state = LifeState.DEAD

func reduce_life_span(amount: float) -> void:
	life_span -= amount
