import os, json, hashlib, tempfile
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.video import Video
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from plyer import filechooser, fingerprint
from cryptography.fernet import Fernet
from jnius import autoclass

# ================= ANDROID SECURITY =================
def block_screenshot():
    try:
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        WindowManager = autoclass('android.view.WindowManager$LayoutParams')
        PythonActivity.mActivity.getWindow().addFlags(
            WindowManager.FLAG_SECURE
        )
    except:
        pass

# ================= PATH =================
BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, "data")
PHOTO = os.path.join(DATA, "photos")
VIDEO = os.path.join(DATA, "videos")
CONFIG = os.path.join(DATA, "config.json")
KEYFILE = os.path.join(DATA, "secret.key")

# ================= HELPER =================
def popup(t, m):
    Popup(title=t, content=Label(text=m), size_hint=(0.7,0.3)).open()

def hash_pin(p):
    return hashlib.sha256(p.encode()).hexdigest()

def load_key():
    if not os.path.exists(KEYFILE):
        with open(KEYFILE, "wb") as f:
            f.write(Fernet.generate_key())
    return open(KEYFILE, "rb").read()

cipher = Fernet(load_key())

def encrypt(src, dst):
    with open(src, "rb") as f:
        data = cipher.encrypt(f.read())
    with open(dst, "wb") as f:
        f.write(data)

def decrypt_temp(path):
    with open(path, "rb") as f:
        dec = cipher.decrypt(f.read())
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(dec)
    tmp.close()
    return tmp.name

# ================= GLOBAL VIEWER DATA =================
MEDIA_LIST = []
MEDIA_INDEX = 0

# ================= SCREENS =================
class Login(Screen):
    def login_pin(self):
        with open(CONFIG) as f:
            if hash_pin(self.ids.pin.text) == json.load(f)["pin"]:
                self.manager.current = "home"
            else:
                popup("Error", "PIN salah")

class Home(Screen):
    def add_photo(self):
        filechooser.open_file(on_selection=self.save_photo)

    def add_video(self):
        filechooser.open_file(on_selection=self.save_video)

    def save_photo(self, files):
        if files:
            encrypt(files[0], os.path.join(PHOTO, os.path.basename(files[0])+".enc"))
            popup("OK", "Foto disimpan")

    def save_video(self, files):
        if files:
            encrypt(files[0], os.path.join(VIDEO, os.path.basename(files[0])+".enc"))
            popup("OK", "Video disimpan")

    def open_gallery(self):
        self.manager.current = "gallery"

class Gallery(Screen):
    def on_enter(self):
        global MEDIA_LIST
        grid = self.ids.grid
        grid.clear_widgets()
        MEDIA_LIST = []

        for f in os.listdir(PHOTO):
            MEDIA_LIST.append(("photo", os.path.join(PHOTO, f)))

        for v in os.listdir(VIDEO):
            MEDIA_LIST.append(("video", os.path.join(VIDEO, v)))

        for i, item in enumerate(MEDIA_LIST):
            btn = Button(text=f"{item[0].upper()} {i+1}",
                         size_hint_y=None, height=180)
            btn.bind(on_press=lambda x, idx=i: self.open_viewer(idx))
            grid.add_widget(btn)

    def open_viewer(self, index):
        global MEDIA_INDEX
        MEDIA_INDEX = index
        self.manager.current = "viewer"

class Viewer(Screen):
    def on_enter(self):
        self.show_media()
        Window.bind(on_touch_move=self.on_swipe)

    def on_leave(self):
        Window.unbind(on_touch_move=self.on_swipe)

    def on_swipe(self, window, touch):
        global MEDIA_INDEX
        if abs(touch.dx) > 40:
            if touch.dx < 0 and MEDIA_INDEX < len(MEDIA_LIST)-1:
                MEDIA_INDEX += 1
            elif touch.dx > 0 and MEDIA_INDEX > 0:
                MEDIA_INDEX -= 1
            self.show_media()

    def show_media(self):
        self.ids.box.clear_widgets()
        mtype, path = MEDIA_LIST[MEDIA_INDEX]
        temp = decrypt_temp(path)

        if mtype == "photo":
            self.ids.box.add_widget(
                Image(source=temp, allow_stretch=True, keep_ratio=True)
            )
        else:
            self.ids.box.add_widget(
                Video(source=temp, state="play")
            )

# ================= APP =================
class PrivateMediaApp(App):
    def build(self):
        block_screenshot()

        os.makedirs(PHOTO, exist_ok=True)
        os.makedirs(VIDEO, exist_ok=True)

        if not os.path.exists(CONFIG):
            with open(CONFIG, "w") as f:
                json.dump({"pin": hash_pin("1234")}, f)

        self.sm = Builder.load_file("app.kv")
        return self.sm

    def on_pause(self):
        self.sm.current = "login"
        return True

    def on_resume(self):
        self.sm.current = "login"

PrivateMediaApp().run()
