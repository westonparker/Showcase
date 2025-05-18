import pygame
from button import button
import os


text_color = (212, 172, 0)
highlight_text = (249, 241, 24)
bg_color = (50, 60, 100)



font_path = os.path.join(os.path.dirname(__file__), "Assets", "Font.ttf")

font = pygame.font.Font(font_path, 25)

pygame.init()

# FPS
fps = 60
fpsClock = pygame.time.Clock()

# Screen setup
X = 500
Y = 500
screen = pygame.display.set_mode((X, Y))
pygame.display.set_caption("Space Trader")


#background
background_path = os.path.join(os.path.dirname(__file__), "Assets", "AdobeStock_500191857.jpeg")
background = pygame.image.load(background_path)
background = pygame.transform.scale(background, (X, Y))

#ship
ship_path = os.path.join(os.path.dirname(__file__), "Assets", "ship.png")
ship = pygame.image.load(ship_path)
ship = pygame.transform.scale(ship, (200, 52))

#thrusters
t_1_path = os.path.join(os.path.dirname(__file__), "Assets", "ship thrusters_1.png")
t_2_path = os.path.join(os.path.dirname(__file__), "Assets", "engine_thruster_2.png")
thruster1 = pygame.image.load(t_1_path)
thruster2 = pygame.image.load(t_2_path)
thruster1 = pygame.transform.scale(thruster1, (17, 52))
thruster2 = pygame.transform.scale(thruster2, (17, 52))

#indicators
port_icon_path = os.path.join(os.path.dirname(__file__), "Assets", "port.png")
port_icon = pygame.image.load(port_icon_path)

icon_width, icon_height = port_icon.get_size()

port_size = (30, 30)  # Size for ports
port_icon = pygame.transform.scale(port_icon, port_size)


# Background movement variables
bg_x = 0  # Initial position
bg_speed = 1  # Speed of movement
bg_moving = False  # Control movement


# Random Port Generation
import random
import math





class Port:
    def __init__(self, name, description, x, y, iron_price, gold_price, diamond_price,):
        self.name = name
        self.description = description
        self.x = x
        self.y = y
        self.iron_price = iron_price
        self.gold_price = gold_price
        self.diamond_price = diamond_price
        """
        self.iron_sell = iron_sell
        self.gold_sell = gold_sell
        self.diamond_sell = diamond_sell
        """
        self.data = [
            {"Item": "Iron Ore", "Value": iron_price},
            {"Item": "Gold Ore", "Value": gold_price},
            {"Item": "Diamond Ore", "Value": diamond_price},
        ]
        """
        self.sale_data = [
            {"Item": "Iron Ore", "Value": iron_sell},
            {"Item": "Gold Ore", "Value": gold_sell},
            {"Item": "Diamond Ore", "Value": diamond_sell},
        ]
        """




ports = [
    Port("Iron Mines", "Come get y'alls Iron for cheap! ", random.randint(50, X - 50), random.randint(50, Y - 50),
         random.randint(5, 10), random.randint(45, 75), random.randint(90, 200)),

    Port("Gold Mines", "Gold 4 cheap! All other luxury materials maybe. ",  random.randint(50, X - 50),random.randint(50, Y - 50),
         random.randint(15, 20), random.randint(25, 65), random.randint(150, 250)),

    Port("The Grand", "All your luxury desires, accomodated. ", random.randint(50, X - 50),random.randint(50, Y - 50),
         random.randint(10, 10), random.randint(25, 35), random.randint(250, 350)),

    Port("High Class Mining", "The best materials, for the finest Customers", random.randint(50, X - 50), random.randint(50, Y - 50),
         random.randint(10, 20), random.randint(100, 150), random.randint(100, 300))


]


def draw_table(surface, data, pos, column_widths, header_height=30, row_height=25):
    x, y = pos
    headers = ["Item", "Amount"]

    # Render header
    for i, header in enumerate(headers):
        header_surf = font.render(header, True, highlight_text)
        surface.blit(header_surf, (x + sum(column_widths[:i]), y))

    # Render rows
    data = [{"Item": item, "Amount": Ship.cargo[item]} for item in Ship.cargo]
    y += header_height
    for row in data:
        for i, key in enumerate(headers):
            cell_text = str(row[key])
            cell_surf = font.render(cell_text, True, highlight_text)
            surface.blit(cell_surf, (x + sum(column_widths[:i]), y))
        y += row_height


#ports = generate_ports()
current_port = random.choice(ports)  # Start location
hovered_port = None  # Port the player is hovering over

port_markets = {}

def travel_to_port(port):
    """Handles traveling to a new port and regenerates its market."""
    global current_port
    current_port = port



ITEMS = ["Ore", "Electronics", "Water"]


travel_to_port(current_port)

# Game state tracker
class GameState:
    MAIN_MENU = "MAIN_MENU"
    CREW = "CREW"
    CARGO = "CARGO"
    TRADE = "TRADE"
    MAP = "MAP"
    ANALYTICS = "ANALYTICS"


current_state = GameState.MAIN_MENU


# Function to return to main menu when closing a sub-screen
def return_to_main():
    global current_state
    current_state = GameState.MAIN_MENU
    pygame.display.set_caption('Space Trader')

#ship data
class Ship:
    #cargo
    cargo_space = 100
    current_cargo = 0
    cargo = {
        "Iron Ore": 0,
        "Gold Ore": 0,
        "Diamond Ore": 0,
    }

    #fuel
    fuel_space = 100
    current_fuel = 100

    #crew
    crew_space = 0
    current_crew = 0


    #credits
    current_credits = 100

    def add_cargo(item, amount):
        """Adds cargo if there's enough space."""
        if item in Ship.cargo and Ship.current_cargo + amount <= Ship.cargo_space:
            Ship.cargo[item] += amount
            Ship.current_cargo += amount
            return True  # Success
        return False

    def sell_cargo(item, item_value):

        if item in Ship.cargo and Ship.cargo[item] > 0:
            Ship.cargo[item] -= 1
            Ship.current_cargo -= 1
            Ship.current_credits += item_value
            return True  # Sale successful
        return False  # Sale failed (no stock)



def port():
    print("You have arrived at a port")

def flying():
    print("you are flying")







def crewFunction():
    pygame.display.set_caption("Crew Management")
    running = True
    while running:
        screen.fill(bg_color)  # Unique background color
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If exit is pressed, return to main
                return_to_main()
                running = False
        pygame.display.flip()
        fpsClock.tick(fps)


def cargoFunction():
    pygame.display.set_caption("Cargo Bay")
    running = True
    while running:
        screen.fill(bg_color)

        cargo_data = [{"Item": item, "Amount": Ship.cargo[item]} for item in Ship.cargo]
        draw_table(screen, cargo_data, (40, 50), [250, 100])



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return_to_main()
                running = False
        pygame.display.flip()
        fpsClock.tick(fps)


def tradeFunction():
    pygame.display.set_caption("Trade Menu")

    running = True
    data = current_port.data
    bought_message = ""  # Message to display after buying an item
    message_timer = 0  # Timer for displaying the message
    last_click = False  # Prevents rapid-fire buying

    while running:
        screen.fill(bg_color)
        mouse_x, mouse_y = pygame.mouse.get_pos()

        pos = (40, 50)
        x, y = pos
        column_widths = [250, 100]
        row_height = 25
        header_height = 30

        # Render headers
        for i, header in enumerate(["Item", "Value/Sell Value"]):
            screen.blit(font.render(header, True, highlight_text), (x + sum(column_widths[:i]), y))

        y += header_height  # Move to the first row

        for i, row in enumerate(data):
            row_rect = pygame.Rect(x, y, sum(column_widths), row_height)
            is_hovered = row_rect.collidepoint(mouse_x, mouse_y)
            row_text_color = highlight_text if is_hovered else text_color

            # Render row data
            for j, key in enumerate(["Item", "Value"]):
                screen.blit(font.render(str(row[key]), True, row_text_color), (x + sum(column_widths[:j]), y))


            screen.blit((font.render("Current Credits: " + str(Ship.current_credits)+ "c", True, highlight_text)), (25, 400))

            # If hovered and clicked, buy the item
            if is_hovered and pygame.mouse.get_pressed()[0]:
                if not last_click:  # Prevents rapid-fire buying
                    selected_item = row["Item"]
                    item_price = row["Value"]
                    temp_cargo = Ship.current_cargo + 1
                    temp_money = Ship.current_credits - item_price

                    if Ship.current_cargo < Ship.cargo_space and ((Ship.current_credits - item_price)>0):
                        success = Ship.add_cargo(selected_item, 1)
                        if success:
                            bought_message = f"Bought {selected_item}!"
                            message_timer = pygame.time.get_ticks()  # Start message timer
                            Ship.current_credits -= item_price
                            print(bought_message)
                            print(Ship.current_cargo)
                    else:
                        if temp_cargo > Ship.cargo_space:
                            bought_message = "Cargo full!"
                            message_timer = pygame.time.get_ticks()
                            print(bought_message)
                    if temp_money < 0:
                            bought_message = "Not enough Credits"
                            message_timer = pygame.time.get_ticks()
                            print(bought_message)


                    last_click = True  # Prevents holding down click


            #right click to sell
            if is_hovered and pygame.mouse.get_pressed()[2]:  # Right-click
                if not last_click:
                    selected_item = row["Item"]
                    item_price = row["Value"]

                    if Ship.cargo[selected_item] > 0:  # Ensure there is stock
                        Ship.sell_cargo(selected_item, item_price)
                        bought_message = f"Sold {selected_item} for {item_price}c!"
                        message_timer = pygame.time.get_ticks()
                    else:
                        bought_message = "Not enough stock to sell!"
                        message_timer = pygame.time.get_ticks()

                    last_click = True




            y += row_height  # Move to next row

        # If mouse is released, allow clicking again
        if not pygame.mouse.get_pressed()[0] and not pygame.mouse.get_pressed()[2]:
            last_click = False

        # Display purchase message temporarily
        if bought_message:
            elapsed_time = pygame.time.get_ticks() - message_timer
            if elapsed_time < 1000:  # Show message for 1 second
                screen.blit(font.render(bought_message, True, highlight_text), (50, 300))
            else:
                bought_message = ""  # Clear message after 1 second

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return_to_main()
                running = False

        pygame.display.flip()
        fpsClock.tick(fps)



def mapFunction():
    global hovered_port, current_port, bg_moving
    pygame.display.set_caption("Star Map")
    running = True
    message = "Hold left click to see description."


    while running:
        screen.fill(bg_color)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.blit(font.render(message, True, highlight_text), (5, 475))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return_to_main()
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                if hovered_port:
                    current_port = hovered_port  # Update current port when clicked
                    screen.fill(bg_color)  # Clear screen
                    screen.blit(font.render("Traveling to " + hovered_port.name + "...", True, highlight_text), (5, Y-25))
                    pygame.display.flip()  # Update display
                    pygame.time.delay(1000)  # Pause for 1 second (adjust if needed)
                    travel_to_port(hovered_port)
                    return_to_main()  # Exit to main screen
                    running = False
                    bg_moving = True

        hovered_port = None  # Reset hovered_port each frame

        # Draw all ports and detect hovering
        for port in ports:
            rotated_port_icon = pygame.transform.rotate(port_icon, -45)  # Adjust angle as needed

            # Adjust offset to ensure proper alignment
            icon_offset = (port.x - rotated_port_icon.get_width() // 2, port.y - rotated_port_icon.get_height() // 2)

            screen.blit(rotated_port_icon, icon_offset)

            # Check if mouse is over a port
            if port.x - port_size[0] // 2 <= mouse_x <= port.x + port_size[0] // 2 and port.y - port_size[1] // 2 <= mouse_y <= port.y + port_size[1] // 2:
                hovered_port = port

        # Draw line from current port to hovered port and show distance
        if hovered_port:
            pygame.draw.line(screen, text_color, (current_port.x, current_port.y), (hovered_port.x, hovered_port.y), 2)
            distance = math.dist((current_port.x, current_port.y), (hovered_port.x, hovered_port.y))
            text_surface = font.render(f"Distance: {int(distance)}", True, highlight_text)
            screen.blit(text_surface, (hovered_port.x + 20, hovered_port.y - 10))
            port_name = font.render(f"Port: {hovered_port.name}", True, highlight_text)
            screen.blit(port_name, (hovered_port.x + 20, hovered_port.y + 10))
            if hovered_port and isinstance(hovered_port, Port) and pygame.mouse.get_pressed()[2]:  # Ensure hovered_port is a Port object
                description_surface = font.render(hovered_port.description, True, highlight_text)
                screen.blit(description_surface, (10, 0))


        # Draw a marker for the current port
        pygame.draw.circle(screen, highlight_text, (current_port.x, current_port.y), 5)

        pygame.display.flip()
        fpsClock.tick(fps)

def analyticsFunction():
    pygame.display.set_caption("Ship Analytics")
    running = True
    while running:
        screen.fill(bg_color)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return_to_main()
                running = False
        pygame.display.flip()
        fpsClock.tick(fps)


# Mapping states to functions for modularity
screen_functions = {
    GameState.CREW: crewFunction,
    GameState.CARGO: cargoFunction,
    GameState.MAP: mapFunction,
    GameState.ANALYTICS: analyticsFunction,
    GameState.TRADE: tradeFunction,
}


# Functions to change state
def set_state(state):
    global current_state
    current_state = state


# Create buttons for the main menu
Buttons = [
    button(0, 0, 100, 100, 'Crew', lambda: set_state(GameState.CREW), True),
    button(100, 0, 100, 100, 'Cargo', lambda: set_state(GameState.CARGO), True),
    button(200, 0, 100, 100, 'Trade', lambda: set_state(GameState.TRADE), True),
    button(300, 0, 100, 100, 'Map', lambda: set_state(GameState.MAP), True),
    button(400, 0, 100, 100, 'Analytics', lambda: set_state(GameState.ANALYTICS), True),
]



frame_counter = 0
thruster_active = thruster1
fly_timer = 0


#Main Game Loop
running = True

while running:
    if current_state == GameState.MAIN_MENU:
        #background
        if bg_moving:
            movement_start_time = pygame.time.get_ticks()  # starts 3 sec timer
            bg_x -= bg_speed  # Move left
            if bg_x <= -X:  # Reset when it moves a full screen width
                bg_x = 0
        screen.blit(background, (bg_x, 0))
        screen.blit(background, (bg_x + X, 0))  # Second image to create seamless loop

        #ship
        screen.blit(ship, (146, 250))
        #thrusters
        if bg_moving:
            frame_counter += 1
            if frame_counter % 10 == 0:  # Swap every 10 frames
                thruster_active = thruster1 if thruster_active == thruster2 else thruster2
            thruster_x = 135
            thruster_y = 250
            screen.blit(thruster_active, (thruster_x, thruster_y))



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Only quits if on the main screen


        # Process buttons only in the main menu
        for btn in Buttons:
            btn.process(screen)
        pygame.display.flip()
        fpsClock.tick(fps)

    else:
        # Run the selected screen function
        screen_functions[current_state]()
        current_state = GameState.MAIN_MENU  # When a function exits, return to main menu

pygame.quit()
