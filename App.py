import pygame
import time

class App:
    def __init__(self, screen):
        self.screen = screen
        self.exit_message = ""
        self.current_app = None
        self.parameters = []

    def run_app(self, app):
        self.current_app = app
        app() # runs the app

        self.parameters = []

        match self.exit_message:
            case "Exicode : 0":
                self.current_app = None
                print("Exicode : 0, App closed successfully.")
            case _:
                self.current_app = None
                print("Exicode : None, App closed with unknown exit code.")


    ### APPLICATIONS ###

    def AppEditor(self):
        class app():
            def __init__(self, os, app_name, line_number):
                self.os = os

                print("editing")
                self.app_name = app_name
                self.line_number = line_number

                self.render_group = []

                self.is_running = True

                self.load_default_textures()

                self.pixel_font = pygame.font.Font("ProgOs/Assets/Font/ProgFont.ttf", 16)

                self.update_app_name_text()

            def load_default_textures(self):
                self.bg_texture = self.load_texture("ProgOs/Assets/Textures/text_editor_bg.png")

            def load_texture(self, file_path):
                return pygame.image.load(file_path).convert_alpha()

            def display_text(self, text, position, layer, color=(pygame.Color("White")), scale=1):
                text_surface = self.pixel_font.render(text, True, color)
                return {"texture": text_surface, "pos": position, "layer": layer, "scale": scale}

            def get_object_texture(self, name):
                objects = {
                    "bg_texture": {"texture": self.bg_texture, "pos": (0, 0), "layer": 0, "scale" : 1},
                }
                return objects.get(name, None)

            def render(self):
                items = [i for i in self.render_group if isinstance(i, dict) and i.get("texture")]
                for item in sorted(items, key=lambda x: x.get("layer", 0)):
                    scale = float(item.get("scale", 1))

                    w = int(item["texture"].get_width() * scale)
                    h = int(item["texture"].get_height() * scale)
                    scaled_texture = pygame.transform.scale(item["texture"], (w, h))

                    self.os.screen.blit(scaled_texture, item.get("pos", (0, 0)))
                pygame.display.flip()

            def update_app_name_text(self):
                # set the text and upper case it
                self.app_name_text = self.display_text(self.app_name.upper(), (4,6), 1, pygame.Color("White"), 2)

            ### ALL APP MODIFY LOGIC ###
            def get_app_code(self):

                """ TODO : i need to replace this code to only get the content of the app method, in the app class, in the app method, in the app class"""

                with open("ProgOs/App.py", "r") as app_file:
                    lines = app_file.readlines()
                # checks all the lines in the app class inside the app fonction
                app_code = []
                if self.line_number is None:
                    return None
                for line in range(self.line_number, len(lines)):
                    if lines[line].startswith("    def " + self.app_name + "("):
                        break
                    app_code.append(lines[line])
                # checks for the end line of app (start of other app or end of code)
                for line in range(self.line_number + len(app_code), len(lines)):
                    if lines[line].startswith("    def "):
                        break
                    app_code.append(lines[line])
                # loop through all app line and remove indent
                code = []
                # goes from line 1 of app to the end
                for line in app_code:
                    code.append(self.remove_indent(line))
                return code

                    
            def remove_indent(self,line):
                if line.startswith("    "):
                     line = line[12:]
                return line
            
            def split_code_to_lines(self, code):
                for i in range(len(code)):
                    code[i] = code[i].split("\n")[0]  # Remove any trailing newline characters
                return code
            
            def display_app_code(self, line_number, x_offset=0):
                code = self.get_app_code()
                if code is None:
                    return None
                
                code = self.split_code_to_lines(code)
                
                # Render settings
                BASE_OFFSET = (4, 34)
                LINE_HEIGHT = 16
                MAX_LINES = 18
                
                # Build render items for visible lines
                items = []
                for i in range(MAX_LINES):
                    idx = line_number + i
                    if idx < len(code):
                        x = BASE_OFFSET[0] + x_offset
                        y = BASE_OFFSET[1] + i * LINE_HEIGHT
                        item = self.display_text(code[idx], (x, y), 1, (11, 64 ,20), 1)
                        items.append(item)
                
                return items

            
            def app(self):
                while self.is_running:

                    self.render_group = [self.get_object_texture("bg_texture")]
                    for item in self.display_app_code(0):
                        self.render_group.append(item)
                    self.render()
                        
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                self.is_running = False

        self.app_instance = app(self, self.parameters[0], self.parameters[1])
        self.app_instance.app()
        self.exit_message = "Exicode : 0"

    def test_app():
        class app():
            def __init__(self):
               print("Hello World !")
               
            def app():
                pass

        self.app_instance = app(self,  self.parameters[0], self.parameters[1])
        self.app_instance.app()

