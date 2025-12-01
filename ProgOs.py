import pygame

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
        self.pixel_font = pygame.font.Font("ProgOs/Assets/Font/reppixel.ttf", 16)

    def get_object_texture(self, name):
        # Retrieve an object by name 
        objects = {
            "background": {"texture": self.background_texture, "pos": (0, 0), "layer": 0, "scale" : 1},
            "ProgOs_Text": self.display_text("PROGOS V0.1", (8, 8), 1),
            "Create_new_app_icon": {"texture": self.create_new_app_icon_texture, "pos": (412, 1), "layer": 1, "scale" : 2}
        }
        return objects.get(name, None)

    def load_default_textures(self): # Load default textures for the OS
        # Use the actual texture file present in the repository
        self.background_texture = self.load_texture("ProgOs/Assets/Textures/ProgCom_desktop.png")
        self.create_new_app_icon_texture = self.load_texture("ProgOs/Assets/Textures/Create_new_button.png")

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

    def __loop__(self): # Main loop of the OS
        while self.Is_Running:

            # Render all textures depending on their layer
            self.render_group = [self.get_object_texture("background"),
                                 self.get_object_texture("ProgOs_Text"),
                                 self.get_object_texture("Create_new_app_icon")]
            self.render()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.Is_Running = False

if __name__ == "__main__":
    running_instance = ProgOs()
    running_instance.__init__()
    running_instance.__loop__()
