import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from tkinter import *
from datetime import datetime, date
import csv
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Variabili globali
directory_export = r"\\192.168.12.9\Scambio-SAP\EXPORT_CSV\STAMPA_ETICHETTE\\"
export_ODP = "export_ODP_GEN.csv"
export_MM = "export_MM.csv"
tolleranza = 20

# Funzione per mandare mail in maniera automatica
def send_email(sender_email, sender_password, receiver_email, cc_email, subject, message):
    # Crea un oggetto MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Cc'] = cc_email
    msg['Subject'] = subject

    # Aggiungi il messaggio al corpo dell'email
    msg.attach(MIMEText(message, 'plain'))

    # Crea una connessione SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    # Accedi al tuo account email
    server.login(sender_email, sender_password)

    # Invia l'email
    server.send_message(msg)

    # Chiudi la connessione SMTP
    server.quit()

# Funzione per chiudere l'applicazione
def chiusura_programma(finestra):
    if messagebox.askyesno("Conferma uscita", "Sei sicuro di voler chiudere l'applicazione?"):
        finestra.destroy()

# Funzione per salvare i dati nella schermata START
def registra_dati_START(valore_operatore, valore_ordine, valore_laser, finestra):
    # Prendiamo i valori data e ora
    data_ora = datetime.now()
    data = data_ora.strftime("%d/%m/%Y")
    ora = data_ora.strftime("%H:%M:%S")

    # Verifichiamo che i campi siano stati inseriti correttamente
    regex_operatore = re.compile(r'^OP\d{6}$')
    regex_ordine = re.compile(r'^\d{7}$')

    # controllo delle due variabili
    if not valore_operatore or not valore_ordine:
        messagebox.showerror("Errore", "Inserire tutti i campi richiesti.")
        return
    elif not regex_operatore.match(valore_operatore):
        messagebox.showerror("Errore", "Il valore operatore non è valido.")
        return
    elif not regex_ordine.match(valore_ordine):
        messagebox.showerror("Errore", "Il valore ordine non è valido.")
        return
    
    # Verifichiamo se esiste già un record con lo stesso operatore e la stessa data
    try:
        with open("record_inizio_lavorazione.csv", "r") as file:
            reader = csv.reader(file, delimiter='|')
            for row in reader:
                if row[0] == valore_operatore and row[2] == data and row[4] == "false":
                    messagebox.showerror("Errore", "Attenzione! Ci sono operazioni ancora aperte nella giornata per questo operatore.")
                    return
                else:
                    if valore_laser == "laser_si":
                        if row[0] == (valore_operatore + "L") and row[1] == valore_ordine and row[4] == "false":
                            messagebox.showerror("Errore", "Attenzione! Ci sono operazioni ancora aperte nella giornata per questo operatore.")
                            return
                    else:
                        if row[0] == (valore_operatore + "L") and row[2] == data and row[4] == "false":
                            messagebox.showerror("Errore", "Attenzione! Ci sono operazioni ancora aperte nella giornata per questo operatore.")
                            return
    except FileNotFoundError:
        pass

    if valore_laser == "laser_si":
        valore_operatore = valore_operatore + "L"

    try:
        # Verifichiamo se il file contiene record relativi al giorno precedente o a giorni precedenti
        with open("record_inizio_lavorazione.csv", "r") as file:
            reader = csv.reader(file, delimiter='|')
            for row in reader:
                data_record = datetime.strptime(row[2], "%d/%m/%Y").date()
                oggi = date.today()
                if data_record < oggi:
                    # Puliamo il file
                    open("record_inizio_lavorazione.csv", "w").close()
                    break
    except FileNotFoundError:
        pass

    # Aggiungiamo il nuovo record al file csv
    with open("record_inizio_lavorazione.csv", "a", newline="") as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow([valore_operatore, valore_ordine, data, ora, "false"])

    # Visualizziamo un messaggio di conferma
    messagebox.showinfo("Conferma", "Dati registrati correttamente.")
    finestra.destroy()

# Funzione per salvare i dati nella schermata STOP
def registra_dati_STOP(valore_operatore_stop, valore_ordine_stop, valori_pezzi_stop, valore_laser_stop, finestra):
    # Prendiamo i valori data e ora
    data_ora = datetime.now()
    data_stop = data_ora.strftime("%d/%m/%Y")
    ora_stop = data_ora.strftime("%H:%M:%S")

    # Verifichiamo che i campi siano stati inseriti correttamente
    regex_operatore = re.compile(r'^OP\d{6}$')
    regex_ordine = re.compile(r'^\d{7}$')
    regex_pezzi = re.compile(r'^\d{1,9}$')

    # controllo delle tre variabili
    if not valore_operatore_stop or not valore_ordine_stop or not valori_pezzi_stop:
        messagebox.showerror("Errore", "Inserire tutti i campi richiesti.")
        return
    elif not regex_operatore.match(valore_operatore_stop):
        messagebox.showerror("Errore", "Il valore operatore non è valido.")
        return
    elif not regex_ordine.match(valore_ordine_stop):
        messagebox.showerror("Errore", "Il valore ordine non è valido.")
        return
    elif not regex_pezzi.match(valori_pezzi_stop):
        messagebox.showerror("Errore", "Il valore pezzi non è valido.")
        return
    
    if valore_laser_stop == "laser_si":
        valore_operatore_stop = valore_operatore_stop + "L"

    # Apriamo il file "record_inizio_lavorazione.csv" in modalità lettura
    with open("record_inizio_lavorazione.csv", "r") as file:
        reader = csv.reader(file, delimiter='|')
        found = False
        for row in reader:
            if row[0] == valore_operatore_stop and row[1] == valore_ordine_stop and row[2] == data_stop and row[4] == "false":
                found = True

                # Ci ricaviamo il codice articolo dell'ordine
                if valore_ordine_stop != "9999001":
                    with open(directory_export + export_ODP, "r") as file_odp:
                        reader_odp = csv.reader(file_odp, delimiter='|')
                        flag_odp = False
                        for index, odp in enumerate(reader_odp):
                            if index != 0:
                                if str(int(odp[0])) == valore_ordine_stop:
                                    flag_odp = True
                                    codice_articolo = odp[1]
                                    break
                        if flag_odp == False:
                            flag_art = False
                            while flag_art == False:
                                codice_articolo = simpledialog.askstring("Codice articolo", "Manca il codice articolo.\nInserirlo di seguito:")
                                if codice_articolo:
                                    flag_art = True

                            # Mandare mail per controllare se il codice inserito manualmente sia corretto oppure no
                            sender_email = "supp.avvisi.2023@gmail.com"
                            sender_password = "gvzcysjjcmqyzuba"
                            receiver_email = "pietro.sforzin@stampoplast.it"
                            cc_email = "mattia.davanzo@stampoplast.it"
                            subject = "PROG DATI ASSEMB - Codice manuale"
                            message = "Ciao,\n\nè stato inserito un codice manualmente.\nIl codice in oggetto è: " + codice_articolo + "\nL'ordine di riferimento è: " + valore_ordine_stop + "\n\nBuona giornata."
                            send_email(sender_email, sender_password, receiver_email, cc_email, subject, message)

                    # Ci ricaviamo la descrizione del codice articolo
                    desc_articolo = ""
                    with open(directory_export + export_MM, "r") as file_mm:
                        reader_mm = csv.reader(file_mm, delimiter='|')
                        for row_mm in reader_mm:
                            if row_mm[0] == codice_articolo:
                                desc_articolo = row_mm[1]
                                if desc_articolo.startswith('"'):
                                    desc_articolo = desc_articolo[1:]  # Rimuovi il primo carattere
                                if desc_articolo.endswith('"'):
                                    desc_articolo = desc_articolo[:-1]  # Rimuovi l'ultimo carattere
                                desc_articolo = desc_articolo.replace('"', '\'')  # Rimuovi la specifica stringa
                                break
                else:
                    codice_articolo = ""
                    desc_articolo = ""

                nome_operatore = ""
                valore_operatore_find = valore_operatore_stop
                if valore_laser_stop == "laser_si":
                    valore_operatore_find = valore_operatore_stop[:-1]      
                with open("operatori.csv", "r") as file_ope:
                    reader_ope = csv.reader(file_ope, delimiter='|')
                    for ope in reader_ope:
                        if ope[0] == valore_operatore_find:
                            nome_operatore = ope[1]
                            break
                
                # Aggiungiamo il nuovo record al file csv "record_fine_lavorazione.csv"
                with open("record_fine_lavorazione.csv", "a", newline="") as file_out:
                    writer = csv.writer(file_out, delimiter='|')
                    ora_start = datetime.strptime(row[3], '%H:%M:%S').time()
                    temp_ora_stop = datetime.strptime(ora_stop, '%H:%M:%S').time()
                    secondi_totali = (datetime.combine(datetime.today(), temp_ora_stop) - datetime.combine(datetime.today(), ora_start)).total_seconds()
                    tempo_ciclo = float(secondi_totali) / float(valori_pezzi_stop)
                    if valore_laser_stop == "laser_si":
                        valore_operatore_stop = valore_operatore_stop[:-1]
                    writer.writerow([valore_operatore_stop, valore_ordine_stop, valori_pezzi_stop, data_stop, row[3], ora_stop, str(int(secondi_totali)), str(str(round(tempo_ciclo, 1))).replace('.', ','), codice_articolo, desc_articolo, nome_operatore])
                    if valore_laser_stop == "laser_si":
                        valore_operatore_stop = valore_operatore_stop + "L"

                # Modifichiamo lo stato del record trovato dentro il file "record_inizio_lavorazione.csv"
                with open("record_inizio_lavorazione.csv", "r") as file_in:
                    rows = []
                    for r in csv.reader(file_in, delimiter='|'):
                        if r[0] == valore_operatore_stop and r[1] == valore_ordine_stop and r[2] == data_stop and r[4] == "false":
                            r[4] = "true"
                        rows.append(r)
                    # sovrascriviamo il file "record_inizio_lavorazione.csv" con i record aggiornati
                    with open("record_inizio_lavorazione.csv", "w", newline="") as file_in:
                        writer = csv.writer(file_in, delimiter='|')
                        writer.writerows(rows)

                # Gestione della tolleranza sul tempo ciclo
                if valore_ordine_stop != "9999001" and not valore_ordine_stop.startswith("2"):
                    with open("medie_lavorazioni.csv", "r") as file_medie:
                        reader_medie = csv.reader(file_medie, delimiter='|')
                        flag_medie = False
                        flag_errore = False
                        for righe in reader_medie:
                            if righe[0] == codice_articolo:
                                flag_medie = True
                                try:
                                    tempo_medio = float(righe[1])
                                except:
                                    flag_errore = True
                                    sender_email = "supp.avvisi.2023@gmail.com"
                                    sender_password = "gvzcysjjcmqyzuba"
                                    receiver_email = "pietro.sforzin@stampoplast.it"
                                    cc_email = "mattia.davanzo@stampoplast.it"
                                    subject = "PROG DATI ASSEMB - Errore nelle medie"
                                    message = "Ciao,\n\nc'è stato un errore nella lettura della media.\nIl codice in oggetto è: " + codice_articolo + "\n\nBuona giornata."
                                    send_email(sender_email, sender_password, receiver_email, cc_email, subject, message)
                                break
                        if flag_errore == False:
                            if flag_medie == False:
                                sender_email = "supp.avvisi.2023@gmail.com"
                                sender_password = "gvzcysjjcmqyzuba"
                                receiver_email = "pietro.sforzin@stampoplast.it"
                                cc_email = "mattia.davanzo@stampoplast.it"
                                subject = "PROG DATI ASSEMB - Codice nuovo"
                                message = "Ciao,\n\nè stato inserito un nuovo codice.\nIl codice in oggetto è: " + codice_articolo + "\nRicordarsi di aggiornare il file delle medie.\n\nBuona giornata."
                                send_email(sender_email, sender_password, receiver_email, cc_email, subject, message)
                            else:
                                min_tempo_medio = round(tempo_medio - (tempo_medio / 100 * tolleranza), 3)
                                max_tempo_medio = round(tempo_medio + (tempo_medio / 100 * tolleranza), 3)
                                if tempo_ciclo > max_tempo_medio or tempo_ciclo < min_tempo_medio:
                                    sender_email = "supp.avvisi.2023@gmail.com"
                                    sender_password = "gvzcysjjcmqyzuba"
                                    receiver_email = "pietro.sforzin@stampoplast.it"
                                    cc_email = "mattia.davanzo@stampoplast.it"
                                    subject = "PROG DATI ASSEMB - Media fuori tolleranza"
                                    message = "Ciao,\n\nè stato inserito un salvataggio con il tempo ciclo fuori tolleranza.\nIl numero d'ordine è: " + valore_ordine_stop + "\n\nTempo ciclo rilevato: " + str(round(tempo_ciclo, 1)) + " [s]\nMedia attesa: " + str(tempo_medio) + " [s]\nFuori tolleranza del: " + str(round(((tempo_ciclo / tempo_medio) - 1) * 100, 1)) + " [%]\n\nBuona giornata."
                                    send_email(sender_email, sender_password, receiver_email, cc_email, subject, message)

                # Visualizziamo un messaggio di conferma
                messagebox.showinfo("Conferma", "Dati registrati correttamente.")
                finestra.destroy()
                break

        if not found:
            messagebox.showerror("Errore", "Record non trovato o già chiuso.")

# Funzione per aprire la finestra START
def aprire_finestra_start():
    # Funzione per gestire evento "premi invio" su entry 1
    def my_function_01(event):
        numero_ordine_entry.focus_set()

    # Funzione per gestire evento "premi invio" su entry 2
    def my_function_02(event):
        pulsante_salva.focus_set()

    # Crea la finestra START
    finestra_start = tk.Toplevel()
    finestra_start.title("START")
    finestra_start.geometry("1280x1024")
    finestra_start.config(bg='#333333')
    finestra_start.wm_state("zoomed")
    finestra_start.grab_set()  # bloccare l'accesso alla finestra principale finché la finestra figlia è aperta

    # Carichiamo il logo per la finestra principale
    icon = PhotoImage(file = "Logotipo.png")
    finestra_start.iconphoto(False, icon)

    # Aggiungiamo il sottotitolo
    etichetta_01 = ttk.Label(finestra_start, text="Registro eventi START")
    etichetta_01.configure(font=('Helvetica', 36, 'bold'), foreground='#F5F5F5', background='#333333')
    etichetta_01.pack(pady=(40, 0))

    # Aggiungiamo la casella per il numero dell'operatore
    etichetta_02 = ttk.Label(finestra_start, text="Numero operatore:")
    etichetta_02.configure(font=('Helvetica', 28))
    etichetta_02.pack(pady=(40, 0))
    numero_operatore_entry = ttk.Entry(finestra_start)
    numero_operatore_entry.configure(font=('Helvetica', 28))
    numero_operatore_entry.pack(pady=(10, 0))
    numero_operatore_entry.focus_set()
    numero_operatore_entry.bind("<Return>", my_function_01)

    # Aggiungiamo la casella per il numero d'ordine
    etichetta_03 = ttk.Label(finestra_start, text="Numero ordine di produzione:")
    etichetta_03.configure(font=('Helvetica', 28))
    etichetta_03.pack(pady=(30, 0))
    numero_ordine_entry = ttk.Entry(finestra_start)
    numero_ordine_entry.configure(font=('Helvetica', 28))
    numero_ordine_entry.pack(pady=(10, 0))
    numero_ordine_entry.bind("<Return>", my_function_02)

    # Aggiungiamo il comando per i radiobuttons
    etichetta_04 = ttk.Label(finestra_start, text="L'ordine è di laseratura:")
    etichetta_04.configure(font=('Helvetica', 28))
    etichetta_04.pack(pady=(30, 0))

    selected_option = tk.StringVar(value="laser_no")
    options = [("NO", "laser_no"), ("SI", "laser_si")]
    radio_frame = ttk.Frame(finestra_start, style='My.TFrame')
    radio_frame.pack(pady=(10, 0))
    for text, value in options:
        radio_button = ttk.Radiobutton(radio_frame, text=text, value=value, variable=selected_option, style='My.TRadiobutton')
        radio_button.pack(anchor=tk.N)

    # Aggiungi i pulsanti
    pulsante_salva = ttk.Button(finestra_start, text="SALVA", command=lambda: registra_dati_START(numero_operatore_entry.get(), numero_ordine_entry.get(), selected_option.get(), finestra_start))
    pulsante_salva.pack(pady=(40, 0))
    pulsante_home = ttk.Button(finestra_start, text="HOME", command=finestra_start.destroy)
    pulsante_home.pack(pady=(60, 0))

# Funzione per aprire la finestra STOP
def aprire_finestra_stop():
    # Funzione per gestire evento "premi invio" su entry 1
    def my_function_01(event):
        numero_ordine_entry.focus_set()

    # Funzione per gestire evento "premi invio" su entry 2
    def my_function_02(event):
        numero_pezzi_entry.focus_set()
    
    # Funzione per gestire evento "premi invio" su entry 3
    def my_function_03(event):
        pulsante_salva.focus_set()

    # Crea la finestra STOP
    finestra_stop = tk.Toplevel()
    finestra_stop.title("STOP")
    finestra_stop.geometry("1280x1024")
    finestra_stop.config(bg='#333333')
    finestra_stop.wm_state("zoomed")
    finestra_stop.grab_set()  # bloccare l'accesso alla finestra principale finché la finestra figlia è aperta

    # Carichiamo il logo per la finestra principale
    icon = PhotoImage(file = "Logotipo.png")
    finestra_stop.iconphoto(False, icon)

    # Aggiungiamo il sottotitolo
    etichetta_01 = ttk.Label(finestra_stop, text="Registro eventi STOP")
    etichetta_01.configure(font=('Helvetica', 36, 'bold'), foreground='#F5F5F5', background='#333333')
    etichetta_01.pack(pady=(40, 0))

    # Aggiungiamo la casella per il numero dell'operatore
    etichetta_02 = ttk.Label(finestra_stop, text="Numero operatore:")
    etichetta_02.configure(font=('Helvetica', 28))
    etichetta_02.pack(pady=(40, 0))
    numero_operatore_entry = ttk.Entry(finestra_stop)
    numero_operatore_entry.configure(font=('Helvetica', 28))
    numero_operatore_entry.pack(pady=(10, 0))
    numero_operatore_entry.focus_set()
    numero_operatore_entry.bind("<Return>", my_function_01)

    # Aggiungiamo la casella per il numero d'ordine
    etichetta_03 = ttk.Label(finestra_stop, text="Numero ordine di produzione:")
    etichetta_03.configure(font=('Helvetica', 28))
    etichetta_03.pack(pady=(30, 0))
    numero_ordine_entry = ttk.Entry(finestra_stop)
    numero_ordine_entry.configure(font=('Helvetica', 28))
    numero_ordine_entry.pack(pady=(10, 0))
    numero_ordine_entry.bind("<Return>", my_function_02)

    # Aggiungiamo la casella per i pezzi prodotti
    etichetta_04 = ttk.Label(finestra_stop, text="Pezzi prodotti:")
    etichetta_04.configure(font=('Helvetica', 28))
    etichetta_04.pack(pady=(30, 0))
    numero_pezzi_entry = ttk.Entry(finestra_stop)
    numero_pezzi_entry.configure(font=('Helvetica', 28))
    numero_pezzi_entry.pack(pady=(10, 0))
    numero_pezzi_entry.bind("<Return>", my_function_03)

    # Aggiungiamo il comando per i radiobuttons
    etichetta_04 = ttk.Label(finestra_stop, text="L'ordine è di laseratura:")
    etichetta_04.configure(font=('Helvetica', 28))
    etichetta_04.pack(pady=(30, 0))

    selected_option = tk.StringVar(value="laser_no")
    options = [("NO", "laser_no"), ("SI", "laser_si")]
    radio_frame = ttk.Frame(finestra_stop, style='My.TFrame')
    radio_frame.pack(pady=(10, 0))
    for text, value in options:
        radio_button = ttk.Radiobutton(radio_frame, text=text, value=value, variable=selected_option, style='My.TRadiobutton')
        radio_button.pack(anchor=tk.N)
    
    # Aggiungi i pulsanti
    pulsante_salva = ttk.Button(finestra_stop, text="SALVA", command=lambda: registra_dati_STOP(numero_operatore_entry.get(), numero_ordine_entry.get(), numero_pezzi_entry.get(), selected_option.get(), finestra_stop))
    pulsante_salva.pack(pady=(40, 0))
    pulsante_home = ttk.Button(finestra_stop, text="HOME", command=finestra_stop.destroy)
    pulsante_home.pack(pady=(60, 0))

# Creiamo la finestra principale
finestra_principale = tk.Tk()
finestra_principale.title("HOME")
finestra_principale.geometry("1280x1024")
finestra_principale.config(bg='#333333')
finestra_principale.wm_state("zoomed")

# Carichiamo il logo per la finestra principale
icon = PhotoImage(file = "Logotipo.png")
finestra_principale.iconphoto(False, icon)

# Configuriamo il tema
ttk.Style().theme_use('clam')
ttk.Style().configure('TButton', font=('Helvetica', 36), foreground='#FF6600', background='#1E1E1E')
ttk.Style().configure('TLabel', font=('Helvetica', 36), foreground='#F5F5F5', background='#333333')
ttk.Style().map('TButton', foreground=[('pressed', '#FF6600'), ('active', '#FF6600')])
ttk.Style().configure('My.TFrame', background='#333333')
ttk.Style().configure('My.TRadiobutton', font=('Helvetica', 28), background='#333333', foreground='#F5F5F5')
ttk.Style().map('My.TRadiobutton', foreground=[('pressed', '#FF6600'), ('active', '#FF6600')])

# Creiamo le etichette
etichetta_01 = ttk.Label(finestra_principale, text="STAMPOPLAST")
etichetta_01.configure(font=('Helvetica', 60, 'bold'), foreground='#FF6600')
etichetta_01.pack(pady=(50, 0))
etichetta_02 = ttk.Label(finestra_principale, text="Reparto ASSEMBLAGGIO")
etichetta_02.pack(pady=(20, 0))
etichetta_03 = ttk.Label(finestra_principale, text="Registro lavorazioni")
etichetta_03.pack(pady=(80, 0))

# Creiamo i pulsanti
pulsante_01 = ttk.Button(finestra_principale, text="START", command=aprire_finestra_start)
pulsante_01.pack(pady=(60, 0))
pulsante_02 = ttk.Button(finestra_principale, text="STOP", command=aprire_finestra_stop)
pulsante_02.pack(pady=(40, 0))
pulsante_03 = ttk.Button(finestra_principale, text="EXIT", command=lambda: chiusura_programma(finestra_principale))
pulsante_03.pack(pady=(120, 0))

# Avviamo il mainloop
finestra_principale.mainloop()