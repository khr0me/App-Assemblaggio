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
from kivy.uix.floatlayout import FloatLayout

import csv
import re
from datetime import datetime

# Funzione per calcolo della media di tempo impiegato dagli operatori
def calcola_e_salva_media(codice_operatore):
    start_records = []
    stop_records = []
    
    # Leggi record START
    try:
        with open("record_start.csv", "r") as file:
            reader = csv.reader(file, delimiter='|')
            for row in reader:
                if len(row) >= 6 and row[0].strip() == codice_operatore:
                    start_records.append({
                        'ordine': row[1].strip(),
                        'data': row[3].strip(),
                        'ora': row[4].strip(),
                        'nome': row[5].strip(),
                        'datetime': datetime.strptime(f"{row[3].strip()} {row[4].strip()}", "%d/%m/%Y %H:%M:%S")
                    })
    except FileNotFoundError:
        return
    
    # Leggi record STOP
    try:
        with open("record_stop.csv", "r") as file:
            reader = csv.reader(file, delimiter='|')
            for row in reader:
                if len(row) >= 6 and row[0].strip() == codice_operatore:
                    stop_records.append({
                        'ordine': row[1].strip(),
                        'data': row[3].strip(),
                        'ora': row[4].strip(),
                        'nome': row[5].strip(),
                        'datetime': datetime.strptime(f"{row[3].strip()} {row[4].strip()}", "%d/%m/%Y %H:%M:%S")
                    })
    except FileNotFoundError:
        return
    
    if not start_records or not stop_records:
        return
    
    # Ordina i record per data/ora
    start_records.sort(key=lambda x: x['datetime'])
    stop_records.sort(key=lambda x: x['datetime'])
    
    # Abbina START con STOP cronologicamente
    tempi_lavorazione = []
    stop_usati = set()
    
    for start in start_records:
        # Trova il primo STOP dopo questo START con stesso ordine
        for i, stop in enumerate(stop_records):
            if (i not in stop_usati and 
                stop['ordine'] == start['ordine'] and 
                stop['datetime'] >= start['datetime']):
                
                # Calcola durata
                durata_secondi = (stop['datetime'] - start['datetime']).total_seconds()
                
                if durata_secondi > 0:
                    tempi_lavorazione.append(durata_secondi)
                    stop_usati.add(i)
                    print(f"START: {start['datetime']} → STOP: {stop['datetime']} = {durata_secondi} secondi")
                break
    
    if not tempi_lavorazione:
        print(f"Nessuna lavorazione completa trovata per operatore {codice_operatore}")
        return
    
    # Calcola media
    media_secondi = sum(tempi_lavorazione) / len(tempi_lavorazione)
    nome_operatore = start_records[0]['nome'] if start_records else ""
    
    print(f"Tempi individuali: {tempi_lavorazione}")
    print(f"Media calcolata: {media_secondi} secondi")
    
    # Leggi medie esistenti
    medie_esistenti = {}
    try:
        with open("medie.csv", "r") as file:
            reader = csv.reader(file, delimiter='|')
            for row in reader:
                if len(row) >= 3:
                    medie_esistenti[row[0].strip()] = (row[1].strip(), row[2].strip())
                elif len(row) >= 2:
                    medie_esistenti[row[0].strip()] = ("", row[1].strip())
    except FileNotFoundError:
        pass
    
    # Aggiorna media
    medie_esistenti[codice_operatore] = (nome_operatore, str(round(media_secondi, 3)))
    
    # Salva file con formato: operatore|nome|media_secondi
    with open("medie.csv", "w", newline="") as file:
        writer = csv.writer(file, delimiter='|')
        for operatore, (nome, media) in medie_esistenti.items():
            writer.writerow([operatore, nome, media])
    
    print(f"Media salvata per {codice_operatore} ({nome_operatore}): {round(media_secondi, 3)} secondi")



# Schermata Principale
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Layout principale con FloatLayout per positioning assoluto
        main_layout = FloatLayout()

        # Titolo principale
        title = Label( text="STAMPOPLAST", size_hint=(None, None), size=(dp(400), dp(80)), pos_hint={"center_x": 0.5, "top": 0.95}, color=(1, 0, 0, 1), font_size=dp(100), bold=True )

        # Box per le etichette 
        labels_box = BoxLayout( orientation="vertical", spacing=dp(10), size_hint=(None, None), size=(dp(400), dp(200)), pos_hint={"center_x": 0.5, "center_y": 0.7})
        assemb_lb = Label( text="Reparto Assemblaggio", size_hint=(1, 0.5), font_size=dp(40))
        reg_lb = Label( text="Registro Lavorazioni", size_hint=(1, 0.5), font_size=dp(40))
        
        labels_box.add_widget(assemb_lb)
        labels_box.add_widget(reg_lb)

        # box per i pulsanti START/STOP 
        buttons_box = BoxLayout( orientation="horizontal", spacing=dp(200), size_hint=(None, None), size=(dp(650), dp(100)), pos_hint={"center_x": 0.5, "center_y": 0.4})
        start_btn = Button( text="START", size_hint=(0.5, 1), background_color=(0, 1, 0, 1), font_size=dp(30), bold=True) 
        stop_btn = Button( text="STOP", size_hint=(0.5, 1), background_color=(1, 0, 0, 1), font_size=dp(30), bold=True)
        
        exit_btn = Button( text="EXIT", size_hint=(None, None), size=(dp(200), dp(80)), pos_hint={"right": 0.95, "y": 0.05}, background_color=(0, 1, 1, 1), font_size=dp(25), bold=True)

        buttons_box.add_widget(start_btn)
        buttons_box.add_widget(stop_btn)

        start_btn.bind(on_press=self.start)
        stop_btn.bind(on_press=self.stop)
        exit_btn.bind(on_press=self.exit_app)

        # Aggiunta widget al layout principale
        main_layout.add_widget(title)
        main_layout.add_widget(labels_box)
        main_layout.add_widget(buttons_box)
        main_layout.add_widget(exit_btn)

        self.add_widget(main_layout)

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

        main_layout = FloatLayout()

        # Titolo centrato in alto
        title = Label( text="Registro di eventi START", size_hint=(None, None), size=(dp(500), dp(80)), pos_hint={"center_x": 0.5, "top": 0.95}, font_size=dp(80), bold=True, color=(1, 0, 0, 1))

        # box principale per i campi input
        form_box = BoxLayout( orientation="vertical", spacing=dp(20), size_hint=(None, None), size=(dp(400), dp(400)), pos_hint={"center_x": 0.5, "center_y": 0.5})

        # Campo Operatore
        op_box = BoxLayout(orientation="vertical", spacing=dp(20), size_hint=(1, None), height=dp(95))
        op_lbl = Label(text="Numero Operatore", size_hint=(1, 0.4), font_size=dp(40))
        self.numOp_in = TextInput(size_hint=(1, 0.6), font_size=dp(25))
        op_box.add_widget(op_lbl)
        op_box.add_widget(self.numOp_in)
        
        # Campo Ordine
        ord_box = BoxLayout(orientation="vertical", spacing=dp(20), size_hint=(1, None), height=dp(95))
        ord_lbl = Label(text="Numero ordine di produzione", size_hint=(1, 0.4), font_size=dp(40))
        self.numOrd_in = TextInput(size_hint=(1, 0.6), font_size=dp(25))
        ord_box.add_widget(ord_lbl)
        ord_box.add_widget(self.numOrd_in)

        # Sezione Laser
        laser_section = BoxLayout(orientation="vertical", spacing=dp(10), size_hint=(1, None), height=dp(100))        
        laser_lbl = Label( text="L'ordine è di laseratura:", size_hint=(1, 0.4), font_size=dp(33), halign="center", valign="middle")
        
        laser_options = BoxLayout(orientation="horizontal", spacing=dp(30), size_hint=(1, 0.6))
        
        laser_si_box = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(0.5, 1))
        self.laser_si = CheckBox(group="laser", size_hint=(0.3, 1))
        laser_si_lbl = Label(text="SI", size_hint=(0.7, 1), font_size=dp(27))
        laser_si_box.add_widget(self.laser_si)
        laser_si_box.add_widget(laser_si_lbl)
        
        laser_no_box = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(0.5, 1))
        self.laser_no = CheckBox(group="laser", size_hint=(0.3, 1))
        laser_no_lbl = Label(text="NO", size_hint=(0.7, 1), font_size=dp(27))
        laser_no_box.add_widget(self.laser_no)
        laser_no_box.add_widget(laser_no_lbl)
        
        laser_options.add_widget(laser_si_box)
        laser_options.add_widget(laser_no_box)
        
        laser_section.add_widget(laser_lbl)
        laser_section.add_widget(laser_options)

        # Pulsante SALVA centrato
        save_btn = Button( text="SALVA", size_hint=(None, None), size=(dp(200), dp(80)), background_color=(0, 1, 0, 1), font_size=dp(25), bold=True)

        # Aggiunta elementi al form box
        form_box.add_widget(op_box)
        form_box.add_widget(ord_box)
        form_box.add_widget(laser_section)
        form_box.add_widget(save_btn)

        # Pulsante HOME in basso a destra con margine
        home_btn = Button( text="HOME", size_hint=(None, None), size=(dp(200), dp(80)), pos_hint={"right": 0.95, "y": 0.05}, background_color=(1, 1, 0, 1), font_size=dp(25), bold=True)

        # Binding eventi
        home_btn.bind(on_press=self.home)
        save_btn.bind(on_press=self.salva_start)

        # Aggiunta widget al layout principale
        main_layout.add_widget(title)
        main_layout.add_widget(form_box)
        main_layout.add_widget(home_btn)

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

        print(f"[START] Operatore: {val_op}, Ordine: {val_ord}, Laser: {laser}, oggi: {oggi}, Start Time: {start_time}, Nome Operatore: {nome_operatore}")
        
        with open("record_start.csv", "a", newline="") as file:
            writer = csv.writer(file, delimiter='|')
            writer.writerow([val_op, val_ord, laser, oggi, start_time, nome_operatore])

        calcola_e_salva_media(val_op)

        # Svuotiamo i campi della sezione start
        self.numOp_in.text = ""
        self.numOrd_in.text = ""
        self.laser_si.active = False
        self.laser_no.active = False
        
        popup = Popup(title="CONFERMA", content=Label(text="Dati salvati correttamente."), size_hint=(None, None), pos_hint={"center_x":0.5, "center_y":0.5}, size=(300,200))
        popup.bind(on_dismiss=self.home)
        popup.open()

        
    def home(self, instance):
        self.manager.current = "main"

# Schermata Stop
class StopScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = FloatLayout()

        # Titolo centrato in alto
        title = Label( text="Registro di eventi STOP", size_hint=(None, None), size=(dp(500), dp(80)), pos_hint={"center_x": 0.5, "top": 0.95}, font_size=dp(80), bold=True, color=(1, 0, 0, 1))

        # box principale per i campi input
        form_box = BoxLayout( orientation="vertical", spacing=dp(20), size_hint=(None, None), size=(dp(400), dp(450)), pos_hint={"center_x": 0.5, "center_y": 0.43})

        # Campo Operatore
        op_box = BoxLayout(orientation="vertical", spacing=dp(20), size_hint=(1, None), height=dp(95))
        op_lbl = Label(text="Numero Operatore", size_hint=(1, 0.4), font_size=dp(40))
        self.numOp_in = TextInput(size_hint=(1, 0.6), font_size=dp(25))
        op_box.add_widget(op_lbl)
        op_box.add_widget(self.numOp_in)
        
        # Campo Ordine
        ord_box = BoxLayout(orientation="vertical", spacing=dp(20), size_hint=(1, None), height=dp(95))
        ord_lbl = Label(text="Numero ordine di produzione", size_hint=(1, 0.4), font_size=dp(40))
        self.numOrd_in = TextInput(size_hint=(1, 0.6), font_size=dp(25))
        ord_box.add_widget(ord_lbl)
        ord_box.add_widget(self.numOrd_in)

        # Campo Pezzi Prodotti
        prd_box = BoxLayout(orientation="vertical", spacing=dp(5), size_hint=(1, None), height=dp(80))
        prd_lbl = Label(text="Pezzi Prodotti", size_hint=(1, 0.4), font_size=dp(35))
        self.numPrd_in = TextInput(size_hint=(1, 0.6), font_size=dp(25))
        prd_box.add_widget(prd_lbl)
        prd_box.add_widget(self.numPrd_in)

        # Sezione Laser
        laser_section = BoxLayout(orientation="vertical", spacing=dp(10), size_hint=(1, None), height=dp(100))        
        laser_lbl = Label( text="L'ordine è di laseratura:", size_hint=(1, 0.4), font_size=dp(33), halign="center", valign="middle")
        
        laser_options = BoxLayout(orientation="horizontal", spacing=dp(30), size_hint=(1, 0.6))
        
        laser_si_box = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(0.5, 1))
        self.laser_si = CheckBox(group="laser", size_hint=(0.3, 1))
        laser_si_lbl = Label(text="SI", size_hint=(0.7, 1), font_size=dp(27))
        laser_si_box.add_widget(self.laser_si)
        laser_si_box.add_widget(laser_si_lbl)
        
        laser_no_box = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(0.5, 1))
        self.laser_no = CheckBox(group="laser", size_hint=(0.3, 1))
        laser_no_lbl = Label(text="NO", size_hint=(0.7, 1), font_size=dp(27))
        laser_no_box.add_widget(self.laser_no)
        laser_no_box.add_widget(laser_no_lbl)
        
        laser_options.add_widget(laser_si_box)
        laser_options.add_widget(laser_no_box)
        
        laser_section.add_widget(laser_lbl)
        laser_section.add_widget(laser_options)

        save_btn = Button( text="SALVA", size_hint=(None, None), size=(dp(200), dp(80)), background_color=(0, 1, 0, 1), font_size=dp(25), bold=True)
        home_btn = Button( text="HOME", size_hint=(None, None), size=(dp(200), dp(80)), pos_hint={"right": 0.95, "y": 0.05}, background_color=(1, 1, 0, 1), font_size=dp(25), bold=True)

        # Aggiunta elementi al form box
        home_btn.bind(on_press=self.home)
        save_btn.bind(on_press=self.salva_stop)

        form_box.add_widget(op_box)
        form_box.add_widget(ord_box)
        form_box.add_widget(prd_box)
        form_box.add_widget(laser_section)
        form_box.add_widget(save_btn)

        main_layout.add_widget(title)
        main_layout.add_widget(form_box)
        main_layout.add_widget(home_btn)
        
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

        # Ricerca del nome dell'operatore all'interno di operatori.csv
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

        print(f"[STOP] Operatore: {val_op}, Ordine: {val_ord}, Laser: {laser}, Pezzi Prodotti: {val_prd}, Data: {oggi},Stop Time: {stop_time}, Nome Operatore: {nome_operatore}")
        
        with open("record_stop.csv", "a", newline="") as file:
            writer = csv.writer(file, delimiter='|')
            writer.writerow([val_op, val_ord, laser, oggi, stop_time, nome_operatore])

        calcola_e_salva_media(val_op)

        # Svuotiamo i campi della sezione stop
        self.numOp_in.text = ""
        self.numOrd_in.text = ""
        self.numPrd_in.text = ""
        self.laser_si.active = False
        self.laser_no.active = False
        
        popup = Popup(title="CONFERMA", content=Label(text="Dati salvati correttamente."), size_hint=(None, None), pos_hint={"center_x":0.5, "center_y":0.5}, size=(300,200))
        popup.bind(on_dismiss=self.home)
        popup.open()

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