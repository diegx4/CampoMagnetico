import pygame
import math

# Inicializar Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 800, 700
BACKGROUND_COLOR = (0, 0, 0)
CHARGE_RADIUS = 20
SENSOR_RADIUS = 10
K = 8.99e9
ARROW_COLOR = (255, 255, 255)
ARROW_LENGTH = 20

# Configurar pantalla
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Producto Final")

# Definir cargas
charges = [
    {"pos": [WIDTH // 2 - 100, HEIGHT // 2 - 50], "q": 1e-9},
    {"pos": [WIDTH // 2 + 100, HEIGHT // 2 - 50], "q": -1e-9},
]

# Definir sensor
sensor = {"pos": [WIDTH // 2, HEIGHT // 2 + 100]}

# Slider configuración
slider_rects = [pygame.Rect(150, HEIGHT - 50, 200, 10),
                pygame.Rect(450, HEIGHT - 50, 200, 10)]
slider_values = [0.5, -0.5]

# Estados
dragging = None
selected_slider = None

def calculate_field(x, y, charges):
    Ex, Ey = 0, 0
    for charge in charges:
        dx = x - charge["pos"][0]
        dy = y - charge["pos"][1]
        r_squared = dx ** 2 + dy ** 2
        if r_squared != 0:
            r = math.sqrt(r_squared)
            E = K * charge["q"] / r_squared
            Ex += E * dx / r
            Ey += E * dy / r
    return Ex, Ey

def draw_arrow(screen, start_pos, end_pos, color=ARROW_COLOR, width=3):
    pygame.draw.line(screen, color, start_pos, end_pos, width)
    angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])
    arrow_size = 5
    left = (end_pos[0] - arrow_size * math.cos(angle - math.pi / 6),
            end_pos[1] - arrow_size * math.sin(angle - math.pi / 6))
    right = (end_pos[0] - arrow_size * math.cos(angle + math.pi / 6),
             end_pos[1] - arrow_size * math.sin(angle + math.pi / 6))
    pygame.draw.polygon(screen, color, [end_pos, left, right])

def draw_charges(screen, charges):
    font = pygame.font.SysFont('Arial', 24, bold=True)
    for charge in charges:
        color = (255, 0, 0) if charge["q"] > 0 else (0, 128, 255)
        pygame.draw.circle(screen, color, charge["pos"], CHARGE_RADIUS)
        pygame.draw.circle(screen, (255, 255, 255), charge["pos"], CHARGE_RADIUS, 2)
        sign = '+' if charge["q"] > 0 else '−'
        text = font.render(sign, True, (255, 255, 255))
        text_rect = text.get_rect(center=charge["pos"])
        screen.blit(text, text_rect)

def draw_field_vectors(screen, charges):
    for x in range(0, WIDTH, 40):
        for y in range(0, HEIGHT - 100, 40):  # Limita vectores hasta zona válida
            Ex, Ey = calculate_field(x, y, charges)
            magnitude = math.hypot(Ex, Ey)
            if magnitude > 0:
                Ex, Ey = (Ex / magnitude) * ARROW_LENGTH, (Ey / magnitude) * ARROW_LENGTH
                end_pos = (x + int(Ex), y + int(Ey))
                draw_arrow(screen, (x, y), end_pos)

def draw_sliders(screen, slider_rects, slider_values):
    font = pygame.font.SysFont('Arial', 20)
    for i, rect in enumerate(slider_rects):
        pygame.draw.rect(screen, (255, 255, 255), rect, 2)
        x = rect.x + int((slider_values[i] + 5) / 10 * rect.width)
        pygame.draw.circle(screen, (200, 200, 0), (x, rect.centery), 10)
        q_value = round(slider_values[i], 2)
        text = font.render(f"Q{i+1}: {q_value} nC", True, (255, 255, 255))
        screen.blit(text, (rect.x, rect.y - 25))

def draw_sensor(screen, sensor, charges):
    pygame.draw.circle(screen, (0, 255, 0), sensor["pos"], SENSOR_RADIUS)
    pygame.draw.circle(screen, (255, 255, 255), sensor["pos"], SENSOR_RADIUS, 2)
    Ex, Ey = calculate_field(sensor["pos"][0], sensor["pos"][1], charges)
    magnitude = math.hypot(Ex, Ey)
    if magnitude > 0:
        Ex, Ey = (Ex / magnitude) * 50, (Ey / magnitude) * 50
        end_pos = (sensor["pos"][0] + int(Ex), sensor["pos"][1] + int(Ey))
        draw_arrow(screen, sensor["pos"], end_pos, color=(0, 255, 0), width=4)

def draw_field_lines(screen, charges):
    steps = 500
    step_size = 5
    for charge in charges:
        for angle in range(0, 360, 30):
            x, y = charge["pos"]
            x += CHARGE_RADIUS * math.cos(math.radians(angle))
            y += CHARGE_RADIUS * math.sin(math.radians(angle))
            points = []
            for _ in range(steps):
                Ex, Ey = calculate_field(x, y, charges)
                mag = math.hypot(Ex, Ey)
                if mag == 0:
                    break
                Ex /= mag
                Ey /= mag
                x += Ex * step_size
                y += Ey * step_size
                if x < 0 or x > WIDTH or y < 0 or y > HEIGHT - 100:  # Límite abajo
                    break
                points.append((x, y))
            if len(points) > 1:
                pygame.draw.lines(screen, (255, 255, 0), False, points, 1)

# Nueva función: dibujar borde
def draw_border(screen, color=(255, 255, 255), thickness=5):
    pygame.draw.rect(screen, color, (0, 0, WIDTH, HEIGHT - 100), thickness)

# Bucle principal
running = True
while running:
    screen.fill(BACKGROUND_COLOR)

    draw_border(screen)  # Dibujar borde
    draw_field_vectors(screen, charges)
    draw_field_lines(screen, charges)
    draw_charges(screen, charges)
    draw_sensor(screen, sensor, charges)
    draw_sliders(screen, slider_rects, slider_values)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for i, charge in enumerate(charges):
                dx = mouse_pos[0] - charge["pos"][0]
                dy = mouse_pos[1] - charge["pos"][1]
                if math.hypot(dx, dy) < CHARGE_RADIUS:
                    dragging = ("charge", i)
            dx = mouse_pos[0] - sensor["pos"][0]
            dy = mouse_pos[1] - sensor["pos"][1]
            if math.hypot(dx, dy) < SENSOR_RADIUS:
                dragging = ("sensor", None)
            for i, rect in enumerate(slider_rects):
                if rect.collidepoint(mouse_pos):
                    selected_slider = i

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = None
            selected_slider = None

        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                x, y = event.pos
                # Limitar dentro de pantalla y fuera de la zona de controles
                x = max(CHARGE_RADIUS, min(x, WIDTH - CHARGE_RADIUS))
                y = max(CHARGE_RADIUS, min(y, HEIGHT - 100 - CHARGE_RADIUS))

                if dragging[0] == "charge":
                    charges[dragging[1]]["pos"][0] = x
                    charges[dragging[1]]["pos"][1] = y
                elif dragging[0] == "sensor":
                    sensor["pos"][0] = x
                    sensor["pos"][1] = y

            elif selected_slider is not None:
                rel_x = event.pos[0] - slider_rects[selected_slider].x
                rel_x = max(0, min(rel_x, slider_rects[selected_slider].width))
                slider_values[selected_slider] = (rel_x / slider_rects[selected_slider].width) * 10 - 5
                charges[selected_slider]["q"] = slider_values[selected_slider] * 1e-9

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:  # Agregar carga (aparece en zona válida)
                new_charge = {"pos": [WIDTH // 2, (HEIGHT - 100) // 2], "q": 1e-9}
                charges.append(new_charge)
            elif event.key == pygame.K_q and len(charges) > 0:  # Quitar carga
                charges.pop()

pygame.quit()
