class_name RandomUtils
extends Node

static var rand: RandomNumberGenerator:
	get = get_rand


static func get_rand():
	if rand:
		return rand
	rand = RandomNumberGenerator.new()
	rand.randomize()
	return rand


func generate_random_binary() -> int:
	return rand.randi() % 2


func generate_random_sign():
	if generate_random_binary():
		return 1
	return -1
