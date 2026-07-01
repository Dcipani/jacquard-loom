import pygame
from preprocess import image_to_jacquard_matrix

SCREEN_W = 1200
SCREEN_H = 800
MARGIN = 50
THREAD_SPACING = 1
SCROLL_SPEED = 30

class WeftBar:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

class InputBox:
    def __init__(self, x, y, w, h, text="10"):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit():
                self.text += event.unicode

    def value(self):
        return max(1, int(self.text)) if self.text else 1

    def draw(self, screen, font):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        surf = font.render(self.text, True, (0, 0, 0))
        screen.blit(surf, (self.rect.x + 5, self.rect.y + 5))

def compute_thread_width(num_threads):
    available = SCREEN_W - 2 * MARGIN
    total_spacing = (num_threads - 1) * THREAD_SPACING
    max_thread_width = (available - total_spacing) // num_threads
    return max(1, min(6, max_thread_width))

def build_weft_bars(matrix, thread_width, weft_color):
    rows, cols = matrix.shape

    loom_width = cols * thread_width + (cols - 1) * THREAD_SPACING
    rightmost_warp_x = MARGIN + (cols - 1) * (thread_width + THREAD_SPACING)
    start_x = rightmost_warp_x + thread_width + THREAD_SPACING
    bars = []

    for row in range(rows):
        y = MARGIN + row * (thread_width + THREAD_SPACING)
        bars.append(
            WeftBar(
                x=start_x,
                y=y,
                width=loom_width,
                height=thread_width,
                color=weft_color
            )
        )
    return bars

def weave(weft_bars, active_row, speed):
    if active_row >= len(weft_bars):
        return active_row
    active_bar = weft_bars[active_row]
    active_bar.x -= speed

    if active_bar.x <= MARGIN:
        active_bar.x = MARGIN
        active_row += 1

    return active_row


def draw_interlaced(surface, matrix, thread_width, warp_color, weft_bars):
    rows, cols = matrix.shape
    loom_height = rows * (thread_width + THREAD_SPACING) - THREAD_SPACING

    for col in range(cols):
        x = MARGIN + col * (thread_width + THREAD_SPACING)

        pygame.draw.rect(
            surface,
            warp_color,
            (x, MARGIN, thread_width, loom_height)
        )

    for row, bar in enumerate(weft_bars):
        pygame.draw.rect(
            surface,
            bar.color,
            (bar.x, bar.y, bar.width, bar.height)
        )

        for col in range(cols):
            if matrix[row][col] == 1:
                x = MARGIN + col * (thread_width + THREAD_SPACING)

                pygame.draw.rect(
                    surface,
                    warp_color,
                    (x, bar.y, thread_width, thread_width)
                )


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    matrix, warp_color, weft_color = image_to_jacquard_matrix(
        "input.png",
        (0, 50, 80),
        (80, 50, 200)
    )

    rows, cols = matrix.shape
    thread_width = compute_thread_width(cols)

    loom_width = cols * thread_width + (cols - 1) * THREAD_SPACING
    loom_height = rows * thread_width + (rows - 1) * THREAD_SPACING

    world = pygame.Surface((
        loom_width + 2 * MARGIN,
        loom_height + 2 * MARGIN
    ))
    weft_bars = build_weft_bars(
        matrix,
        thread_width,
        weft_color
    )

    input_box = InputBox(50, 10, 100, 30, "10")
    active_row = 0
    camera_y = 0

    running = True
    while running:
        screen.fill((240, 240, 240))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    camera_y += SCROLL_SPEED
                elif event.key == pygame.K_UP:
                    camera_y -= SCROLL_SPEED

            input_box.handle_event(event)

        speed = input_box.value()

        active_row = weave(
            weft_bars,
            active_row,
            speed
        )
        if active_row < len(weft_bars):
            camera_y = max(
                0,
                weft_bars[active_row].y - SCREEN_H // 2
            )
        camera_y = max(
            0,
            min(camera_y, world.get_height() - SCREEN_H)
        )
        world.fill((240, 240, 240))
        draw_interlaced(
            world,
            matrix,
            thread_width,
            warp_color,
            weft_bars
        )
        screen.blit(
            world,
            (0, 0),
            area=pygame.Rect(
                0,
                camera_y,
                SCREEN_W,
                SCREEN_H
            )
        )
        input_box.draw(screen, font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
