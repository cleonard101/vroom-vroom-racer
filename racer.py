
import random
import math

# -----------------------------
# GAME SETTINGS
# -----------------------------

NUM_RIVALS = 3
LANE_COUNT = NUM_RIVALS + 1
LANE_WIDTH = 110
ROAD_WIDTH = LANE_WIDTH * LANE_COUNT
SHOULDER_WIDTH = 55

PLAYER_ROW = 480
MAX_SPEED = 10
SHOULDER_MAX_SPEED = MAX_SPEED * 0.7
ROUGH_MAX_SPEED = MAX_SPEED * 0.4

ACCEL = 0.12
BRAKE = 0.35
COAST = 0.04
ROUGH_BRAKE = 0.40

NITRO_MAX = 100.0
NITRO_MAX_SPEED = MAX_SPEED * 1.45
NITRO_ACCEL = 0.25
NITRO_DRAIN = 0.8
NITRO_RECHARGE = 0.2
NITRO_PICKUP_AMOUNT = 35.0

DASH_PERIOD = 60
DASH_LENGTH = 30

FINISH_DISTANCE = 15000

RIVAL_COLORS = [
    "car_blue",
    "car_green",
    "car_yellow"
]

GRASS_MARGIN = 150

WIDTH = (
    ROAD_WIDTH
    + 2 * SHOULDER_WIDTH
    + 2 * GRASS_MARGIN
)

HEIGHT = 600

GRASS = (40, 120, 55)
GRAVEL = (150, 140, 110)
TARMAC = (60, 60, 68)
LINE = (240, 240, 240)


# -----------------------------
# PLAYER AND GAME VARIABLES
# -----------------------------

player = Actor("car_red", (WIDTH // 2, PLAYER_ROW))

player_world_x = 0.0
camera_x = 0.0

player_speed = 0.0
distance_traveled = 0.0

game_state = "racing"

nitro = NITRO_MAX
nitro_active = False

rivals = []
nitro_pickups = []


# -----------------------------
# WORLD COORDINATES
# -----------------------------

def dist_at(y):
    return distance_traveled + (PLAYER_ROW - y)


def row_at(dist):
    return PLAYER_ROW - (dist - distance_traveled)


def road_center_world_x(y):
    d = dist_at(y)

    if d < 300:
        return 0.0

    blend = min(1.0, (d - 300) / 400.0)

    t = d - 300

    curve = (
        math.sin(t / 750.0) * 420.0
        + math.sin(t / 320.0) * 180.0
    )

    return curve * blend


def to_screen_x(world_x):
    return world_x - camera_x + WIDTH // 2


def road_left_world(y):
    return road_center_world_x(y) - ROAD_WIDTH / 2


def road_right_world(y):
    return road_center_world_x(y) + ROAD_WIDTH / 2


def on_road(world_x, y):
    return (
        road_left_world(y)
        <= world_x
        <= road_right_world(y)
    )


def on_shoulder(world_x, y):
    if on_road(world_x, y):
        return False

    return (
        road_left_world(y) - SHOULDER_WIDTH
        <= world_x
        <= road_right_world(y) + SHOULDER_WIDTH
    )


def lane_to_world_x(lane, y):
    return road_left_world(y) + lane * ROAD_WIDTH


# -----------------------------
# START NEW RACE
# -----------------------------

def new_race():
    global player_speed
    global distance_traveled
    global rivals
    global game_state
    global nitro
    global nitro_active
    global nitro_pickups
    global player_world_x
    global camera_x

    player_speed = 0.0
    distance_traveled = 0.0

    nitro = NITRO_MAX
    nitro_active = False

    game_state = "racing"

    player_lane = (NUM_RIVALS + 0.5) / LANE_COUNT

    player_world_x = lane_to_world_x(
        player_lane,
        PLAYER_ROW
    )

    camera_x = player_world_x

    player.pos = (
        to_screen_x(player_world_x),
        PLAYER_ROW
    )

    # Create rivals

    rivals = []

    for i in range(NUM_RIVALS):

        lane = (i + 0.5) / LANE_COUNT

        rivals.append({
            "actor": Actor(
                RIVAL_COLORS[i % len(RIVAL_COLORS)]
            ),
            "distance": 0.0,
            "lane": lane,
            "target_lane": lane,
            "lane_timer": random.randint(60, 180),
            "base_speed": random.uniform(7.2, 8.2),
        })

    # Create nitro pickups

    nitro_pickups = []

    for d in range(600, FINISH_DISTANCE - 300, 450):

        lane = (
            random.randint(0, LANE_COUNT - 1) + 0.5
        ) / LANE_COUNT

        nitro_pickups.append({
            "distance": d + random.randint(-100, 100),
            "lane": lane,
            "collected": False,
        })


new_race()


# -----------------------------
# DRAW GAME
# -----------------------------

def draw():

    screen.fill(GRASS)

    strip_height = 6

    # Draw road and shoulders

    for top in range(0, HEIGHT, strip_height):

        y = top + strip_height // 2

        center_x = to_screen_x(
            road_center_world_x(y)
        )

        left_x = center_x - ROAD_WIDTH // 2

        # Left shoulder

        screen.draw.filled_rect(
            Rect(
                left_x - SHOULDER_WIDTH,
                top,
                SHOULDER_WIDTH,
                strip_height
            ),
            GRAVEL
        )

        # Right shoulder

        screen.draw.filled_rect(
            Rect(
                left_x + ROAD_WIDTH,
                top,
                SHOULDER_WIDTH,
                strip_height
            ),
            GRAVEL
        )

        # Road

        screen.draw.filled_rect(
            Rect(
                left_x,
                top,
                ROAD_WIDTH,
                strip_height
            ),
            TARMAC
        )

        # Lane markings

        if dist_at(y) % DASH_PERIOD < DASH_LENGTH:

            for lane_i in range(1, LANE_COUNT):

                line_x = left_x + lane_i * LANE_WIDTH

                screen.draw.filled_rect(
                    Rect(
                        line_x - 4,
                        top,
                        8,
                        strip_height
                    ),
                    LINE
                )

    # Finish line

    finish_y = row_at(FINISH_DISTANCE)

    if -20 < finish_y < HEIGHT:

        left = to_screen_x(
            road_left_world(finish_y)
        )

        for i in range(0, ROAD_WIDTH, 20):

            color = (
                "white"
                if (i // 20) % 2 == 0
                else "black"
            )

            screen.draw.filled_rect(
                Rect(left + i, finish_y - 8, 20, 16),
                color
            )

    # Nitro pickups

    for p in nitro_pickups:

        if not p["collected"]:

            py = row_at(p["distance"])

            if -20 < py < HEIGHT + 20:

                px = to_screen_x(
                    lane_to_world_x(p["lane"], py)
                )

                screen.draw.filled_rect(
                    Rect(px - 10, py - 14, 20, 28),
                    "cyan"
                )

                screen.draw.filled_rect(
                    Rect(px - 5, py - 18, 10, 4),
                    "white"
                )

                screen.draw.text(
                    "N",
                    center=(px, py),
                    fontsize=20,
                    color="black"
                )

    # Rivals

    for r in rivals:
        r["actor"].draw()

    # Nitro flame

    if nitro_active:

        flame_h = random.randint(18, 30)

        screen.draw.filled_rect(
            Rect(
                player.x - 10,
                player.bottom - 5,
                20,
                flame_h
            ),
            "orange"
        )

        screen.draw.filled_rect(
            Rect(
                player.x - 5,
                player.bottom - 5,
                10,
                flame_h // 2
            ),
            "yellow"
        )

    # Player

    player.draw()

    # HUD

    screen.draw.text(
        f"Speed: {player_speed:0.1f}",
        topleft=(10, 10),
        fontsize=30,
        color="white"
    )

    screen.draw.text(
        f"Distance: {int(distance_traveled)} / {FINISH_DISTANCE} m",
        topleft=(10, 40),
        fontsize=30,
        color="white"
    )

    screen.draw.text(
        "Nitro:",
        topleft=(10, 72),
        fontsize=26,
        color="white"
    )

    screen.draw.filled_rect(
        Rect(75, 74, 150, 18),
        (40, 40, 40)
    )

    bar_color = (
        "cyan"
        if nitro_active
        else "deepskyblue"
    )

    screen.draw.filled_rect(
        Rect(
            75,
            74,
            int(150 * nitro / NITRO_MAX),
            18
        ),
        bar_color
    )

    # Game over banners

    if game_state == "crashed":
        _banner("CRASHED!", "Press SPACE to try again")

    elif game_state == "won":
        _banner("YOU WIN!", "Press SPACE to race again")

    elif game_state == "lost":
        _banner("YOU LOSE!", "Press SPACE to race again")


# -----------------------------
# GAME OVER BANNER
# -----------------------------

def _banner(title, subtitle):

    screen.draw.filled_rect(
        Rect(
            0,
            HEIGHT // 2 - 60,
            WIDTH,
            120
        ),
        (0, 0, 0)
    )

    screen.draw.text(
        title,
        center=(WIDTH // 2, HEIGHT // 2 - 15),
        fontsize=60,
        color="white"
    )

    screen.draw.text(
        subtitle,
        center=(WIDTH // 2, HEIGHT // 2 + 30),
        fontsize=30,
        color="white"
    )


# -----------------------------
# UPDATE GAME
# -----------------------------

def update():

    global player_speed
    global distance_traveled
    global game_state
    global nitro
    global nitro_active
    global player_world_x
    global camera_x

    if game_state != "racing":

        if keyboard.space:
            new_race()

        return

    # -------------------------
    # PLAYER STEERING
    # -------------------------

    if keyboard.left:
        player_world_x -= 6

    if keyboard.right:
        player_world_x += 6

    # Keep player near the road

    road_mid = road_center_world_x(PLAYER_ROW)

    max_offroad = (
        ROAD_WIDTH / 2
        + SHOULDER_WIDTH
        + 120
    )

    player_world_x = max(
        road_mid - max_offroad,
        min(
            road_mid + max_offroad,
            player_world_x
        )
    )

    # Camera follows player

    camera_x += (
        player_world_x - camera_x
    ) * 0.25

    player.x = to_screen_x(player_world_x)

    # -------------------------
    # NITRO
    # -------------------------

    nitro_active = (
        keyboard.space
        and keyboard.up
        and nitro > 0
    )

    if nitro_active:

        nitro = max(
            0.0,
            nitro - NITRO_DRAIN
        )

    else:

        nitro = min(
            NITRO_MAX,
            nitro + NITRO_RECHARGE
        )

    # -------------------------
    # ACCELERATION
    # -------------------------

    if nitro_active:

        player_speed += NITRO_ACCEL

    elif keyboard.up:

        player_speed += ACCEL

    elif keyboard.down:

        player_speed -= BRAKE

    else:

        player_speed -= COAST

    # -------------------------
    # ROAD SURFACE
    # -------------------------

    current_max = (
        NITRO_MAX_SPEED
        if nitro_active
        else MAX_SPEED
    )

    if on_shoulder(player_world_x, PLAYER_ROW):

        if player_speed > SHOULDER_MAX_SPEED:
            player_speed -= ROUGH_BRAKE

    elif not on_road(player_world_x, PLAYER_ROW):

        if player_speed > ROUGH_MAX_SPEED:
            player_speed -= ROUGH_BRAKE

    player_speed = max(
        0.0,
        min(current_max, player_speed)
    )

    # Move forward

    distance_traveled += player_speed

    # -------------------------
    # NITRO PICKUP COLLISIONS
    # -------------------------

    for p in nitro_pickups:

        if p["collected"]:
            continue

        py = row_at(p["distance"])

        px = to_screen_x(
            lane_to_world_x(p["lane"], py)
        )

        pickup_rect = Rect(
            px - 10,
            py - 14,
            20,
            28
        )

        if player.colliderect(pickup_rect):

            p["collected"] = True

            nitro = min(
                NITRO_MAX,
                nitro + NITRO_PICKUP_AMOUNT
            )

    # -------------------------
    # RIVAL AI
    # -------------------------

    lane_step = 1.0 / LANE_COUNT

    for r in rivals:

        gap = distance_traveled - r["distance"]

        # Rubber-banding

        if gap > 250:

            current_speed = r["base_speed"] + 2.2

        elif gap < -300:

            current_speed = r["base_speed"] - 1.2

        else:

            current_speed = r["base_speed"]

        r["distance"] += current_speed

        # Lane switching timer

        r["lane_timer"] -= 1

        if r["lane_timer"] <= 0:

            r["lane_timer"] = random.randint(90, 240)

            direction = random.choice([-1, 1])

            candidate = (
                r["target_lane"]
                + direction * lane_step
            )

            if 0 < candidate < 1:

                blocked = any(
                    other is not r
                    and abs(
                        other["target_lane"] - candidate
                    ) < lane_step * 0.5
                    and abs(
                        other["distance"] - r["distance"]
                    ) < 140

                    for other in rivals
                )

                if not blocked:
                    r["target_lane"] = candidate

        # Smooth lane movement

        diff = r["target_lane"] - r["lane"]

        if abs(diff) > 0.005:

            r["lane"] += (
                0.015 if diff > 0 else -0.015
            )

        else:

            r["lane"] = r["target_lane"]

        # Position rival in world coordinates

        rival_y = row_at(r["distance"])

        rival_wx = lane_to_world_x(
            r["lane"],
            rival_y
        )

        r["actor"].pos = (
            to_screen_x(rival_wx),
            rival_y
        )

        # Collision detection

        if player.colliderect(r["actor"]):

            game_state = "crashed"

            return

        # Rival finishes first

        if r["distance"] >= FINISH_DISTANCE:

            game_state = "lost"

            return

    # -------------------------
    # PLAYER FINISH LINE
    # -------------------------

    if distance_traveled >= FINISH_DISTANCE:

        game_state = "won"
