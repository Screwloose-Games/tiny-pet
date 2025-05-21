from PIL import Image, ImageDraw
import numpy as np



def draw_arrow(draw, start, end, color='black', width=2):
    """
    Draw an arrow from start to end on the given draw object.
    """
    draw.line([start, end], fill=color, width=width)
    # Draw the arrowhead
    arrowhead_length = 10 * width
    arrowhead_angle = 30
    angle = np.arctan2(end[1] - start[1], end[0] - start[0])
    arrowhead_left = (end[0] - arrowhead_length * np.cos(angle + np.radians(arrowhead_angle)),
                      end[1] - arrowhead_length * np.sin(angle + np.radians(arrowhead_angle)))
    arrowhead_right = (end[0] - arrowhead_length * np.cos(angle - np.radians(arrowhead_angle)),
                       end[1] - arrowhead_length * np.sin(angle - np.radians(arrowhead_angle)))
    draw.polygon([end, arrowhead_left, arrowhead_right], fill=color)


def draw_arrow_down(draw, img_width, img_height):
    bottom_center = (img_width // 2, img_height)
    center = (img_width // 2, img_height // 2)
    start = center
    end = bottom_center
    color = 'red'
    draw_arrow(draw, start, end, color=color, width=img_width//100)

def draw_arrow_right(draw, img_width, img_height):
    center_right = (img_width, img_height // 2)
    center = (img_width // 2, img_height // 2)
    start = center
    end = center_right
    color = 'red'
    draw_arrow(draw, start, end, color=color, width=img_width//100)

def draw_text_right(draw, img_width, img_height):
    center = (img_width // 2, img_height // 2)
    center_right = (img_width, img_height // 2)
    center_center_right = (center[0] + center_right[0]) // 2, (center[1] + center_right[1]) // 2
    text = "Facing Direction"

    text_position =  (center_center_right[0], center_center_right[1] - img_height // 20)
    draw.text(text_position, text, fill='red', font_size=img_height // 40)

def draw_text_down(draw, img_width, img_height):
    center = (img_width // 2, img_height // 2)
    bottom_center = (img_width // 2, img_height)
    center_center_down = (center[0] + bottom_center[0]) // 2 + 0.1 * center[0], (center[1] + bottom_center[1]) // 2
    text = "Facing Direction"

    text_position =  (center_center_down[0], center_center_down[1] - img_height // 20)
    draw.text(text_position, text, fill='red', font_size=img_height // 40)

def draw_facing_direction(draw, direction: str):
    img_width, img_height = draw.im.size
    if direction == 'down':
        draw_arrow_down(draw, img_width, img_height)
        draw_text_down(draw, img_width, img_height)
    elif direction == 'right':
        draw_arrow_right(draw, img_width, img_height)
        draw_text_right(draw, img_width, img_height)
    else:
        pass
        # Do nothing. It only makes sense to draw the facing direction for down and right.

def main():
    width, height = 256, 256
    
    image = Image.new('RGBA', (width, height), 0)
    draw = ImageDraw.Draw(image)
    draw_facing_direction(draw, 'down')

if __name__ == "__main__":
    main()