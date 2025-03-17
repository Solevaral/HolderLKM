import tkinter as tk
import threading
from pynput import keyboard, mouse

mouse_controller = mouse.Controller()
holding = False  # Флаг для отслеживания состояния зажатия
listening = False  # Флаг для отслеживания состояния ожидания нажатия
selected_key = "x"  # По умолчанию клавиша 'X'
listener_thread = None

def on_press(key):
    global holding, selected_key
    try:
        if key.char == selected_key and listening:
            holding = not holding  # Переключаем состояние
            status_label.config(text=f"Статус: {'Зажато' if holding else 'Отпущено'}")
            if holding:
                mouse_controller.press(mouse.Button.left)
            else:
                mouse_controller.release(mouse.Button.left)
    except AttributeError:
        pass

def start_listening():
    global listening, listener_thread
    listening = True
    status_label.config(text="Статус: Ожидание нажатия")
    
    if listener_thread is None or not listener_thread.is_alive():
        listener_thread = threading.Thread(target=run_listener, daemon=True)
        listener_thread.start()

def run_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def stop_listening():
    global listening, holding
    listening = False
    holding = False
    mouse_controller.release(mouse.Button.left)
    status_label.config(text="Статус: Остановлено")

def set_key():
    global selected_key
    selected_key = key_entry.get()
    key_label.config(text=f"Выбранная кнопка: {selected_key}")

def main():
    global key_entry, key_label, status_label
    
    root = tk.Tk()
    root.title("Настройка клавиши для зажатия мыши")
    
    tk.Label(root, text="Введите желаемую кнопку:").pack()
    key_entry = tk.Entry(root)
    key_entry.pack()
    
    key_button = tk.Button(root, text="Установить кнопку", command=set_key)
    key_button.pack()
    
    key_label = tk.Label(root, text=f"Выбранная кнопка: {selected_key}")
    key_label.pack()
    
    status_label = tk.Label(root, text="Статус: Остановлено")
    status_label.pack()
    
    start_button = tk.Button(root, text="Старт", command=start_listening)
    start_button.pack()
    
    stop_button = tk.Button(root, text="Стоп", command=stop_listening)
    stop_button.pack()
    
    root.mainloop()

if __name__ == "__main__":
    main()