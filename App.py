import pygame

class App:
    def __init__(self, screen):
        self.screen = screen
        self.exit_message = ""
        self.current_app = None
        self.parameters = []

    def run_app(self, app):
        self.current_app = app
        app()
        self.parameters = []

        match self.exit_message:
            case "Exicode : 0":
                self.current_app = None
                print("App closed successfully.")
            case _:
                self.current_app = None
                print("App closed with error.")

    def AppEditor(self):
        class app():
            def __init__(self, os, app_name, line_number):
                self.os = os
                self.app_name = app_name
                self.line_number = line_number
                self.temp_file = "Temp_app.py"
                self.render_group = []
                self.is_running = True
                
                self.bg_texture = self._load_texture("Assets/Textures/text_editor_bg.png")
                self.pixel_font = pygame.font.Font("Assets/Font/ProgFont.ttf", 16)
                self.app_name_text = self._render_text(self.app_name.upper(), (4, 6), 1, pygame.Color("White"), 2)
                self.cursor_texture = self._load_texture("Assets/Textures/cursor.png")
                self.selected_line_texture = self._load_texture("Assets/Textures/selected_line.png")

                self.app_start_line = None
                self.app_end_line = None
                
                self._extract_and_load_code()
            
            def _load_texture(self, path):
                return pygame.image.load(path).convert_alpha()
            
            def _render_text(self, text, pos, layer, color, scale):
                surface = self.pixel_font.render(text, True, color)
                return {"texture": surface, "pos": pos, "layer": layer, "scale": scale}
            
            def _extract_and_load_code(self):
                code = self.get_app_code()
                if code:
                    with open(self.temp_file, "w") as f:
                        f.writelines(code)
            
            def render(self):
                """Render all items sorted by layer."""
                items = [i for i in self.render_group if isinstance(i, dict) and i.get("texture")]
                for item in sorted(items, key=lambda x: x.get("layer", 0)):
                    scale = float(item.get("scale", 1))
                    w, h = int(item["texture"].get_width() * scale), int(item["texture"].get_height() * scale)
                    scaled = pygame.transform.scale(item["texture"], (w, h))
                    self.os.screen.blit(scaled, item.get("pos", (0, 0)))
                pygame.display.flip()
            
            def get_app_code(self):
                """Extract app method body from App.py source."""
                with open("App.py", "r") as f:
                    lines = f.readlines()
                
                if self.line_number is None:
                    return None
                
                # Find nested app class
                app_class_idx = None
                for i in range(self.line_number, len(lines)):
                    if "class app():" in lines[i]:
                        app_class_idx = i
                        print(i)
                        break
                
                if app_class_idx is None:
                    return None
                
                # Find def app(self): method
                app_method_idx = None
                for i in range(app_class_idx, len(lines)):
                    if "def app(self):" in lines[i]:
                        app_method_idx = i
                        print(i)
                        break
                
                if app_method_idx is None:
                    return None
                
                self.app_start_line = app_method_idx + 2
                method_indent = len(lines[app_method_idx]) - len(lines[app_method_idx].lstrip())
                
                # Extract method body until instantiation/exit lines
                code = []
                last_idx = None
                for i in range(app_method_idx + 1, len(lines)):
                    if "self.app_instance" in lines[i] or "self.exit_message" in lines[i]:
                        break
                    if lines[i].strip() and not lines[i].startswith(" " * (method_indent + 4)):
                        if lines[i].strip().startswith(("def ", "class ")):
                            break
                    
                    code.append(lines[i])
                    last_idx = i
                
                self.app_end_line = (last_idx + 1) if last_idx is not None else app_method_idx + 2
                
                # Remove indentation
                cleaned = []
                for line in code:
                    if line.startswith(" " * (method_indent + 4)):
                        cleaned.append(line[method_indent + 4:])
                    elif line.strip():
                        cleaned.append(line)
                    else:
                        cleaned.append("\n")
                
                return cleaned

                    
            def display_app_code(self, start_line):
                """Display visible lines from temp file."""
                try:
                    with open(self.temp_file, "r") as f:
                        code = [line.rstrip('\n') for line in f.readlines()]
                except FileNotFoundError:
                    return []
                
                items = []
                for i in range(18):  # MAX_VISIBLE_LINES
                    idx = start_line + i
                    if idx < len(code):
                        y = 34 + i * 16  # BASE_OFFSET[1] + LINE_HEIGHT * i
                        items.append(self._render_text(code[idx], (4, y), 1, (11, 64, 20), 1))
                
                return items
            
            def save_temp_to_app(self):
                """Save temp file changes back to App.py with proper indentation."""
                with open(self.temp_file, "r") as f:
                    temp_code = f.readlines()
                
                with open("App.py", "r") as f:
                    app_lines = f.readlines()
                
                # Re-find the method boundaries in case file changed
                app_method_idx = None
                for i in range(self.line_number, len(app_lines)):
                    if "def app(self):" in app_lines[i]:
                        app_method_idx = i
                        break
                
                if app_method_idx is None:
                    return
                
                # Find where to end: stop at self.app_instance or self.exit_message
                end_idx = None
                for i in range(app_method_idx + 1, len(app_lines)):
                    if "self.app_instance" in app_lines[i] or "self.exit_message" in app_lines[i]:
                        end_idx = i
                        break
                
                if end_idx is None:
                    return
                
                # Add proper indentation for nested class method body
                method_indent = len(app_lines[app_method_idx]) - len(app_lines[app_method_idx].lstrip())
                indent = " " * (method_indent + 4)
                indented = [indent + line if line.strip() else line for line in temp_code]
                
                # Replace method body: keep everything up to and including def line, add new code, keep from end onwards
                new_lines = app_lines[:app_method_idx + 1] + indented + app_lines[end_idx:]
                
                with open("App.py", "w") as f:
                    f.writelines(new_lines)
            
            def modify_line(self, line_num, pos, text):
                """Insert text at cursor position in temp file."""
                with open(self.temp_file, "r") as f:
                    lines = f.readlines()
                
                if line_num < len(lines):
                    lines[line_num] = lines[line_num][:pos] + text + lines[line_num][pos:]
                    with open(self.temp_file, "w") as f:
                        f.writelines(lines)
            
            def delete_char_at_pos(self, line_num, pos):
                """Delete character before cursor (backspace)."""
                with open(self.temp_file, "r") as f:
                    lines = f.readlines()
                
                if line_num < len(lines) and pos > 0:
                    lines[line_num] = lines[line_num][:pos-1] + lines[line_num][pos:]
                    with open(self.temp_file, "w") as f:
                        f.writelines(lines)

            def _get_file_lines(self):
                """Read temp file lines."""
                with open(self.temp_file, "r") as f:
                    return f.readlines()
                
            def determine_visible_cursor_pos(self, selected_line, scroll_line, cursor_pos):
                BASE_OFFSET, LINE_HEIGHT, MAX_VISIBLE = (4, 34), 16, 18
                raw_lines = self._get_file_lines()            # retourne les lignes brutes avec '\n'
                lines = [l.rstrip('\n') for l in raw_lines]   # même format que display_app_code

                if selected_line < len(lines):
                    current_line = lines[selected_line]
                else:
                    current_line = ""

                    # clamp cursor_pos pour éviter overflow / négatif
                cursor_pos = max(0, min(cursor_pos, len(current_line)))

                text_before_cursor = current_line[:cursor_pos]

                    # X = offset gauche + largeur réelle du texte affiché (même font que le rendu)
                cursor_x = BASE_OFFSET[0] + self.pixel_font.size(text_before_cursor)[0]

                    # Y = offset top + (ligne visible index) * LINE_HEIGHT  (prendre en compte scroll_line)
                visible_index = selected_line - scroll_line
                cursor_y = BASE_OFFSET[1] + visible_index * LINE_HEIGHT

                if visible_index < 0:
                    cursor_y = BASE_OFFSET[1]
                elif visible_index >= MAX_VISIBLE:
                    cursor_y = BASE_OFFSET[1] + (MAX_VISIBLE - 1) * LINE_HEIGHT
                return cursor_x, cursor_y

            def app(self):
                """Main editor loop."""
                scroll_line = selected_line = cursor_pos = 0
                BASE_OFFSET, LINE_HEIGHT, MAX_VISIBLE = (4, 34), 16, 18
                
                while self.is_running:
                    
                    

                    cursor_x, cursor_y = self.determine_visible_cursor_pos(selected_line,  scroll_line, cursor_pos)
                    self.outline_line_pos = cursor_y
                    self.outline_cursor_pos = (cursor_x - 2, cursor_y)


                    self.render_group = [{"texture": self.bg_texture, "pos": (0, 0), "layer": 0, "scale": 1},
                                          self.app_name_text,
                                          {"texture": self.selected_line_texture, "pos": (0, self.outline_line_pos), "layer": 1, "scale": 1},
                                          {"texture": self.cursor_texture, "pos": self.outline_cursor_pos, "layer": 2, "scale": 1}
                                          ]
                    self.render_group.extend(self.display_app_code(scroll_line))
                    self.render()
                    
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            if mouse_y < 32:
                                print("modify app name")

                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                self.save_temp_to_app()
                                self.is_running = False

                            elif event.unicode and event.unicode.isprintable():
                                self.modify_line(selected_line, cursor_pos, event.unicode)
                                cursor_pos += 1

                            elif event.key == pygame.K_BACKSPACE and cursor_pos > 0:
                                self.delete_char_at_pos(selected_line, cursor_pos)
                                cursor_pos -= 1

                            elif event.key == pygame.K_UP and selected_line > 0:
                                selected_line -= 1
                                cursor_pos = 0
                                if selected_line < scroll_line:
                                    scroll_line = selected_line

                            elif event.key == pygame.K_DOWN and pygame.KMOD_CTRL:
                                lines = self._get_file_lines()
                                if selected_line < len(lines) - 1:
                                    selected_line += 1
                                    cursor_pos = 0
                                    if selected_line >= scroll_line + MAX_VISIBLE:
                                        scroll_line = selected_line - MAX_VISIBLE + 1

                            elif event.key == pygame.K_RIGHT and pygame.KMOD_CTRL:
                                cursor_pos -= 1

                            elif event.key == pygame.K_LEFT and pygame.KMOD_CTRL:
                                lines = self._get_file_lines()
                                if selected_line < len(lines):
                                    max_pos = len(lines[selected_line].rstrip('\n'))
                                    if cursor_pos < max_pos:
                                        cursor_pos += 1

                            elif event.key == pygame.K_RETURN:
                                self.modify_line(selected_line, cursor_pos, "\n")
                                selected_line += 1
                                cursor_pos = 0

                            elif event.key == pygame.K_TAB:
                                self.modify_line(selected_line, cursor_pos, "   ")
                                cursor_pos += 3


        self.app_instance = app(self, self.parameters[0], self.parameters[1])
        self.app_instance.app()
        self.exit_message = "Exicode : 0"
