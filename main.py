import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk, scrolledtext
import json
import os

class GameObject:
    def __init__(self, name, x, y, width, height, obj_type, image_path=None):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = obj_type
        self.image_path = image_path

class GameEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Roaming Engine v1")
        self.master.config(bg='#1e1e1e')  # Темный фон

        # Главное меню
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save", command=self.save_game)
        file_menu.add_command(label="Load Project", command=self.load_project)
        file_menu.add_command(label="Export", command=self.export_project)
        file_menu.add_command(label="Save Code", command=self.save_code)
        file_menu.add_command(label="Load Code", command=self.load_code)
        menubar.add_cascade(label="File", menu=file_menu)

        # Главный фрейм
        self.main_frame = tk.Frame(self.master, bg='#1e1e1e')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Панель инструментов
        self.tool_panel = tk.Frame(self.main_frame, bg='#333')
        self.tool_panel.pack(side=tk.TOP, fill=tk.X)

        self.object_type = tk.StringVar()
        self.template_menu = ttk.Combobox(self.tool_panel, textvariable=self.object_type)
        self.template_menu.pack(side=tk.LEFT, padx=5, pady=5)
        self.load_templates()

        self.add_button = tk.Button(self.tool_panel, text="Add Object", command=self.add_object, bg='#4d4d4d', fg='white')
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Поле для канваса
        self.canvas = tk.Canvas(self.main_frame, width=800, height=600, bg='white')
        self.canvas.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.objects = []
        self.selected_object = None
        self.offset_x = 0
        self.offset_y = 0

        self.canvas.bind("<Button-1>", self.select_object)
        self.canvas.bind("<ButtonRelease-1>", self.release_object)
        self.canvas.bind("<B1-Motion>", self.move_object)

        # Встроенный редактор кода
        self.code_editor = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=10, font=('Courier New', 10))
        self.code_editor.pack(padx=5, pady=5, fill=tk.X)

        # Добавим начальный код IRL
        self.initialize_irl_code()

    def initialize_irl_code(self):
        initial_code = '''# Инициализация Pygame
import pygame
pygame.init()

# Основной игровой цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Завершение работы
pygame.quit()'''
        self.code_editor.insert(tk.END, initial_code)

    def load_templates(self):
        self.templates = {}
        template_dir = "templates"
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
        for filename in os.listdir(template_dir):
            if filename.endswith(".json"):
                with open(os.path.join(template_dir, filename), 'r') as file:
                    template = json.load(file)
                    self.templates[template['name']] = template
        self.template_menu['values'] = list(self.templates.keys())

    def add_object(self):
        selected_template = self.object_type.get()
        if selected_template not in self.templates:
            messagebox.showerror("Error", "Select a valid template.")
            return

        template = self.templates[selected_template]
        name = simpledialog.askstring("Input", "Enter object name:", initialvalue=template['name'])
        if not name:
            return

        x = 100
        y = 100
        width = template['width']
        height = template['height']
        image_path = template.get('image', None)

        obj = GameObject(name, x, y, width, height, selected_template, image_path)
        self.objects.append(obj)

        if image_path:
            img = Image.open(image_path)
            img = img.resize((width, height), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(img)
            self.canvas.create_image(x + width / 2, y + height / 2, image=photo, tags="obj")
            self.canvas.image = photo  # Сохраняем ссылку на фотку
        else:
            rect_id = self.canvas.create_rectangle(x, y, x + width, y + height, fill='blue', tags="obj")
            text_id = self.canvas.create_text(x + width / 2, y + height / 2, text=name, fill='white', tags="text")

    def save_game(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        game_data = [{'name': obj.name, 'x': obj.x, 'y': obj.y, 'width': obj.width, 'height': obj.height, 'type': obj.type, 'image': obj.image_path} for obj in self.objects]
        with open(file_path, 'w') as f:
            json.dump(game_data, f)
        messagebox.showinfo("Save", "Game data saved!")

    def load_project(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        with open(file_path, 'r') as file:
            game_data = json.load(file)

        self.canvas.delete("obj")
        self.canvas.delete("text")
        self.objects.clear()

        for obj_data in game_data:
            obj = GameObject(obj_data['name'], obj_data['x'], obj_data['y'], obj_data['width'], obj_data['height'], obj_data['type'], obj_data.get('image'))
            self.objects.append(obj)

            if obj.image_path:
                img = Image.open(obj.image_path)
                img = img.resize((obj.width, obj.height), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(img)
                self.canvas.create_image(obj.x + obj.width / 2, obj.y + obj.height / 2, image=photo, tags="obj")
                self.canvas.image = photo  # Сохраняем ссылку на фотку
            else:
                self.canvas.create_rectangle(obj.x, obj.y, obj.x + obj.width, obj.y + obj.height, fill='blue', tags="obj")
                self.canvas.create_text(obj.x + obj.width / 2, obj.y + obj.height / 2, text=obj.name, fill='white', tags="text")

    def export_project(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        for obj in self.objects:
            if obj.image_path:
                image_name = f"{obj.name}.png"
                img = Image.open(obj.image_path)
                img.save(os.path.join(folder_path, image_name))

        messagebox.showinfo("Export", f"Project exported to {folder_path}.")

    def save_code(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".irl", filetypes=[("IRL files", "*.irl")])
        if not file_path:
            return
        
        with open(file_path, 'w') as f:
            f.write(self.code_editor.get("1.0", tk.END))
        messagebox.showinfo("Save Code", "IRL code saved!")

    def load_code(self):
        file_path = filedialog.askopenfilename(filetypes=[("IRL files", "*.irl")])
        if not file_path:
            return

        with open(file_path, 'r') as f:
            code = f.read()
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert(tk.END, code)

    def select_object(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        if not item:
            return

        self.selected_object = None
        for obj in self.objects:
            # Проверка пересечения с объектом
            rect_id = self.canvas.find_overlapping(obj.x, obj.y, obj.x + obj.width, obj.y + obj.height)
            if rect_id and rect_id[0] == item[0]:
                self.selected_object = obj
                self.offset_x = event.x - obj.x
                self.offset_y = event.y - obj.y
                break

    def move_object(self, event):
        if not self.selected_object:
            return

        new_x = event.x - self.offset_x
        new_y = event.y - self.offset_y

        self.canvas.coords(self.canvas.find_withtag("obj")[0], new_x + self.selected_object.width / 2, new_y + self.selected_object.height / 2)
        self.canvas.coords(self.canvas.find_withtag("text")[0], new_x + self.selected_object.width / 2, new_y + self.selected_object.height / 2)

        self.selected_object.x = new_x
        self.selected_object.y = new_y
    
    def release_object(self, event):
        self.selected_object = None

def main():
    root = tk.Tk()
    editor = GameEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()