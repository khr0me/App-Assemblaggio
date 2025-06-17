from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.checkbox import CheckBox
from kivy.uix.floatlayout import FloatLayout
from datetime import datetime, timedelta
import csv

# Schermata Principale
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        title = Label(text="STAMPOPLAST", size_hint=(None, None), size=(600, 100), pos_hint={'center_x': 0.5, "top": 0.98}, color=(1, 0, 0, 1), font_size=80, bold=True)

        assemb_lb = Label(text="Reparto Assemblaggio", size_hint=(None, None), size=(500, 60), pos_hint={'center_x': 0.5, "top": 0.83}, font_size=40)
        reg_lb = Label(text="Registro Lavorazioni", size_hint=(None, None), size=(500, 60), pos_hint={'center_x': 0.5, "top": 0.77}, font_size=40)

        start_btn = Button(text="START", size_hint=(None, None), size=(200, 100), pos_hint={'center_x': 0.4, "center_y": 0.35}, background_color=(0, 1, 0, 1), font_size=30, bold=True)
        stop_btn = Button(text="STOP", size_hint=(None, None), size=(200, 100), pos_hint={'center_x': 0.6, "center_y": 0.35}, background_color=(1, 0, 0, 1), font_size=30, bold=True)
        exit_btn = Button(text="EXIT", size_hint=(None, None), size=(200, 100), pos_hint={'right': 0.97, "top": 0.95}, background_color=(0, 1, 1, 1), font_size=30, bold=True)

        start_btn.bind(on_press=self.start)
        stop_btn.bind(on_press=self.stop)
        exit_btn.bind(on_press=self.exit_app)

        layout.add_widget(title)
        layout.add_widget(assemb_lb)
        layout.add_widget(reg_lb)
        layout.add_widget(start_btn)
        layout.add_widget(stop_btn)
        layout.add_widget(exit_btn)

        self.add_widget(layout)

    def start(self, instance):
        self.manager.current = 'start_screen'

    def stop(self, instance):
        self.manager.current = 'stop_screen'

    def exit_app(self, instance):
        App.get_running_app().stop()

# Schermata Start
class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        title = Label(text="Registro di eventi START", size_hint=(None, None), size=(700, 100), pos_hint={'center_x': 0.5, "top": 0.98}, font_size=70, bold=True, color=(1, 0, 0, 1))

        op_lbl = Label(text="Numero Operatore", pos_hint={'center_x': 0.5, "top": 0.9}, size_hint=(None, None), font_size=40)
        self.numOp_in = TextInput(size_hint=(None, None), size=(320, 50), pos_hint={'center_x': 0.5, "top": 0.83}, font_size=20)

        ord_lbl = Label(text="Numero ordine di produzione", pos_hint={'center_x': 0.5, "top": 0.77}, size_hint=(None, None), font_size=40)
        self.numOrd_in = TextInput(size_hint=(None, None), size=(320, 50), pos_hint={'center_x': 0.5, "top": 0.70}, font_size=20)

        laser_lbl = Label(text="L'ordine è di laseratura:", pos_hint={'center_x': 0.5, "top": 0.60}, size_hint=(None, None), font_size=40)

        self.laser_si = CheckBox(group='laser', pos_hint={'center_x': 0.47, "top": 0.55}, size_hint=(None, None))
        self.laser_no = CheckBox(group='laser', pos_hint={'center_x': 0.47, "top": 0.50}, size_hint=(None, None))
        laser_si_lbl = Label(text="SI", pos_hint={'center_x': 0.53, "center_y": 0.505}, font_size=30)
        laser_no_lbl = Label(text="NO", pos_hint={'center_x': 0.53, "center_y": 0.45}, font_size=30)

        save_btn = Button(text="SALVA", pos_hint={'center_x': 0.5, "top": 0.25}, size_hint=(None, None), size=(200, 100), background_color=(0, 1, 0, 1), font_size=30, bold=True)
        home_btn = Button(text="HOME", pos_hint={'right': 0.97, "top": 0.95}, size_hint=(None, None), size=(200, 100), background_color=(1, 1, 0, 1), font_size=30, bold=True)

        home_btn.bind(on_press=self.home)
        save_btn.bind(on_press=self.salva)

        layout.add_widget(title)
        layout.add_widget(op_lbl)
        layout.add_widget(self.numOp_in)
        layout.add_widget(ord_lbl)
        layout.add_widget(self.numOrd_in)
        layout.add_widget(laser_lbl)
        layout.add_widget(self.laser_si)
        layout.add_widget(self.laser_no)
        layout.add_widget(laser_si_lbl)
        layout.add_widget(laser_no_lbl)
        layout.add_widget(save_btn)
        layout.add_widget(home_btn)

        self.add_widget(layout)

    def salva(self, instance):
        op = self.numOp_in.text
        ord = self.numOrd_in.text
        start_time = datetime.now().strftime("%H:%M:%S")

        laser = 'SI' if self.laser_si.active else 'NO'
        print(f"[START] Operatore: {op}, Ordine: {ord}, Laser: {laser}, Start Time: {start_time}")
        
        data = [op, ord, laser, start_time]

        with open('record.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='|', quotechar='"', escapechar='\\')
            writer.writerow(data)

    def home(self, instance):
        self.manager.current = 'main'

# Schermata Stop
class StopScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        title = Label(text="Registro di eventi STOP", size_hint=(None, None), size=(700, 100), pos_hint={'center_x': 0.5, "top": 0.98}, font_size=70, bold=True, color=(1, 0, 0, 1))

        op_lbl = Label(text="Numero Operatore", pos_hint={'center_x': 0.5, "center_y": 0.85}, font_size=40)
        self.numOp_in = TextInput(size_hint=(None, None), size=(320, 50), pos_hint={'center_x': 0.5, "center_y": 0.8}, font_size=20)

        ord_lbl = Label(text="Numero ordine di produzione", pos_hint={'center_x': 0.5, "center_y": 0.72}, font_size=40)
        self.numOrd_in = TextInput(size_hint=(None, None), size=(320, 50), pos_hint={'center_x': 0.5, "center_y": 0.67}, font_size=20)

        prd_lbl = Label(text="Pezzi Prodotti", pos_hint={'center_x': 0.5, "center_y": 0.59}, font_size=40)
        self.numPrd_in = TextInput(size_hint=(None, None), size=(320, 50), pos_hint={'center_x': 0.5, "center_y": 0.54}, font_size=20)

        laser_lbl = Label(text="L'ordine è di laseratura:", pos_hint={'center_x': 0.5, "center_y": 0.45}, font_size=40)
        self.laser_si = CheckBox(group='laser', pos_hint={'center_x': 0.47, "center_y": 0.40}, size_hint=(None, None))
        self.laser_no = CheckBox(group='laser', pos_hint={'center_x': 0.47, "center_y": 0.35}, size_hint=(None, None))
        laser_si_lbl = Label(text="SI", pos_hint={'center_x': 0.53, "center_y": 0.40}, font_size=40)
        laser_no_lbl = Label(text="NO", pos_hint={'center_x': 0.53, "center_y": 0.35}, font_size=40)

        save_btn = Button(text="SALVA", pos_hint={'center_x': 0.5, "center_y": 0.25}, size_hint=(None, None), size=(200, 100), background_color=(0, 1, 0, 1), font_size=30, bold=True)
        home_btn = Button(text="HOME", pos_hint={'right': 0.97, "center_y": 0.905}, size_hint=(None, None), size=(200, 100), background_color=(1, 1, 0, 1), font_size=30, bold=True)

        home_btn.bind(on_press=self.home)
        save_btn.bind(on_press=self.salva)

        layout.add_widget(title)
        layout.add_widget(op_lbl)
        layout.add_widget(self.numOp_in)
        layout.add_widget(ord_lbl)
        layout.add_widget(self.numOrd_in)
        layout.add_widget(prd_lbl)
        layout.add_widget(self.numPrd_in)
        layout.add_widget(laser_lbl)
        layout.add_widget(self.laser_si)
        layout.add_widget(self.laser_no)
        layout.add_widget(laser_si_lbl)
        layout.add_widget(laser_no_lbl)
        layout.add_widget(save_btn)
        layout.add_widget(home_btn)

        self.add_widget(layout)

    def salva(self, instance):
        op = self.numOp_in.text
        ord = self.numOrd_in.text
        prd = self.numPrd_in.text
        stop_time = datetime.now().strftime("%H:%M:%S")

        laser = 'SI' if self.laser_si.active else 'NO'
        print(f"[STOP] Operatore: {op}, Ordine: {ord}, Laser: {laser}, Pezzi: {prd}, Stop Time: {stop_time}")
        
        data = [op, ord, laser, prd, stop_time]

        with open('record.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='|', quotechar='"', escapechar='\\')
            writer.writerow(data)

    def home(self, instance):
        self.manager.current = 'main'

# App Start
class AppAssemblaggio(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(StartScreen(name='start_screen'))
        sm.add_widget(StopScreen(name='stop_screen'))
        return sm

if __name__ == '__main__':
    Window.maximize()
    AppAssemblaggio().run()
