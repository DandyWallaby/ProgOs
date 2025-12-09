import pygame
from App import App

pygame.init()

class ProgOs:
    def __init__(self):
        # Initialize core attributes

        self.Is_Running = True
        self.Screen_Size = (480, 320)
        self.screen = pygame.display.set_mode(self.Screen_Size, pygame.NOFRAME)
        
        self.render_group = []

        # Load default textures

        self.load_default_textures()
        self.pixel_font = pygame.font.Font("Assets/Font/ProgFont.ttf", 16)

        self.app_instance = App(self.screen)

        self.is_create_new_menu_visible = False

    def get_object_texture(self, name):
        # Retrieve an object by name 
        objects = {
            "background": {"texture": self.background_texture, "pos": (0, 0), "layer": 0, "scale" : 1},
            "ProgOs_Text": self.display_text("PROGOS_v0.1", (8, 8), 1, scale=2),
            "Create_new_app_icon": {"texture": self.create_new_app_icon_texture, "pos": (412, 1), "layer": 1, "scale" : 2}
        }
        return objects.get(name, None)

    def load_default_textures(self): # Load default textures for the OS
        # Use the actual texture file present in the repository
        self.background_texture = self.load_texture("Assets/Textures/ProgCom_desktop.png")
        self.create_new_app_icon_texture = self.load_texture("Assets/Textures/Create_new_button.png")

    def load_texture(self, file_path): # Load a texture from a file path
        return pygame.image.load(file_path).convert_alpha()

    def render(self): # render all items depending on their layer and scale
        # Filter out any invalid items and safely read optional keys
        items = [i for i in self.render_group if isinstance(i, dict) and i.get("texture")]
        for item in sorted(items, key=lambda x: x.get("layer", 0)):
            scale = float(item.get("scale", 1))
            # compute scaled size
            w = int(item["texture"].get_width() * scale)
            h = int(item["texture"].get_height() * scale)
            scaled_texture = pygame.transform.scale(item["texture"], (w, h))

            self.screen.blit(scaled_texture, item.get("pos", (0, 0)))
        pygame.display.flip()

    def display_text(self, text, position, layer, color=(255, 255, 255), scale=1):
        text_surface = self.pixel_font.render(text, True, color)
        return {"texture": text_surface, "pos": position, "layer": layer, "scale": scale}

    def create_new_app(self, app_name):
        self.app_instance = App(self.screen)
        with open("App.py", "a") as app_file:
            app_file.write(f"\n    def {app_name}(self):\n")
            app_file.write("        class app():\n")
            app_file.write("            def __init__(self, os, app_name, line_number):\n")
            app_file.write("                self.os = os\n")
            app_file.write("                self.app_name = app_name\n")
            app_file.write("                self.line_count = line_number\n")
            app_file.write("            def app(self):\n")
            app_file.write("                pass\n")
            app_file.write("        self.app_instance = app(self, self.parameters[0], self.parameters[1])\n")
            app_file.write("        self.app_instance.app()\n")
            app_file.write("        self.exit_message = 'Exicode : 0'\n")

    def find_app_lines(self, app_name):
        with open("App.py", "r") as app_file:
            lines = app_file.readlines()
        
        for line in range(len(lines)):
            if lines[line].startswith("    def " + app_name + "("):
                return line + 1
        return None
    
    def modify_app(self, app_name: str):
        self.app_instance.parameters = [app_name, self.find_app_lines(app_name)]
        self.start_app("AppEditor")

    def start_app(self, app):
        
        app_method = getattr(self.app_instance, app, None)
        if callable(app_method):
            self.app_instance.run_app(app_method)
    
    def get_app_stopped(self):
        # detects if the app is done running
        return self.app_instance.current_app is None

    def __loop__(self): # Main loop of the OS
        while self.Is_Running:
            
            
            # Render all textures depending on their layer

            if not self.app_instance.current_app:
                self.render_group = [self.get_object_texture("background"),
                                    self.get_object_texture("ProgOs_Text"),
                                    self.get_object_texture("Create_new_app_icon")]
                self.render()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.Is_Running = False
                        # detects mouse button and get pos
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        if mouse_x >  412 and mouse_x < 475:
                            if mouse_y > 5 and mouse_y < 30:
                                self.create_new_app("no_name_app")
                                self.modify_app("no_name_app")
                                
                            

if __name__ == "__main__":
    running_instance = ProgOs()
    running_instance.__loop__()
