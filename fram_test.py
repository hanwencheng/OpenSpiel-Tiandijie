import tkinter as tk

class ButtonManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Button Manager")
        self.buttons = {}
        self.counter = 0

    def add_button(self):
        self.counter += 1
        button_id = f"button_{self.counter}"
        button = tk.Button(self.root, text=button_id, command=lambda bid=button_id: self.delete_button(bid))
        button.pack()
        self.buttons[button_id] = button

    def delete_button(self, button_id):
        button = self.buttons.get(button_id)
        if button:
            button.destroy()
            del self.buttons[button_id]

    def run(self):
        add_button = tk.Button(self.root, text="Add Button", command=self.add_button)
        add_button.pack()
        self.root.mainloop()

if __name__ == "__main__":
    manager = ButtonManager()
    manager.run()
