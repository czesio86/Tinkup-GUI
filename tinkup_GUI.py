import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import subprocess
import threading
import os
import sys
from PIL import Image, ImageTk  # Wymaga instalacji: pip install pillow

class TinkupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tinkup GUI - Retrotink firmware update tool")
        self.root.geometry("700x500")
        
        self.hex_file_path = tk.StringVar()
        self.teensy_model = tk.StringVar()
        self.status_var = tk.StringVar()
        self.status_var.set("Gotowe.")
        
        # Inicjalizacja języka (domyślnie polski)
        self.current_lang = "pl"
        
        # Słownik tłumaczeń
        self.translations = {
            "pl": {
                "window_title": "Tinkup GUI - Retrotink firmware update tool",
                "file_frame": "Plik Firmware (.hex)",
                "path_label": "Ścieżka:",
                "browse_button": "Przeglądaj...",
                "config_frame": "Konfiguracja",
                "model_label": "Port:",
                "auto_detect": "Auto-detect (Zalecane)",
                "start_button": "⚡ Rozpocznij Aktualizację ⚡",
                "output_frame": "Logi wyjściowe",
                "status_ready": "Gotowe.",
                "status_selected": "Wybrano plik: {}",
                "status_uploading": "Przesyłanie...",
                "status_success": "✅ Aktualizacja zakończona pomyślnie.",
                "status_error": "❌ Błąd podczas aktualizacji (Kod: {}). Sprawdź logi.",
                "error_title": "Błąd",
                "error_no_file": "Proszę wybrać plik HEX.",
                "file_dialog_title": "Wybierz plik firmware",
                "hex_files": "Pliki HEX",
                "all_files": "Wszystkie pliki",
                "cmd_start": "Uruchamianie komendy: {}",
                "process_end": "\n--- Proces zakończony (Kod: {}) ---\n",
                "execution_error": "Błąd wykonania: {}\nUpewnij się, że tinkup.py jest w tym samym folderze.\n",
                "critical_error": "❌ Błąd krytyczny",
                "language": "Język:"
            },
            "en": {
                "window_title": "Tinkup GUI - Retrotink firmware update tool",
                "file_frame": "Firmware File (.hex)",
                "path_label": "Path:",
                "browse_button": "Browse...",
                "config_frame": "Configuration",
                "model_label": "Port:",
                "auto_detect": "Auto-detect (Recommended)",
                "start_button": "⚡ Start Update ⚡",
                "output_frame": "Output Logs",
                "status_ready": "Ready.",
                "status_selected": "Selected file: {}",
                "status_uploading": "Uploading...",
                "status_success": "✅ Update completed successfully.",
                "status_error": "❌ Error during update (Code: {}). Check logs.",
                "error_title": "Error",
                "error_no_file": "Please select a HEX file.",
                "file_dialog_title": "Choose firmware file",
                "hex_files": "HEX Files",
                "all_files": "All Files",
                "cmd_start": "Running command: {}",
                "process_end": "\n--- Process finished (Code: {}) ---\n",
                "execution_error": "Execution error: {}\nMake sure tinkup.py is in the same folder.\n",
                "critical_error": "❌ Critical Error",
                "language": "Language:"
            }
        }

        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Górna ramka z flagami i logo ---
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        # Lewa strona: Przyciski zmiany języka
        lang_frame = ttk.Frame(top_frame)
        lang_frame.pack(side=tk.LEFT)
        
        # Etykieta z opisem języka
        ttk.Label(lang_frame, text=self.get_text("language")).pack(side=tk.LEFT, padx=5)
        
        # Emoji flag dla Polski (Unicode) - po lewej
        self.pl_button = ttk.Button(lang_frame, text="PL", width=3, command=lambda: self.change_language("pl"))
        self.pl_button.pack(side=tk.LEFT, padx=2)
        
        # Emoji flag dla UK (Unicode) - po lewej
        self.uk_button = ttk.Button(lang_frame, text="EN", width=3, command=lambda: self.change_language("en"))
        self.uk_button.pack(side=tk.LEFT, padx=2)
        
        # Prawa strona: Logo
        logo_frame = ttk.Frame(top_frame)
        logo_frame.pack(side=tk.RIGHT)
        
        # Próba załadowania logo.png
        try:
            logo_path = "logo.png"
            if os.path.exists(logo_path):
                # Załaduj obrazek i utwórz PhotoImage
                original_image = Image.open(logo_path)
                # Ustal maksymalne wymiary logo
                max_height = 150
                # Zachowaj proporcje przy skalowaniu
                width_percent = (max_height / float(original_image.size[1]))
                new_width = int((float(original_image.size[0]) * float(width_percent)))
                # Przeskaluj obrazek
                resized_image = original_image.resize((new_width, max_height), Image.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(resized_image)
                # Wyświetl logo
                self.logo_label = ttk.Label(logo_frame, image=self.logo_image)
                self.logo_label.pack(side=tk.RIGHT, padx=5)
            else:
                print(f"Uwaga: Plik '{logo_path}' nie został znaleziony. Logo nie będzie wyświetlane.")
        except Exception as e:
            print(f"Błąd podczas ładowania logo: {e}")

        # --- Sekcja wyboru pliku HEX ---
        self.file_frame = ttk.LabelFrame(main_frame, text=self.get_text("file_frame"), padding="10")
        self.file_frame.pack(fill=tk.X, pady=5)

        self.path_label = ttk.Label(self.file_frame, text=self.get_text("path_label"))
        self.path_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.hex_file_path, width=60)
        self.file_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        
        self.browse_button = ttk.Button(self.file_frame, text=self.get_text("browse_button"), command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=5)
        self.file_frame.columnconfigure(1, weight=1)

        # --- Sekcja wyboru modelu ---
        self.models = ["Auto-detect (Zalecane)", "TEENSY41", "TEENSY40", "TEENSY36", "TEENSY35", 
                  "TEENSY32", "TEENSY31", "TEENSY30", "TEENSYLC", "TEENSY2PP", "TEENSY2"]
        
        self.model_frame = ttk.LabelFrame(main_frame, text=self.get_text("config_frame"), padding="10")
        self.model_frame.pack(fill=tk.X, pady=5)
        
        self.model_label = ttk.Label(self.model_frame, text=self.get_text("model_label"))
        self.model_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.model_combo = ttk.Combobox(self.model_frame, textvariable=self.teensy_model, values=self.models, state="readonly")
        self.model_combo.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.teensy_model.set(self.models[0])

        # --- Przycisk Aktualizacji ---
        self.upload_button = ttk.Button(main_frame, text=self.get_text("start_button"), 
                                        command=self.start_upload_thread, style='Accent.TButton')
        self.upload_button.pack(pady=15)

        # --- Konsola wyjściowa (Logi) ---
        self.output_frame = ttk.LabelFrame(main_frame, text=self.get_text("output_frame"), padding="10")
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.output_text = scrolledtext.ScrolledText(self.output_frame, height=10, state=tk.DISABLED, wrap=tk.WORD, font=("Consolas", 10))
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # --- Pasek statusu ---
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Inicjalizacja statusu
        self.status_var.set(self.get_text("status_ready"))

    def get_text(self, key, *args):
        """Pobierz tekst w aktualnym języku z możliwością formatowania"""
        if key not in self.translations[self.current_lang]:
            # Jeśli klucz nie istnieje, dodaj go do słownika
            self.translations[self.current_lang][key] = key
                
        text = self.translations[self.current_lang][key]
        if args:
            return text.format(*args)
        return text

    def change_language(self, lang):
        """Zmień język interfejsu"""
        if lang == self.current_lang:
            return
            
        self.current_lang = lang
        
        # Aktualizacja tytułu okna
        self.root.title(self.get_text("window_title"))
        
        # Aktualizacja etykiet ramek
        self.file_frame.configure(text=self.get_text("file_frame"))
        self.model_frame.configure(text=self.get_text("config_frame"))
        self.output_frame.configure(text=self.get_text("output_frame"))
        
        # Aktualizacja etykiet i przycisków
        self.path_label.configure(text=self.get_text("path_label"))
        self.browse_button.configure(text=self.get_text("browse_button"))
        self.model_label.configure(text=self.get_text("model_label"))
        self.upload_button.configure(text=self.get_text("start_button"))
        
        # Aktualizacja listy modeli dla angielskiego
        if lang == "en":
            self.models[0] = "Auto-detect (Recommended)"
        else:
            self.models[0] = "Auto-detect (Zalecane)"
            
        # Zachowanie aktualnej wartości i aktualizacja listy modeli
        current_value = self.teensy_model.get()
        self.model_combo.configure(values=self.models)
        
        # Zachowanie wartości z uwzględnieniem tłumaczenia (Auto-detect)
        if current_value == "Auto-detect (Zalecane)" or current_value == "Auto-detect (Recommended)":
            self.teensy_model.set(self.models[0])
        else:
            self.teensy_model.set(current_value)
        
        # Aktualizacja statusu
        current_status = self.status_var.get()
        if current_status == self.translations["pl"]["status_ready"] or current_status == self.translations["en"]["status_ready"]:
            self.status_var.set(self.get_text("status_ready"))
        elif "Wybrano plik:" in current_status or "Selected file:" in current_status:
            # Wyciągnij nazwę pliku
            if "Wybrano plik:" in current_status:
                filename = current_status.replace("Wybrano plik:", "").strip()
            else:
                filename = current_status.replace("Selected file:", "").strip()
            self.status_var.set(self.get_text("status_selected", filename))

    def browse_file(self):
        """Otwiera menadżer plików, aby wybrać plik .hex."""
        filename = filedialog.askopenfilename(
            title=self.get_text("file_dialog_title"),
            filetypes=[(self.get_text("hex_files"), "*.hex"), (self.get_text("all_files"), "*.*")]
        )
        if filename:
            self.hex_file_path.set(filename)
            self.status_var.set(self.get_text("status_selected", os.path.basename(filename)))

    def append_output(self, message):
        """Dodaje tekst do konsoli wyjściowej."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message)
        self.output_text.see(tk.END) # Auto-scroll
        self.output_text.config(state=tk.DISABLED)

    def start_upload_thread(self):
        """Przygotowuje komendę i uruchamia proces aktualizacji w osobnym wątku."""
        hex_file = self.hex_file_path.get()
        if not hex_file:
            messagebox.showerror(self.get_text("error_title"), self.get_text("error_no_file"))
            return

        model = self.teensy_model.get()
        # Usuwamy "(Zalecane)" lub "(Recommended)" z auto-detect
        if "(" in model:
            model = "Auto-detect"

        command = [sys.executable, 'tinkup.py', hex_file]

        if model != "Auto-detect":
            command.extend(['-m', model])
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)
        self.append_output(self.get_text("cmd_start", ' '.join(command)) + "\n---\n")
        
        self.status_var.set(self.get_text("status_uploading"))
        self.upload_button.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.run_tinkup, args=(command,))
        thread.start()

    def run_tinkup(self, command):
        """Wykonuje skrypt tinkup.py i przechwytuje jego wyjście w czasie rzeczywistym."""
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            for line in iter(process.stdout.readline, ''):
                self.root.after(0, self.append_output, line)

            process.wait()

            if process.returncode == 0:
                status_message = self.get_text("status_success")
            else:
                status_message = self.get_text("status_error", process.returncode)
            
            self.root.after(0, lambda: self.status_var.set(status_message))
            self.root.after(0, self.append_output, self.get_text("process_end", process.returncode))

        except Exception as e:
            self.root.after(0, self.append_output, self.get_text("execution_error", str(e)))
            self.root.after(0, lambda: self.status_var.set(self.get_text("critical_error")))
        finally:
            self.root.after(0, lambda: self.upload_button.config(state=tk.NORMAL))

if __name__ == "__main__":
    # Sprawdzenie, czy tinkup.py istnieje w bieżącym katalogu
    if not os.path.exists("tinkup.py"):
        print("BŁĄD: Plik 'tinkup.py' nie został znaleziony w bieżącym katalogu.")
        print("Pobierz go z https://github.com/rmull/tinkup i umieść obok tinkup_gui.py")
        sys.exit(1)

    root = tk.Tk()
    
    # Konfiguracja stylu dla lepszego wyglądu
    style = ttk.Style()
    style.configure('Accent.TButton', font=('Helvetica', 12, 'bold'), padding=6)
    
    app = TinkupGUI(root)
    root.mainloop()
