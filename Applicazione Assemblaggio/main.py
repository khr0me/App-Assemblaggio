from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout

import csv
import re
from datetime import datetime

# Schermata Principale
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))

        title = Label(text="STAMPOPLAST", size_hint=(None, None), size=(600, 100), pos_hint={"center_x": 0.5, "top": 0.98}, color=(1, 0, 0, 1), font_size=80, bold=True)

        assemb_lb = Label(text="Reparto Assemblaggio", size_hint=(None, None), size=(500, 60), pos_hint={"center_x": 0.5, "top": 0.83}, font_size=40)
        reg_lb = Label(text="Registro Lavorazioni", size_hint=(None, None), size=(500, 60), pos_hint={"center_x": 0.5, "top": 0.77}, font_size=40)

        start_btn = Button(text="START", size_hint=(None, None), size=(200, 100), pos_hint={"center_x": 0.4, "center_y": 0.35}, background_color=(0, 1, 0, 1), font_size=30, bold=True)
        stop_btn = Button(text="STOP", size_hint=(None, None), size=(200, 100), pos_hint={"center_x": 0.6, "center_y": 0.35}, background_color=(1, 0, 0, 1), font_size=30, bold=True)
        exit_btn = Button(text="EXIT", size_hint=(None, None), size=(200, 100), pos_hint={"right": 0.97, "top": 0.95}, background_color=(0, 1, 1, 1), font_size=30, bold=True)

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
        self.manager.current = "start_screen"

    def stop(self, instance):
        self.manager.current = "stop_screen"

    def exit_app(self, instance):
        App.get_running_app().stop()

# Schermata Start
class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = AnchorLayout(anchor_x="center", anchor_y="bottom")

        layout = BoxLayout(orientation="vertical", spacing=dp(55), size_hint=(1, None), height=dp(400), padding=dp(170))
        title = Label(text="Registro di eventi START", size_hint=(1, None), height=dp(80), font_size=70, bold=True, color=(1, 0, 0, 1))

        op_box = BoxLayout(orientation="vertical", size_hint=(None, None), width=dp(320), height=dp(100), spacing=dp(5), pos_hint={"center_x": 0.5})
        op_lbl = Label(text="Numero Operatore", size_hint=(1, None), height=dp(40), font_size=dp(40))
        self.numOp_in = TextInput(size_hint=(1, None), height=dp(50), font_size=dp(18))
        op_box.add_widget(op_lbl)
        op_box.add_widget(self.numOp_in)
        
        ord_box = BoxLayout(orientation="vertical", size_hint=(None, None), width=dp(320), height=dp(100), spacing=dp(5), pos_hint={"center_x": 0.5})
        ord_lbl = Label(text="Numero ordine di produzione", size_hint=(1, None), height=dp(40), font_size=dp(40))
        self.numOrd_in = TextInput(size_hint=(1, None), height=dp(50), font_size=dp(18))
        ord_box.add_widget(ord_lbl)
        ord_box.add_widget(self.numOrd_in)

        laser_si_box = BoxLayout(orientation="horizontal", size_hint=(None, None), width=dp(320), height=dp(20), spacing=dp(5), pos_hint={"center_x": 0.5})
        laser_no_box = BoxLayout(orientation="horizontal", size_hint=(None, None), width=dp(320), height=dp(20), spacing=dp(5), pos_hint={"center_x": 0.5})
        laser_lbl = Label(text="L'ordine è di laseratura:", size_hint=(1, None), height=dp(40), font_size=dp(40), halign="center", valign="middle")
        self.laser_si = CheckBox(group="laser", size_hint=(1, None), height=dp(20))
        self.laser_no = CheckBox(group="laser", size_hint=(1, None), height=dp(20))
        laser_si_lbl = Label(text="SI", size_hint=(1, None), height=dp(20), font_size=dp(30))
        laser_no_lbl = Label(text="NO", size_hint=(1, None), height=dp(20), font_size=dp(30))
        laser_si_box.add_widget(self.laser_si)
        laser_si_box.add_widget(laser_si_lbl)
        laser_no_box.add_widget(self.laser_no)
        laser_no_box.add_widget(laser_no_lbl)

        save_btn = Button(text="SALVA", size_hint=(None, None), width=dp(200), height=dp(100), background_color=(0, 1, 0, 1), font_size=dp(30),pos_hint={"center_x": 0.5}, bold=True)

        home_btn = Button(text="HOME", size_hint=(None, None), width=dp(200), height=dp(100), background_color=(1, 1, 0, 1), font_size=dp(30), pos_hint={"right": 1, "top": 1}, bold=True
        )
        home_btn.bind(on_press=self.home)
        save_btn.bind(on_press=self.salva_start)

        layout.add_widget(title)
        layout.add_widget(op_box)
        layout.add_widget(ord_box)
        layout.add_widget(laser_lbl)
        layout.add_widget(laser_si_box)
        layout.add_widget(laser_no_box)
        layout.add_widget(save_btn)
        layout.add_widget(home_btn)

        main_layout.add_widget(layout)
        self.add_widget(main_layout)

    def salva_start(self, instance):
        val_op = self.numOp_in.text
        val_ord = self.numOrd_in.text

        oggi = datetime.now().strftime("%d/%m/%Y")  
        start_time = datetime.now().strftime("%H:%M:%S")

        # Verifichiamo che i campi siano stati inseriti correttamente
        regex_operatore = re.compile(r'^OP\d{6}$')
        regex_ordine = re.compile(r'^\d{7}$')

        if not val_op or not val_ord:
            Popup(title="ERRORE", content=Label(text="Inserire tutti i campi richiesti"), size_hint=(None, None), pos_hint={"center_x":0.5, "center_y":0.5}, size=(300,200)).open()
            return
        elif not regex_operatore.match(val_op):
            Popup(title="ERRORE", content=Label(text="Il valore operatore non è valido."), size_hint=(None, None), pos_hint={"center_x":0.5, "center_y":0.5}, size=(300,200)).open()
            return
        elif not regex_ordine.match(val_ord):
            Popup(title="ERRORE", content=Label(text="Il valore ordine non è valido."), size_hint=(None, None), pos_hint={"center_x":0.5, "center_y":0.5}, size=(300,200)).open()
            return

        laser = "SI" if self.laser_si.active else "NO"

        nome_operatore = ""
        valore_operatore_find = val_op
        if laser == "SI":
            valore_operatore_find = val_op     
            with open("operatori.csv", "r") as file_ope:
                reader_ope = csv.reader(file_ope, delimiter='|')
                for ope in reader_ope:
                    if ope[0].strip() == valore_operatore_find.strip():
                        nome_operatore = ope[1].strip()
                        break

        print(f"[START] Operatore: {val_op}, Ordine: {val_ord}, Laser: {laser}, Start Time: {start_time}, Nome Operatore: {nome_operatore}")
        
        with open("record_start.csv", "a", newline="") as file:
            writer = csv.writer(file, delimiter='|')
            writer.writerow([val_op, val_ord, laser, oggi, start_time, nome_operatore])

        # Svuotiamo i campi della sezione start
        self.numOp_in.text = ""
        self.numOrd_in.text = ""
        self.laser_si.active = False
        self.laser_no.active = False
        
        popup = Popup(title="CONFERMA", content=Label(text="Dati salvati correttamente."), size_hint=(None, None), pos_hint={"center_x":0.5, "center_y":0.5}, size=(300,200))
        popup.bind(on_dismiss=self.home)
        popup.open()
        
        # Svuotiamo i campi start


    def home(self, instance):
        self.manager.current = "main"

# Schermata Stop
class StopScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = AnchorLayout(anchor_x="center", anchor_y="bottom")

        layout = BoxLayout(orientation="vertical", spacing=dp(55), size_hint=(1, None), height=dp(400), padding=dp(20))
        title = Label(text="Registro di eventi START", size_hint=(1, None), height=dp(80), font_size=70, bold=True, color=(1, 0, 0, 1))

        op_box = BoxLayout(orientation="vertical", size_hint=(None, None), width=dp(320), height=dp(100), spacing=dp(5), pos_hint={"center_x": 0.5})
        op_lbl = Label(text="Numero Operatore", size_hint=(1, None), height=dp(40), font_size=dp(40))
        self.numOp_in = TextInput(size_hint=(1, None), height=dp(50), font_size=dp(18))
        op_box.add_widget(op_lbl)
        op_box.add_widget(self.numOp_in)
        
        ord_box = BoxLayout(orientation="vertical", size_hint=(None, None), width=dp(320), height=dp(100), spacing=dp(5), pos_hint={"center_x": 0.5})
        ord_lbl = Label(text="Numero ordine di produzione", size_hint=(1, None), height=dp(40), font_size=dp(40))
        self.numOrd_in = TextInput(size_hint=(1, None), height=dp(50), font_size=dp(18))
        ord_box.add_widget(ord_lbl)
        ord_box.add_widget(self.numOrd_in)

        prd_box = BoxLayout(orientation="vertical", size_hint=(None, None), width=dp(320), height=dp(100), spacing=dp(5), pos_hint={"center_x": 0.5})
        prd_lbl = Label(text="Pezzi Prodotti", pos_hint={"center_x": 0.5, "center_y": 0.59}, font_size=40)
        self.numPrd_in = TextInput(size_hint=(None, None), size=(320, 50), pos_hint={"center_x": 0.5, "center_y": 0.54}, font_size=20)
        prd_box.add_widget(prd_lbl)
        prd_box.add_widget(self.numPrd_in)

        laser_si_box = BoxLayout(orientation="horizontal", size_hint=(None, None), width=dp(320), height=dp(20), spacing=dp(5), pos_hint={"center_x": 0.5})
        laser_no_box = BoxLayout(orientation="horizontal", size_hint=(None, None), width=dp(320), height=dp(20), spacing=dp(5), pos_hint={"center_x": 0.5})
        laser_lbl = Label(text="L'ordine è di laseratura:", size_hint=(1, None), height=dp(40), font_size=dp(40), halign="center", valign="middle")
        self.laser_si = CheckBox(group="laser", size_hint=(1, None), height=dp(20))
        self.laser_no = CheckBox(group="laser", size_hint=(1, None), height=dp(20))
        laser_si_lbl = Label(text="SI", size_hint=(1, None), height=dp(20), font_size=dp(30))
        laser_no_lbl = Label(text="NO", size_hint=(1, None), height=dp(20), font_size=dp(30))
        laser_si_box.add_widget(self.laser_si)
        laser_si_box.add_widget(laser_si_lbl)
        laser_no_box.add_widget(self.laser_no)
        laser_no_box.add_widget(laser_no_lbl)

        save_btn = Button(text="SALVA", pos_hint={"center_x": 0.5, "center_y": 0.25}, size_hint=(None, None), size=(200, 100), background_color=(0, 1, 0, 1), font_size=30, bold=True)
        home_btn = Button(text="HOME", pos_hint={"right": 0.97, "center_y": 0.905}, size_hint=(None, None), size=(200, 100), background_color=(1, 1, 0, 1), font_size=30, bold=True)

        home_btn.bind(on_press=self.home)
        save_btn.bind(on_press=self.salva_stop)

        layout.add_widget(title)
        layout.add_widget(op_box)
        layout.add_widget(ord_box)
        layout.add_widget(prd_box)
        layout.add_widget(laser_lbl)
        layout.add_widget(laser_si_box)
        layout.add_widget(laser_no_box)
        layout.add_widget(save_btn)
        layout.add_widget(home_btn)
        
        main_layout.add_widget(layout)
        self.add_widget(main_layout)

    def salva_stop(self, instance):
        val_op = self.numOp_in.text
        val_ord = self.numOrd_in.text
        val_prd = self.numPrd_in.text

        oggi = datetime.now().strftime("%d/%m/%Y")
        stop_time = datetime.now().strftime("%H:%M:%S")

        # Verifichiamo che i campi siano stati inseriti correttamente
        regex_operatore = re.compile(r'^OP\d{6}$')
        regex_ordine = re.compile(r'^\d{7}$')
        regex_pezzi = re.compile(r'^\d{1,9}$')

        if not val_op or not val_ord or not val_prd:
            Popup(title="ERRORE", content=Label(text="Inserire tutti i campi richiesti."), size_hint=(None, None), pos_hint={"center_x":0.5, "center_y":0.5}, size=(300,200)).open()
            return
        elif not regex_operatore.match(val_op):
            Popup(title="ERRORE", content=Label(text="Il valore operatore non è valido."), size_hint=(None, None), pos_hint={"center_x":0.5, "center_y":0.5}, size=(300,200)).open()
            return
        elif not regex_ordine.match(val_ord):
            Popup(title="ERRORE", content=Label(text="Il valore ordine non è valido."), size_hint=(None, None), pos_hint={"center_x":0.5, "center_y":0.5}, size=(300,200)).open()
            return
        elif not regex_pezzi.match(val_prd):
            Popup(title="ERRORE", content=Label(text="Il valore pezzi non è valido."), size_hint=(None, None), pos_hint={"center_x":0.5, "center_y":0.5}, size=(300,200)).open()
            return

        laser = "SI" if self.laser_si.active else "NO"
        print(f"[STOP] Operatore: {val_op}, Ordine: {val_ord}, Laser: {laser}, Pezzi: {val_prd}, Stop Time: {stop_time}")

        # Ricaviamo il nome dell'operatore
        nome_operatore = ""
        valore_operatore_find = val_op
        if laser == "laser_si":
            valore_operatore_find = val_op[:-1]      
            with open("operatori.csv", "r") as file_ope:
                reader_ope = csv.reader(file_ope, delimiter='|')
                for ope in reader_ope:
                    if ope[0] == valore_operatore_find:
                        nome_operatore = ope[1]
                        break

        with open("record_stop.csv", "a", newline="") as file:
            writer = csv.writer(file, delimiter='|')
            writer.writerow([val_op, val_ord, laser, val_prd, oggi, stop_time, nome_operatore])
        
        Popup(title="CONFERMA", content=Label(text="Dati salvati correttamente."), size_hint=(None, None), pos_hint={"center_x":0.5, "center_y":0.5}, size=(300,200)).open()

    def home(self, instance):
        self.manager.current = "main"

# App Start
class AppAssemblaggio(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(StartScreen(name="start_screen"))
        sm.add_widget(StopScreen(name="stop_screen"))
        return sm
    
    # def on_window_resize(instance, width, height):
    #     print(f"Window resized to {width}x{height}")

    # Window.bind(on_resize=on_window_resize)

if __name__ == "__main__":
    Window.maximize()
    AppAssemblaggio().run()
