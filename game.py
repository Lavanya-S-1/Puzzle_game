#----------------------------------------------------------------------------------
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import random

# Initialize OpenGL and Pygame
def init():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(-1.5, 1.5, -5)  # Adjust camera for the grid

# Load and split image into textures
def load_textures(image_path):
    image = Image.open(image_path).resize((300, 300))  # Resize to 300x300
    tile_size = 100  # Each tile is 100x100 pixels
    textures = []

    for i in range(3):
        for j in range(3):
            if i * 3 + j == 8:  # Skip the last tile (empty space)
                textures.append(None)
                continue
            box = (j * tile_size, i * tile_size, (j + 1) * tile_size, (i + 1) * tile_size)
            tile = image.crop(box)
            tile = tile.transpose(Image.FLIP_TOP_BOTTOM)  # Flip for OpenGL
            tile_data = pygame.image.tostring(pygame.image.fromstring(tile.tobytes(), tile.size, tile.mode), "RGBA", 1)

            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tile.width, tile.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tile_data)
            textures.append(texture_id)
    return textures

# Load background image as texture
def load_background(image_path):
    background_image = Image.open(image_path).resize((800, 600))  # Resize to fit the screen size
    background_data = pygame.image.tostring(pygame.image.fromstring(background_image.tobytes(), background_image.size, background_image.mode), "RGBA", 1)

    background_texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, background_texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, background_image.width, background_image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, background_data)

    return background_texture_id

# Draw the background image
def draw_background(texture):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)
    glBegin(GL_QUADS)
    # Draw the background as a large rectangle (covering the entire window)
    glTexCoord2f(0, 1)
    glVertex3f(-6.5, 5, -3)  # Top-left corner of the screen
    glTexCoord2f(1, 1)
    glVertex3f(6.5, 5, -3)  # Top-right corner
    glTexCoord2f(1, 0)
    glVertex3f(6.5, -5, -3)  # Bottom-right corner
    glTexCoord2f(0, 0)
    glVertex3f(-6.5, -5, -3)  # Bottom-left corner
    glEnd()
    glDisable(GL_TEXTURE_2D)

# Draw a single tile with a texture
def draw_tile(x, y, z, size, texture):
    if texture:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
    glBegin(GL_QUADS)
    # Front face
    glTexCoord2f(0, 0)
    glVertex3f(x, y, z)
    glTexCoord2f(1, 0)
    glVertex3f(x + size, y, z)
    glTexCoord2f(1, 1)
    glVertex3f(x + size, y - size, z)
    glTexCoord2f(0, 1)
    glVertex3f(x, y - size, z)
    glEnd()
    if texture:
        glDisable(GL_TEXTURE_2D)

# Generate and shuffle the grid
def generate_grid():
    grid = list(range(9))  # 8 tiles + 1 empty space
    random.shuffle(grid)
    while not is_solvable(grid) or is_solved(grid):
        random.shuffle(grid)
    return grid

# Check if the grid is solvable
def is_solvable(grid):
    inversions = 0
    for i in range(len(grid)):
        for j in range(i + 1, len(grid)):
            if grid[i] != 8 and grid[j] != 8 and grid[i] > grid[j]:
                inversions += 1
    return inversions % 2 == 0

# Check if the grid is solved
def is_solved(grid):
    return grid == list(range(9))

# Get the empty tile's position
def get_empty_tile(grid):
    return grid.index(8)  # The empty space is represented as 8

# Swap two tiles
def swap_tiles(grid, pos1, pos2):
    grid[pos1], grid[pos2] = grid[pos2], grid[pos1]

# Display the timer
def display_timer(elapsed_time):
    font = pygame.font.SysFont("Arial", 24)
    time_text = font.render(f"Time: {elapsed_time:.2f} seconds", True, (255, 0, 0))  # Red color
    pygame.display.get_surface().blit(time_text, (10, 10))

# Main function
def main():
    init()
    textures = load_textures("your_image.jpg")  # Replace with your image path
    background_texture = load_background("background_image.jpg")  # Replace with your background image path
    grid = generate_grid()
    tile_size = 1  # Size of each tile in OpenGL units
    start_time = pygame.time.get_ticks()  # Get the start time in milliseconds

    while True:
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0  # Convert to seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == KEYDOWN:
                empty_pos = get_empty_tile(grid)
                if event.key == K_UP and empty_pos + 3 < 9:
                    swap_tiles(grid, empty_pos, empty_pos + 3)
                elif event.key == K_DOWN and empty_pos - 3 >= 0:
                    swap_tiles(grid, empty_pos, empty_pos - 3)
                elif event.key == K_LEFT and empty_pos % 3 < 2:
                    swap_tiles(grid, empty_pos, empty_pos + 1)
                elif event.key == K_RIGHT and empty_pos % 3 > 0:
                    swap_tiles(grid, empty_pos, empty_pos - 1)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw the background first
        draw_background(background_texture)

        # Draw tiles on top of the background
        for i in range(3):
            for j in range(3):
                idx = grid[i * 3 + j]
                if idx != 8:  # Skip the empty space
                    draw_tile(j * tile_size, -i * tile_size, 0, tile_size, textures[idx])
                    

        # Display the timer (using pygame text rendering)
        display_timer(elapsed_time)

        # Update the display with OpenGL content and Pygame UI
        pygame.display.flip()  # Use flip() for OpenGL rendering

        pygame.time.wait(10)

        if is_solved(grid):
            print("You solved the puzzle!")
            pygame.quit()
            quit()

if __name__ == "__main__":
    main()
