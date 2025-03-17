import tkinter as tk
import threading
from pynput import keyboard, mouse
import time

mouse_controller = mouse.Controller()
holding = False  # Флаг для отслеживания состояния зажатия
listening = False  # Флаг для отслеживания состояния ожидания
selected_key = "x"  # По умолчанию клавиша 'X'
listener_thread = None
keyboard_controller = keyboard.Controller()
holding_key = None  # Хранит текущую зажатую клавишу (A или D)

# Добавленные переменные для времени
action_time = 1  # Время зажатия клавиши (по умолчанию 1 секунда)
idle_time = 2  # Время простоя (по умолчанию 2 секунд)
use_timer = False  # Флаг для включения/выключения таймеров

# Статусы клавиш
key_status = {"a": "Не активна", "d": "Не активна"}  # Статус кнопок

# Флаг для отслеживания состояния
toggle_pressed = False
cycle_active = False  # Флаг для отслеживания активности цикла

# Функция начала прослушивания
def start_listening():
    global listening, listener_thread, cycle_active
    listening = True
    cycle_active = False  # Сначала цикл не активен
    status_label.config(text="Статус: Ожидание нажатия")
    
    if listener_thread is None or not listener_thread.is_alive():
        listener_thread = threading.Thread(target=run_listener, daemon=True)
        listener_thread.start()

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

def on_left_bracket():
    toggle_key("a")

def on_right_bracket():
    toggle_key("d")

def toggle_key(key_char):
    global holding_key, cycle_active, toggle_pressed, key_status
    if cycle_active:  # Если цикл активен, останавливаем его
        cycle_active = False  # Останавливаем цикл
        release_key()
    else:  # Если цикл не активен, запускаем его
        if holding_key != key_char:
            release_key()
            time.sleep(0.05)  # Небольшая задержка для корректного зажатия
            keyboard_controller.press(key_char)
            holding_key = key_char
            key_status[key_char] = "Зажата"  # Устанавливаем статус как "Зажата"
            update_status_labels()
            if use_timer:
                cycle_active = True  # Включаем цикл
                threading.Thread(target=timer_cycle, daemon=True).start()

def release_key():
    global holding_key, key_status
    if holding_key:
        keyboard_controller.release(holding_key)
        key_status[holding_key] = "Не активна"  # После отпускания, делаем клавишу неактивной
        holding_key = None
        update_status_labels()

def update_status_labels():
    d_status_label.config(text=f"D: {key_status['d']}")
    a_status_label.config(text=f"A: {key_status['a']}")

def stop_cycle():
    global cycle_active
    cycle_active = False  # Останавливаем цикл

def start_timer_cycle():
    global cycle_active
    cycle_active = True  # Запускаем цикл
    threading.Thread(target=timer_cycle, daemon=True).start()

def timer_cycle():
    global holding_key, cycle_active, key_status
    while cycle_active:
        # Зафиксировать время зажатия
        if holding_key:
            key_status[holding_key] = "Зажата"  # Время зажатия
            update_status_labels()
            time.sleep(action_time)  # Время зажатия
            # Отпускаем клавишу после действия
            release_key()
            key_status[holding_key] = "В ожидании"  # Статус в ожидании
            update_status_labels()
        
        # Простое ожидание перед новым циклом
        time.sleep(idle_time)  # Время простоя
        
        if cycle_active:
            # После простоя снова активируем зажатие клавиши
            if holding_key:
                key_status[holding_key] = "Зажата"
                update_status_labels()
                # Не выполняем освобождение клавиши, чтобы она осталась в зажатом состоянии
                toggle_key(holding_key)  # Повторное зажатие клавиши

def stop_listening():
    global listening, holding, cycle_active
    listening = False
    holding = False
    cycle_active = False  # Останавливаем цикл
    release_key()
    mouse_controller.release(mouse.Button.left)
    status_label.config(text="Статус: Остановлено")

def set_key():
    global selected_key
    selected_key = key_entry.get()
    key_label.config(text=f"Выбранная кнопка: {selected_key}")

def toggle_timer_option():
    global use_timer
    use_timer = timer_var.get() == 1
    if not use_timer:
        # Если галочка снята, сбрасываем время
        action_time = 1
        idle_time = 5

def update_times():
    global action_time, idle_time
    action_time = int(action_time_entry.get())  # Время зажатия
    idle_time = int(idle_time_entry.get())  # Время простоя

def run_listener():
    with keyboard.Listener(on_press=on_press) as listener, \
         keyboard.GlobalHotKeys({
             '[': on_left_bracket,
             ']': on_right_bracket
         }) as combo_listener:
        listener.join()
        combo_listener.join()

def main():
    global key_entry, key_label, status_label, d_status_label, a_status_label, action_time_entry, idle_time_entry, timer_var
    
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
    
    d_status_label = tk.Label(root, text="D: Не активна")
    d_status_label.pack()
    
    a_status_label = tk.Label(root, text="A: Не активна")
    a_status_label.pack()
    
    start_button = tk.Button(root, text="Старт", command=start_listening)
    start_button.pack()
    
    stop_button = tk.Button(root, text="Стоп", command=stop_listening)
    stop_button.pack()

    # Галочка для времени действия
    timer_var = tk.IntVar()
    timer_checkbox = tk.Checkbutton(root, text="Хотите ли добавить время действия?", variable=timer_var, command=toggle_timer_option)
    timer_checkbox.pack()

    # Время зажатия и простоя (если галочка активирована)
    time_frame = tk.Frame(root)
    time_frame.pack()
    
    tk.Label(time_frame, text="Время зажатия (секунды):").pack(side=tk.LEFT)
    action_time_entry = tk.Entry(time_frame)
    action_time_entry.insert(0, str(action_time))  # По умолчанию 1 секунда
    action_time_entry.pack(side=tk.LEFT)
    
    tk.Label(time_frame, text="Время простоя (секунды):").pack(side=tk.LEFT)
    idle_time_entry = tk.Entry(time_frame)
    idle_time_entry.insert(0, str(idle_time))  # По умолчанию 5 секунд
    idle_time_entry.pack(side=tk.LEFT)
    
    update_time_button = tk.Button(time_frame, text="Обновить время", command=update_times)
    update_time_button.pack(side=tk.LEFT)
    
    root.mainloop()

if __name__ == "__main__":
    main()
