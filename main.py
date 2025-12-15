import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import random
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw
import requests
from io import BytesIO
import threading
import queue

class ModernSmartMealPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("🍽️ SmartMeal-Planner - Repas sains & intelligents")
        
        # Définir la taille initiale
        self.root.geometry("1400x900")
        self.root.minsize(1000, 600)
        
        self.root.configure(bg='#f8fafc')
        
        # Variables pour le redimensionnement
        self.window_width = 1400
        self.window_height = 900
        self.cards_per_row = 3
        
        # Queue pour la communication entre threads
        self.image_queue = queue.Queue()
        
        # Images par défaut
        self.default_images = {}
        self.recipe_images = {}
        self.create_default_images()
        
        # Configuration des styles
        self.setup_styles()
        
        self.current_user = None
        self.setup_database()
        
        # Bind pour le redimensionnement
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Vérifier périodiquement la queue d'images
        self.root.after(100, self.check_image_queue)
        
        self.show_login_screen()
    
    def check_image_queue(self):
        """Vérifie périodiquement la queue d'images depuis le thread principal"""
        try:
            while True:
                recipe_id, size_name, photo = self.image_queue.get_nowait()
                key = f'{recipe_id}_{size_name}'
                self.recipe_images[key] = photo
                
                # Rafraîchir l'affichage si on est sur la page des recettes
                if hasattr(self, 'recipes_cards_frame') and self.recipes_cards_frame.winfo_exists():
                    self.refresh_recipes_display()
                    
        except queue.Empty:
            pass
        
        # Vérifier à nouveau dans 100ms
        self.root.after(100, self.check_image_queue)
    
    def create_default_images(self):
        """Crée des images par défaut"""
        # Tailles d'images
        self.image_sizes = {
            'large': (350, 200),
            'medium': (300, 180),
            'small': (250, 150)
        }
        
        # Couleurs par catégorie
        category_colors = {
            'Petit-déjeuner': '#FFB74D',
            'Déjeuner': '#4DB6AC',
            'Dîner': '#7986CB'
        }
        
        category_icons = {
            'Petit-déjeuner': '🥞',
            'Déjeuner': '🍲',
            'Dîner': '🍛'
        }
        
        for category, color in category_colors.items():
            for size_name, size in self.image_sizes.items():
                img = Image.new('RGB', size, color=color)
                draw = ImageDraw.Draw(img)
                
                # Ajouter l'icône
                try:
                    from PIL import ImageFont
                    font = ImageFont.truetype("arial.ttf", size[1] // 3)
                except:
                    font = ImageFont.load_default()
                
                icon = category_icons.get(category, '🍽️')
                text_bbox = draw.textbbox((0, 0), icon, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
                draw.text(position, icon, fill='white', font=font)
                
                photo = ImageTk.PhotoImage(img)
                self.default_images[f'{category}_{size_name}'] = photo
    
    def get_recipe_image(self, recipe_id, category, size='medium'):
        """Récupère l'image d'une recette"""
        key = f'{recipe_id}_{size}'
        
        if key in self.recipe_images:
            return self.recipe_images[key]
        else:
            # Fallback sur l'image par défaut
            return self.default_images.get(f'{category}_{size}', 
                                          self.default_images.get(f'Déjeuner_{size}'))
    
    def setup_styles(self):
        """Configure les styles modernes"""
        self.colors = {
            'primary': '#4361ee',
            'primary_dark': '#3a56d4',
            'primary_light': '#4cc9f0',
            'background': '#f8fafc',
            'card_bg': '#ffffff',
            'text_primary': '#1e293b',
            'text_secondary': '#64748b',
            'accent': '#f72585',
            'success': '#06d6a0',
            'warning': '#ff9e00',
            'info': '#7209b7',
            'danger': '#ef476f',
            'light_gray': '#e2e8f0'
        }
    
    def setup_database(self):
        """Initialise la base de données"""
        self.conn = sqlite3.connect('meal_planner.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Table utilisateurs
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                height INTEGER,
                weight REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table recettes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL,
                calories INTEGER,
                prep_time INTEGER,
                difficulty TEXT
            )
        ''')
        
        # Table inscriptions
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plan_name TEXT NOT NULL,
                plan_text TEXT NOT NULL,
                calories_target INTEGER,
                days_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Peupler avec des données d'exemple
        self.populate_sample_recipes()
        self.conn.commit()
    
    def populate_sample_recipes(self):
        """Remplit la base avec des recettes d'exemple"""
        sample_recipes = [
            ('Bowl Avoine Énergie', 'Petit-déjeuner', 
             'Flocons davoine, Lait damande, Myrtilles, Noix, Miel', 
             'Cuire lavoine 8 min, ajouter fruits et noix, arroser de miel', 
             320, 10, 'Facile'),
            
            ('Smoothie Vert Vitalité', 'Petit-déjeuner', 
             'Épinards, Banane, Avocat, Lait végétal, Graines de chia', 
             'Mixer tous les ingrédients 2 min jusquà consistance lisse', 
             280, 5, 'Facile'),
            
            ('Toast Avocat Œuf', 'Petit-déjeuner', 
             'Pain complet, Avocat, Œuf, Graines de sésame, Piment', 
             'Griller pain, écraser avocat, cuire œuf au plat, assembler', 
             350, 12, 'Facile'),
            
            ('Bowl Buddha Coloré', 'Déjeuner', 
             'Quinoa, Patate douce, Avocat, Carotte, Sauce tahini', 
             'Cuire quinoa et patate, couper légumes, assembler avec sauce', 
             420, 25, 'Moyen'),
            
            ('Wrap Poulet Caesar', 'Déjeuner', 
             'Tortilla, Poulet grillé, Laitue, Parmesan, Sauce caesar light', 
             'Faire griller poulet, chauffer tortilla, garnir et rouler', 
             380, 15, 'Facile'),
            
            ('Salade Quinoa Feta', 'Déjeuner', 
             'Quinoa, Feta, Concombre, Olives, Huile dolive, Citron', 
             'Cuire quinoa, mélanger avec légumes et feta, assaisonner', 
             320, 20, 'Facile'),
            
            ('Saumon Teriyaki', 'Dîner', 
             'Saumon, Brocoli, Riz basmati, Sauce teriyaki, Sésame', 
             'Cuire riz, faire revenir saumon et brocoli, napper de sauce', 
             450, 30, 'Moyen'),
            
            ('Curry Végétarien', 'Dîner', 
             'Lait de coco, Curcuma, Légumes de saison, Riz, Coriandre', 
             'Faire revenir épices, ajouter légumes et lait de coco, mijoter', 
             380, 35, 'Moyen'),
            
            ('Poke Bowl Thon', 'Dîner', 
             'Thon, Riz vinaigré, Avocat, Algues, Graines, Sauce soja', 
             'Préparer riz, couper thon et avocat, assembler en couches', 
             400, 20, 'Facile'),
        ]
        
        self.cursor.execute('SELECT COUNT(*) FROM recipes')
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            for recipe in sample_recipes:
                self.cursor.execute('''
                    INSERT INTO recipes 
                    (name, category, ingredients, instructions, calories, prep_time, difficulty)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', recipe)
    
    def create_recipe_card(self, parent, recipe_data):
        """Crée une carte de recette moderne - VERSION CORRIGÉE"""
        recipe_id, name, category, ingredients, instructions, calories, prep_time, difficulty = recipe_data
        
        # Créer la carte principale - SANS CURSEUR SUR LA CARTE PRINCIPALE
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief='flat',
                       highlightbackground=self.colors['light_gray'], 
                       highlightthickness=1, bd=0)
        
        # Image de la recette (utilisation d'image par défaut)
        recipe_image = self.get_recipe_image(recipe_id, category)
        
        # Frame pour l'image
        image_frame = tk.Frame(card, bg=self.colors['card_bg'], height=180)
        image_frame.pack(fill='x')
        image_frame.pack_propagate(False)
        
        # Label pour l'image
        img_label = tk.Label(image_frame, image=recipe_image, bg=self.colors['card_bg'])
        img_label.image = recipe_image
        img_label.pack(fill='both', expand=True)
        
        # Badge de catégorie
        category_bg = {
            'Petit-déjeuner': self.colors['warning'],
            'Déjeuner': self.colors['success'],
            'Dîner': self.colors['info']
        }.get(category, self.colors['primary'])
        
        category_label = tk.Label(image_frame, text=category.upper(), 
                                 font=('Segoe UI', 10, 'bold'),
                                 bg=category_bg, fg='white', padx=10, pady=3)
        category_label.place(relx=0, rely=0, anchor='nw', x=10, y=10)
        
        # Contenu de la carte
        content_frame = tk.Frame(card, bg=self.colors['card_bg'], padx=15, pady=15)
        content_frame.pack(fill='both', expand=True)
        
        # Nom de la recette
        name_label = tk.Label(content_frame, text=name, 
                             font=('Segoe UI', 16, 'bold'),
                             bg=self.colors['card_bg'], fg=self.colors['text_primary'],
                             wraplength=280, justify='left')
        name_label.pack(anchor='w', pady=(0, 10))
        
        # Statistiques
        stats_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        stats_frame.pack(fill='x', pady=(0, 15))
        
        stats_data = [
            ("🔥", f"{calories} cal", self.colors['danger']),
            ("⏱️", f"{prep_time} min", self.colors['warning']),
            ("⚡", difficulty, self.colors['success'])
        ]
        
        for icon, value, color in stats_data:
            stat_item = tk.Frame(stats_frame, bg=self.colors['card_bg'])
            stat_item.pack(side='left', padx=(0, 15))
            
            tk.Label(stat_item, text=icon, font=('Segoe UI', 12),
                    bg=self.colors['card_bg'], fg=color).pack(side='left')
            tk.Label(stat_item, text=value, font=('Segoe UI', 11),
                    bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack(side='left', padx=(5, 0))
        
        # Ingrédients (tronqués)
        ingredients_text = ingredients[:60] + "..." if len(ingredients) > 60 else ingredients
        ingredients_label = tk.Label(content_frame, text=ingredients_text,
                                    font=('Segoe UI', 10),
                                    bg=self.colors['card_bg'], fg=self.colors['text_secondary'],
                                    wraplength=280, justify='left', height=2)
        ingredients_label.pack(anchor='w', fill='x', pady=(0, 15))
        
        # Bouton Voir détails - CORRECTION PRINCIPALE
        details_btn = tk.Frame(content_frame, bg=self.colors['primary'], relief='flat',
                              cursor='hand2')
        details_btn.pack(fill='x', pady=(5, 0))
        
        btn_content = tk.Frame(details_btn, bg=self.colors['primary'])
        btn_content.pack(fill='both', expand=True, padx=15, pady=10)
        
        details_text = tk.Label(btn_content, text="📖 Voir les détails", 
                               font=('Segoe UI', 11, 'bold'),
                               bg=self.colors['primary'], fg='white')
        details_text.pack(side='left')
        
        arrow = tk.Label(btn_content, text="→", 
                        font=('Segoe UI', 14, 'bold'),
                        bg=self.colors['primary'], fg='white')
        arrow.pack(side='right')
        
        # Effets hover seulement sur le bouton
        def on_enter(e):
            details_btn.configure(bg=self.colors['primary_dark'])
            btn_content.configure(bg=self.colors['primary_dark'])
            details_text.configure(bg=self.colors['primary_dark'])
            arrow.configure(bg=self.colors['primary_dark'])
        
        def on_leave(e):
            details_btn.configure(bg=self.colors['primary'])
            btn_content.configure(bg=self.colors['primary'])
            details_text.configure(bg=self.colors['primary'])
            arrow.configure(bg=self.colors['primary'])
        
        # Binding du clic seulement sur le bouton
        def on_click(e):
            self.show_recipe_details(recipe_id)
        
        # Appliquer les bindings seulement aux éléments du bouton
        for widget in [details_btn, btn_content, details_text, arrow]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.bind('<Button-1>', on_click)
        
        # NE PAS mettre de binding sur la carte entière
        # NE PAS mettre de binding sur les autres éléments (name_label, ingredients_label, etc.)
        
        return card
    
    def show_recipe_details(self, recipe_id):
        """Affiche les détails d'une recette"""
        print(f"Tentative d'affichage de la recette ID: {recipe_id}")  # Debug
        
        self.cursor.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,))
        recipe = self.cursor.fetchone()
        
        if not recipe:
            messagebox.showerror("Erreur", "Recette non trouvée")
            return
        
        print(f"Recette trouvée: {recipe[1]}")  # Debug
        
        popup = tk.Toplevel(self.root)
        popup.title(f"📖 {recipe[1]}")
        popup.geometry("800x700")
        popup.configure(bg=self.colors['background'])
        popup.transient(self.root)  # Rend la fenêtre modale
        popup.grab_set()  # Bloque l'interaction avec la fenêtre principale
        
        # Centrer la fenêtre
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'{width}x{height}+{x}+{y}')
        
        # Container principal
        main_container = tk.Frame(popup, bg=self.colors['background'])
        main_container.pack(fill='both', expand=True)
        
        # Canvas pour le scroll
        canvas = tk.Canvas(main_container, bg=self.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=self.colors['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Contenu
        content_frame = tk.Frame(scrollable_frame, bg=self.colors['background'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Titre et catégorie
        title_frame = tk.Frame(content_frame, bg=self.colors['background'])
        title_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(title_frame, text=recipe[1], font=('Segoe UI', 28, 'bold'),
                bg=self.colors['background'], fg=self.colors['text_primary']).pack(side='left')
        
        category_bg = {
            'Petit-déjeuner': self.colors['warning'],
            'Déjeuner': self.colors['success'],
            'Dîner': self.colors['info']
        }.get(recipe[2], self.colors['primary'])
        
        tk.Label(title_frame, text=recipe[2], font=('Segoe UI', 12, 'bold'),
                bg=category_bg, fg='white', padx=15, pady=6).pack(side='right')
        
        # Statistiques
        stats_frame = tk.Frame(content_frame, bg=self.colors['background'])
        stats_frame.pack(fill='x', pady=(0, 25))
        
        stats_data = [
            ("🔥", "Calories", f"{recipe[5]} cal", self.colors['danger']),
            ("⏱️", "Temps", f"{recipe[6]} min", self.colors['warning']),
            ("⚡", "Difficulté", recipe[7], self.colors['success'])
        ]
        
        for icon, label, value, color in stats_data:
            stat_card = tk.Frame(stats_frame, bg=self.colors['card_bg'], padx=20, pady=15,
                                highlightbackground=self.colors['light_gray'], 
                                highlightthickness=1)
            stat_card.pack(side='left', padx=(0, 15))
            
            tk.Label(stat_card, text=icon, font=('Segoe UI', 18),
                    bg=self.colors['card_bg'], fg=color).pack()
            tk.Label(stat_card, text=label, font=('Segoe UI', 11),
                    bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack()
            tk.Label(stat_card, text=value, font=('Segoe UI', 14, 'bold'),
                    bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack()
        
        # Section ingrédients
        tk.Label(content_frame, text="🥕 Ingrédients", font=('Segoe UI', 18, 'bold'),
                bg=self.colors['background'], fg=self.colors['text_primary']).pack(anchor='w', pady=(20, 10))
        
        ingredients_card = tk.Frame(content_frame, bg=self.colors['card_bg'], padx=20, pady=15,
                                   highlightbackground=self.colors['light_gray'], 
                                   highlightthickness=1)
        ingredients_card.pack(fill='x', pady=(0, 20))
        
        ingredients_text = scrolledtext.ScrolledText(ingredients_card, height=6, font=('Segoe UI', 11),
                                                    bg=self.colors['card_bg'], fg=self.colors['text_primary'],
                                                    insertbackground=self.colors['primary'], wrap='word')
        ingredients_text.pack(fill='x')
        ingredients_text.insert(1.0, recipe[3])
        ingredients_text.config(state='disabled')
        
        # Section instructions
        tk.Label(content_frame, text="📝 Instructions", font=('Segoe UI', 18, 'bold'),
                bg=self.colors['background'], fg=self.colors['text_primary']).pack(anchor='w', pady=(20, 10))
        
        instructions_card = tk.Frame(content_frame, bg=self.colors['card_bg'], padx=20, pady=15,
                                    highlightbackground=self.colors['light_gray'], 
                                    highlightthickness=1)
        instructions_card.pack(fill='both', expand=True)
        
        instructions_text = scrolledtext.ScrolledText(instructions_card, height=10, font=('Segoe UI', 11),
                                                     bg=self.colors['card_bg'], fg=self.colors['text_primary'],
                                                     insertbackground=self.colors['primary'], wrap='word')
        instructions_text.pack(fill='both', expand=True)
        instructions_text.insert(1.0, recipe[4])
        instructions_text.config(state='disabled')
        
        # Bouton de fermeture
        close_btn = tk.Frame(content_frame, bg=self.colors['primary'], relief='flat',
                            cursor='hand2')
        close_btn.pack(fill='x', pady=(20, 0))
        
        close_label = tk.Label(close_btn, text="✕ Fermer", font=('Segoe UI', 12, 'bold'),
                              bg=self.colors['primary'], fg='white', padx=20, pady=12)
        close_label.pack()
        
        def close_popup(e):
            popup.destroy()
        
        close_btn.bind('<Button-1>', close_popup)
        close_label.bind('<Button-1>', close_popup)
        
        # Effet hover pour le bouton
        def on_enter_close(e):
            close_btn.configure(bg=self.colors['danger'])
            close_label.configure(bg=self.colors['danger'])
        
        def on_leave_close(e):
            close_btn.configure(bg=self.colors['primary'])
            close_label.configure(bg=self.colors['primary'])
        
        close_btn.bind('<Enter>', on_enter_close)
        close_btn.bind('<Leave>', on_leave_close)
        close_label.bind('<Enter>', on_enter_close)
        close_label.bind('<Leave>', on_leave_close)
        
        # Activer le scroll avec la molette
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Permettre de fermer avec Échap
        def on_escape(event):
            if event.keysym == 'Escape':
                popup.destroy()
        
        popup.bind('<Key>', on_escape)
        popup.focus_set()
        
        print("Popup créée avec succès")  # Debug
    
    # ... [Le reste des méthodes reste inchangé, sauf show_recipe_details] ...
    
    def create_card(self, parent, title, subtitle, icon, color, command=None):
        """Crée une carte moderne"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief='flat', 
                       highlightbackground=self.colors['light_gray'], 
                       highlightthickness=1, bd=0)
        
        # Icône
        tk.Label(card, text=icon, font=('Segoe UI', 28), 
                bg=self.colors['card_bg'], fg=color).pack(pady=(25, 15))
        
        # Titre
        tk.Label(card, text=title, font=('Segoe UI', 16, 'bold'), 
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(pady=5)
        
        # Sous-titre
        tk.Label(card, text=subtitle, font=('Segoe UI', 12), 
                bg=self.colors['card_bg'], fg=self.colors['text_secondary'],
                wraplength=200).pack(pady=(0, 25))
        
        if command:
            for widget in [card, card.winfo_children()[0], card.winfo_children()[1], card.winfo_children()[2]]:
                widget.bind('<Button-1>', lambda e: command())
                widget.configure(cursor='hand2')
            
            # Effet hover
            def on_enter(e):
                e.widget.configure(bg=self.colors['light_gray'])
                for child in e.widget.winfo_children():
                    child.configure(bg=self.colors['light_gray'])
            
            def on_leave(e):
                e.widget.configure(bg=self.colors['card_bg'])
                for child in e.widget.winfo_children():
                    child.configure(bg=self.colors['card_bg'])
            
            card.bind('<Enter>', on_enter)
            card.bind('<Leave>', on_leave)
        
        return card
    
    def show_login_screen(self):
        """Affiche l'écran de connexion"""
        self.clear_window()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True)
        
        # Container central
        container = tk.Frame(main_frame, bg=self.colors['background'])
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo et titre
        tk.Label(container, text="🍽️", font=('Segoe UI', 48),
                bg=self.colors['background'], fg=self.colors['primary']).pack(pady=(0, 10))
        
        tk.Label(container, text="SmartMeal-Planner", 
                font=('Segoe UI', 32, 'bold'), 
                bg=self.colors['background'], fg=self.colors['primary']).pack(pady=(0, 5))
        
        tk.Label(container, text="Repas sains & intelligents", 
                font=('Segoe UI', 16), 
                bg=self.colors['background'], fg=self.colors['text_secondary']).pack(pady=(0, 50))
        
        # Cartes d'action
        actions_frame = tk.Frame(container, bg=self.colors['background'])
        actions_frame.pack(pady=20)
        
        # Carte Connexion
        login_card = self.create_card(
            actions_frame, "Se connecter", "Accédez à votre compte", "🔐", self.colors['primary'],
            self.show_login_form
        )
        login_card.grid(row=0, column=0, padx=15, pady=10, sticky='nsew')
        
        # Carte Inscription
        register_card = self.create_card(
            actions_frame, "Créer un compte", "Commencez votre voyage santé", "🚀", self.colors['accent'],
            self.show_register_form
        )
        register_card.grid(row=0, column=1, padx=15, pady=10, sticky='nsew')
        
        # Carte Démo
        demo_card = self.create_card(
            actions_frame, "Mode Démo", "Essayez sans compte", "🎯", self.colors['success'],
            self.demo_mode
        )
        demo_card.grid(row=0, column=2, padx=15, pady=10, sticky='nsew')
        
        # Footer
        tk.Label(main_frame, text="🍎 Mangez mieux. Vivez mieux. 🏃‍♂️", 
                font=('Segoe UI', 12), 
                bg=self.colors['background'], fg=self.colors['text_secondary']).pack(side='bottom', pady=20)
    
    def show_login_form(self):
        """Affiche le formulaire de connexion"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True, padx=50, pady=50)
        
        # Retour
        back_btn = tk.Label(main_frame, text="← Retour", font=('Segoe UI', 12),
                           bg=self.colors['background'], fg=self.colors['primary'],
                           cursor='hand2')
        back_btn.bind('<Button-1>', lambda e: self.show_login_screen())
        back_btn.pack(anchor='nw')
        
        # Container formulaire
        form_container = tk.Frame(main_frame, bg=self.colors['background'])
        form_container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Titre
        tk.Label(form_container, text="🔐 Connexion", font=('Segoe UI', 28, 'bold'),
                bg=self.colors['background'], fg=self.colors['primary']).pack(pady=(0, 30))
        
        # Carte formulaire
        form_card = tk.Frame(form_container, bg=self.colors['card_bg'], relief='flat',
                            highlightbackground=self.colors['light_gray'], 
                            highlightthickness=1, padx=40, pady=40)
        form_card.pack(pady=20)
        
        # Champs
        tk.Label(form_card, text="Email", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(anchor='w', pady=(10, 5))
        
        self.email_entry = ttk.Entry(form_card, width=30, font=('Segoe UI', 12))
        self.email_entry.pack(pady=5, fill='x')
        
        tk.Label(form_card, text="Mot de passe", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(anchor='w', pady=(15, 5))
        
        self.password_entry = ttk.Entry(form_card, width=30, show='•', font=('Segoe UI', 12))
        self.password_entry.pack(pady=5, fill='x')
        
        # Bouton connexion
        ttk.Button(form_card, text="Se connecter", 
                  command=self.login).pack(pady=30, fill='x')
        
        # Lien inscription
        register_link = tk.Label(form_card, text="Pas de compte ? Créer un compte", 
                                font=('Segoe UI', 10), bg=self.colors['card_bg'], 
                                fg=self.colors['primary'], cursor='hand2')
        register_link.bind('<Button-1>', lambda e: self.show_register_form())
        register_link.pack()
    
    def show_register_form(self):
        """Affiche le formulaire d'inscription"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True, padx=50, pady=50)
        
        # Retour
        back_btn = tk.Label(main_frame, text="← Retour", font=('Segoe UI', 12),
                           bg=self.colors['background'], fg=self.colors['primary'],
                           cursor='hand2')
        back_btn.bind('<Button-1>', lambda e: self.show_login_screen())
        back_btn.pack(anchor='nw')
        
        # Container formulaire
        form_container = tk.Frame(main_frame, bg=self.colors['background'])
        form_container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Titre
        tk.Label(form_container, text="🚀 Créer un compte", font=('Segoe UI', 28, 'bold'),
                bg=self.colors['background'], fg=self.colors['primary']).pack(pady=(0, 30))
        
        # Carte formulaire
        form_card = tk.Frame(form_container, bg=self.colors['card_bg'], relief='flat',
                            highlightbackground=self.colors['light_gray'], 
                            highlightthickness=1, padx=40, pady=40)
        form_card.pack(pady=20)
        
        # Grille pour les champs
        form_grid = tk.Frame(form_card, bg=self.colors['card_bg'])
        form_grid.pack(fill='x')
        
        # Champs
        tk.Label(form_grid, text="Prénom", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=0, column=0, sticky='w', pady=10)
        tk.Label(form_grid, text="Nom", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=0, column=1, sticky='w', pady=10, padx=(20,0))
        
        self.firstname_entry = ttk.Entry(form_grid, width=20, font=('Segoe UI', 12))
        self.firstname_entry.grid(row=1, column=0, sticky='w')
        
        self.lastname_entry = ttk.Entry(form_grid, width=20, font=('Segoe UI', 12))
        self.lastname_entry.grid(row=1, column=1, sticky='w', padx=(20,0))
        
        # Email
        tk.Label(form_grid, text="Email", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=2, column=0, sticky='w', pady=(20,5))
        self.reg_email_entry = ttk.Entry(form_grid, width=42, font=('Segoe UI', 12))
        self.reg_email_entry.grid(row=3, column=0, columnspan=2, sticky='we')
        
        # Mot de passe
        tk.Label(form_grid, text="Mot de passe", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=4, column=0, sticky='w', pady=(20,5))
        self.reg_password_entry = ttk.Entry(form_grid, width=42, show='•', font=('Segoe UI', 12))
        self.reg_password_entry.grid(row=5, column=0, columnspan=2, sticky='we')
        
        # Taille et Poids
        tk.Label(form_grid, text="Taille (cm)", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=6, column=0, sticky='w', pady=(20,5))
        tk.Label(form_grid, text="Poids (kg)", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=6, column=1, sticky='w', pady=(20,5), padx=(20,0))
        
        self.height_entry = ttk.Entry(form_grid, width=20, font=('Segoe UI', 12))
        self.height_entry.grid(row=7, column=0, sticky='w')
        
        self.weight_entry = ttk.Entry(form_grid, width=20, font=('Segoe UI', 12))
        self.weight_entry.grid(row=7, column=1, sticky='w', padx=(20,0))
        
        # Bouton inscription
        ttk.Button(form_card, text="Créer mon compte",
                  command=self.register).pack(pady=30, fill='x')
        
        # Lien connexion
        login_link = tk.Label(form_card, text="Déjà un compte ? Se connecter", 
                             font=('Segoe UI', 10), bg=self.colors['card_bg'], 
                             fg=self.colors['primary'], cursor='hand2')
        login_link.bind('<Button-1>', lambda e: self.show_login_form())
        login_link.pack()
    
    def login(self):
        """Gère la connexion"""
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Erreur", "📝 Veuillez remplir tous les champs")
            return
        
        self.cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = self.cursor.fetchone()
        
        if user:
            self.current_user = {
                'id': user[0],
                'firstname': user[1],
                'lastname': user[2],
                'email': user[3],
                'height': user[5],
                'weight': user[6]
            }
            messagebox.showinfo("Succès", f"🎉 Bienvenue {user[1]} !")
            self.show_dashboard()
        else:
            messagebox.showerror("Erreur", "❌ Email ou mot de passe incorrect")
    
    def register(self):
        """Gère l'inscription"""
        firstname = self.firstname_entry.get()
        lastname = self.lastname_entry.get()
        email = self.reg_email_entry.get()
        password = self.reg_password_entry.get()
        height = self.height_entry.get()
        weight = self.weight_entry.get()
        
        if not all([firstname, lastname, email, password, height, weight]):
            messagebox.showerror("Erreur", "📝 Veuillez remplir tous les champs")
            return
        
        try:
            height_int = int(height)
            weight_float = float(weight)
            
            self.cursor.execute('''
                INSERT INTO users (firstname, lastname, email, password, height, weight)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (firstname, lastname, email, password, height_int, weight_float))
            self.conn.commit()
            
            messagebox.showinfo("Succès", "🎉 Compte créé avec succès !")
            self.show_login_screen()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "📧 Cet email est déjà utilisé")
        except ValueError:
            messagebox.showerror("Erreur", "🔢 Taille et poids doivent être des nombres valides")
    
    def demo_mode(self):
        """Mode démo sans connexion"""
        self.current_user = {'firstname': 'Invité', 'id': 0}
        self.show_dashboard()
    
    def show_dashboard(self):
        """Affiche le tableau de bord"""
        self.clear_window()
        
        # Barre latérale
        sidebar = tk.Frame(self.root, bg=self.colors['card_bg'], width=250,
                          highlightbackground=self.colors['light_gray'], 
                          highlightthickness=1)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Logo sidebar
        tk.Label(sidebar, text="🍽️", font=('Segoe UI', 24),
                bg=self.colors['card_bg'], fg=self.colors['primary']).pack(pady=(30, 10))
        
        tk.Label(sidebar, text="SmartMeal", font=('Segoe UI', 16, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['primary']).pack(pady=(0, 30))
        
        # Menu sidebar
        menu_items = [
            ("📊 Tableau de bord", self.show_dashboard),
            ("🍽️ Générer repas", self.show_meal_generator),
            ("📖 Recettes", self.show_recipes),
            ("💾 Mes inscriptions", self.show_saved_plans),
            ("👤 Profil", self.show_profile),
            ("🚪 Déconnexion", self.show_login_screen)
        ]
        
        for text, command in menu_items:
            btn = tk.Label(sidebar, text=text, font=('Segoe UI', 12),
                          bg=self.colors['card_bg'], fg=self.colors['text_secondary'],
                          cursor='hand2', padx=20, pady=15)
            btn.bind('<Button-1>', lambda e, cmd=command: cmd())
            btn.pack(fill='x')
            btn.bind('<Enter>', lambda e: e.widget.configure(bg=self.colors['primary'], fg='white'))
            btn.bind('<Leave>', lambda e: e.widget.configure(bg=self.colors['card_bg'], fg=self.colors['text_secondary']))
        
        # Contenu principal
        main_content = tk.Frame(self.root, bg=self.colors['background'])
        main_content.pack(side='right', fill='both', expand=True, padx=30, pady=30)
        
        # En-tête
        header = tk.Frame(main_content, bg=self.colors['background'])
        header.pack(fill='x', pady=(0, 30))
        
        tk.Label(header, text=f"👋 Bonjour, {self.current_user['firstname']} !", 
                font=('Segoe UI', 24, 'bold'), bg=self.colors['background'], 
                fg=self.colors['text_primary']).pack(side='left')
        
        # Cartes de statistiques
        stats_frame = tk.Frame(main_content, bg=self.colors['background'])
        stats_frame.pack(fill='x', pady=(0, 30))
        
        # Compter le nombre d'inscriptions
        self.cursor.execute('SELECT COUNT(*) FROM saved_plans WHERE user_id = ?', 
                          (self.current_user['id'],))
        plan_count = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM recipes')
        recipe_count = self.cursor.fetchone()[0]
        
        stats_cards = [
            ("📅", str(plan_count), "Plans sauvegardés", self.colors['primary']),
            ("🍽️", str(recipe_count), "Recettes disponibles", self.colors['success']),
            ("🔥", "45", "Jours suivis", self.colors['warning']),
            ("🎯", "85%", "Objectif atteint", self.colors['info'])
        ]
        
        for i, (icon, value, text, color) in enumerate(stats_cards):
            card = self.create_stats_card(stats_frame, icon, value, text, color)
            card.grid(row=0, column=i, padx=10, sticky='nsew')
        
        # Actions rapides
        tk.Label(main_content, text="🚀 Actions rapides", font=('Segoe UI', 18, 'bold'),
                bg=self.colors['background'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 15))
        
        actions_frame = tk.Frame(main_content, bg=self.colors['background'])
        actions_frame.pack(fill='x', pady=(0, 30))
        
        quick_actions = [
            ("🍽️ Générer un plan", "Plan personnalisé 7 jours", self.show_meal_generator),
            ("📖 Voir recettes", f"{recipe_count} recettes santé", self.show_recipes),
            ("💾 Mes inscriptions", "Voir plans sauvegardés", self.show_saved_plans),
            ("🔍 Recherche avancée", "Recettes par critères", self.show_recipe_search)
        ]
        
        for i, (title, subtitle, command) in enumerate(quick_actions):
            card = self.create_card(actions_frame, title, subtitle, "→", self.colors['primary'], command)
            card.grid(row=0, column=i, padx=10, sticky='nsew')
        
        # Derniers plans sauvegardés
        tk.Label(main_content, text="📋 Dernières inscriptions", font=('Segoe UI', 18, 'bold'),
                bg=self.colors['background'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 15))
        
        plans_frame = tk.Frame(main_content, bg=self.colors['background'])
        plans_frame.pack(fill='both', expand=True)
        
        # Récupérer les 3 derniers plans
        self.cursor.execute('''
            SELECT plan_name, days_count, created_at 
            FROM saved_plans 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 3
        ''', (self.current_user['id'],))
        
        recent_plans = self.cursor.fetchall()
        
        if recent_plans:
            for plan in recent_plans:
                plan_name, days_count, created_at = plan
                plan_card = self.create_plan_card(plans_frame, plan_name, 
                                                 f"{days_count} jours • {created_at[:10]}", 
                                                 "📋 Sauvegardé")
                plan_card.pack(fill='x', pady=5)
        else:
            empty_label = tk.Label(plans_frame, text="📭 Aucun plan sauvegardé pour le moment",
                                  font=('Segoe UI', 14), bg=self.colors['background'], 
                                  fg=self.colors['text_secondary'])
            empty_label.pack(pady=20)
    
    def create_stats_card(self, parent, icon, value, text, color):
        """Crée une carte de statistiques"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief='flat', 
                       highlightbackground=self.colors['light_gray'], 
                       highlightthickness=1, padx=20, pady=20)
        
        tk.Label(card, text=icon, font=('Segoe UI', 20), bg=self.colors['card_bg'], fg=color).pack(anchor='w')
        tk.Label(card, text=value, font=('Segoe UI', 24, 'bold'), bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(anchor='w')
        tk.Label(card, text=text, font=('Segoe UI', 12), bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack(anchor='w')
        
        return card
    
    def create_plan_card(self, parent, title, details, status):
        """Crée une carte de plan"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief='flat', 
                       highlightbackground=self.colors['light_gray'], 
                       highlightthickness=1, padx=20, pady=15)
        
        # Titre et détails
        left_frame = tk.Frame(card, bg=self.colors['card_bg'])
        left_frame.pack(side='left', fill='y')
        
        tk.Label(left_frame, text=title, font=('Segoe UI', 14, 'bold'), 
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(anchor='w')
        tk.Label(left_frame, text=details, font=('Segoe UI', 11), 
                bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack(anchor='w')
        
        # Statut
        tk.Label(card, text=status, font=('Segoe UI', 12, 'bold'), 
                bg=self.colors['card_bg'], fg=self.colors['primary']).pack(side='right')
        
        return card
    
    def show_recipes(self):
        """Affiche toutes les recettes"""
        self.clear_window()
        
        # Barre latérale
        sidebar = tk.Frame(self.root, bg=self.colors['card_bg'], width=250,
                          highlightbackground=self.colors['light_gray'], 
                          highlightthickness=1)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text="🍽️", font=('Segoe UI', 24),
                bg=self.colors['card_bg'], fg=self.colors['primary']).pack(pady=(30, 10))
        
        menu_items = [
            ("📊 Tableau de bord", self.show_dashboard),
            ("🍽️ Générer repas", self.show_meal_generator),
            ("📖 Recettes", self.show_recipes),
            ("💾 Mes inscriptions", self.show_saved_plans),
            ("👤 Profil", self.show_profile),
            ("🚪 Déconnexion", self.show_login_screen)
        ]
        
        for text, command in menu_items:
            btn = tk.Label(sidebar, text=text, font=('Segoe UI', 12),
                          bg=self.colors['card_bg'], fg=self.colors['text_secondary'],
                          cursor='hand2', padx=20, pady=15)
            btn.bind('<Button-1>', lambda e, cmd=command: cmd())
            btn.pack(fill='x')
        
        # Contenu principal
        main_content = tk.Frame(self.root, bg=self.colors['background'])
        main_content.pack(side='right', fill='both', expand=True, padx=30, pady=30)
        
        # En-tête
        header = tk.Frame(main_content, bg=self.colors['background'])
        header.pack(fill='x', pady=(0, 30))
        
        tk.Label(header, text="📖 Recettes disponibles", 
                font=('Segoe UI', 28, 'bold'), bg=self.colors['background'], 
                fg=self.colors['text_primary']).pack(side='left')
        
        # Compter les recettes
        self.cursor.execute('SELECT COUNT(*) FROM recipes')
        recipe_count = self.cursor.fetchone()[0]
        
        tk.Label(header, text=f"({recipe_count} recettes)", font=('Segoe UI', 14),
                bg=self.colors['background'], fg=self.colors['text_secondary']).pack(side='left', padx=10)
        
        # Barre de recherche
        search_frame = tk.Frame(main_content, bg=self.colors['background'])
        search_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(search_frame, text="🔍 Rechercher:", font=('Segoe UI', 12),
                bg=self.colors['background'], fg=self.colors['text_primary']).pack(side='left', padx=(0, 10))
        
        self.recipe_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.recipe_search_var, 
                                width=30, font=('Segoe UI', 12))
        search_entry.pack(side='left', padx=(0, 10))
        
        search_btn = tk.Button(search_frame, text="Rechercher", 
                              bg=self.colors['primary'], fg='white',
                              font=('Segoe UI', 11), relief='flat',
                              command=self.filter_recipes)
        search_btn.pack(side='left', padx=(0, 10))
        
        # Filtres
        filter_frame = tk.Frame(main_content, bg=self.colors['background'])
        filter_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(filter_frame, text="Filtrer par catégorie:", font=('Segoe UI', 12),
                bg=self.colors['background'], fg=self.colors['text_primary']).pack(side='left', padx=(0, 10))
        
        self.recipe_category_var = tk.StringVar(value="Toutes")
        category_combo = ttk.Combobox(filter_frame, textvariable=self.recipe_category_var,
                                     values=["Toutes", "Petit-déjeuner", "Déjeuner", "Dîner"],
                                     width=15, font=('Segoe UI', 12))
        category_combo.pack(side='left', padx=(0, 10))
        category_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_recipes())
        
        # Canvas pour le défilement
        canvas_container = tk.Frame(main_content, bg=self.colors['background'])
        canvas_container.pack(fill='both', expand=True)
        
        # Canvas et scrollbar
        canvas = tk.Canvas(canvas_container, bg=self.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        
        # Frame pour les cartes
        self.recipes_cards_frame = tk.Frame(canvas, bg=self.colors['background'])
        
        # Configuration du scroll
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Placement des widgets
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=self.recipes_cards_frame, anchor="nw")
        
        # Mettre à jour la zone de défilement
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self.recipes_cards_frame.bind("<Configure>", configure_scroll_region)
        
        # Raccourcis clavier pour le défilement
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Charger toutes les recettes
        self.load_all_recipes()
    
    def load_all_recipes(self):
        """Charge toutes les recettes"""
        self.cursor.execute('SELECT * FROM recipes ORDER BY name')
        all_recipes = self.cursor.fetchall()
        
        # Effacer le frame existant
        for widget in self.recipes_cards_frame.winfo_children():
            widget.destroy()
        
        # Afficher les recettes en grille
        if all_recipes:
            for i, recipe in enumerate(all_recipes):
                row = i // self.cards_per_row
                col = i % self.cards_per_row
                
                card = self.create_recipe_card(self.recipes_cards_frame, recipe)
                card.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
            
            # Configurer le poids des colonnes
            for col in range(self.cards_per_row):
                self.recipes_cards_frame.columnconfigure(col, weight=1, uniform="col")
        else:
            empty_label = tk.Label(self.recipes_cards_frame, text="📭 Aucune recette disponible",
                                  font=('Segoe UI', 18), bg=self.colors['background'], 
                                  fg=self.colors['text_secondary'])
            empty_label.pack(pady=50)
    
    def filter_recipes(self):
        """Filtre les recettes selon la recherche"""
        search_term = self.recipe_search_var.get().lower()
        category = self.recipe_category_var.get()
        
        # Construire la requête SQL
        query = "SELECT * FROM recipes WHERE 1=1"
        params = []
        
        if category != "Toutes":
            query += " AND category = ?"
            params.append(category)
        
        if search_term:
            query += " AND (name LIKE ? OR ingredients LIKE ?)"
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
        
        query += " ORDER BY name"
        
        # Exécuter la requête
        self.cursor.execute(query, params)
        filtered_recipes = self.cursor.fetchall()
        
        # Effacer le frame existant
        for widget in self.recipes_cards_frame.winfo_children():
            widget.destroy()
        
        # Afficher les recettes filtrées
        if filtered_recipes:
            for i, recipe in enumerate(filtered_recipes):
                row = i // self.cards_per_row
                col = i % self.cards_per_row
                
                card = self.create_recipe_card(self.recipes_cards_frame, recipe)
                card.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
            
            # Configurer le poids des colonnes
            for col in range(self.cards_per_row):
                self.recipes_cards_frame.columnconfigure(col, weight=1, uniform="col")
        else:
            empty_label = tk.Label(self.recipes_cards_frame, 
                                  text="❌ Aucune recette ne correspond à votre recherche",
                                  font=('Segoe UI', 16), bg=self.colors['background'], 
                                  fg=self.colors['text_secondary'])
            empty_label.pack(pady=50)
    
    def show_saved_plans(self):
        """Affiche les plans sauvegardés"""
        self.clear_window()
        
        # Barre latérale
        sidebar = tk.Frame(self.root, bg=self.colors['card_bg'], width=250,
                          highlightbackground=self.colors['light_gray'], 
                          highlightthickness=1)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        menu_items = [
            ("📊 Tableau de bord", self.show_dashboard),
            ("🍽️ Générer repas", self.show_meal_generator),
            ("📖 Recettes", self.show_recipes),
            ("💾 Mes inscriptions", self.show_saved_plans),
            ("👤 Profil", self.show_profile),
            ("🚪 Déconnexion", self.show_login_screen)
        ]
        
        for text, command in menu_items:
            btn = tk.Label(sidebar, text=text, font=('Segoe UI', 12),
                          bg=self.colors['card_bg'], fg=self.colors['text_secondary'],
                          cursor='hand2', padx=20, pady=15)
            btn.bind('<Button-1>', lambda e, cmd=command: cmd())
            btn.pack(fill='x')
        
        # Contenu principal
        main_content = tk.Frame(self.root, bg=self.colors['background'])
        main_content.pack(side='right', fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(main_content, text="💾 Mes inscriptions", 
                font=('Segoe UI', 28, 'bold'), bg=self.colors['background'], 
                fg=self.colors['text_primary']).pack(pady=(0, 30))
        
        # Récupérer tous les plans sauvegardés
        self.cursor.execute('''
            SELECT id, plan_name, calories_target, days_count, created_at 
            FROM saved_plans 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (self.current_user['id'],))
        
        saved_plans = self.cursor.fetchall()
        
        if saved_plans:
            # Frame pour la liste des plans
            list_frame = tk.Frame(main_content, bg=self.colors['background'])
            list_frame.pack(fill='both', expand=True)
            
            # En-têtes
            headers = ["Nom", "Calories/jour", "Jours", "Date", "Actions"]
            for col, header in enumerate(headers):
                tk.Label(list_frame, text=header, font=('Segoe UI', 12, 'bold'),
                        bg=self.colors['background'], fg=self.colors['primary']).grid(row=0, column=col, padx=10, pady=10)
            
            # Liste des plans
            for row, plan in enumerate(saved_plans, 1):
                plan_id, plan_name, calories, days, created_at = plan
                
                # Nom du plan
                tk.Label(list_frame, text=plan_name, font=('Segoe UI', 11),
                        bg=self.colors['background'], fg=self.colors['text_primary']).grid(row=row, column=0, padx=10, pady=5)
                
                # Calories
                tk.Label(list_frame, text=f"{calories} cal", font=('Segoe UI', 11),
                        bg=self.colors['background'], fg=self.colors['text_primary']).grid(row=row, column=1, padx=10, pady=5)
                
                # Jours
                tk.Label(list_frame, text=str(days), font=('Segoe UI', 11),
                        bg=self.colors['background'], fg=self.colors['text_primary']).grid(row=row, column=2, padx=10, pady=5)
                
                # Date
                tk.Label(list_frame, text=created_at[:10], font=('Segoe UI', 11),
                        bg=self.colors['background'], fg=self.colors['text_secondary']).grid(row=row, column=3, padx=10, pady=5)
                
                # Boutons d'action
                action_frame = tk.Frame(list_frame, bg=self.colors['background'])
                action_frame.grid(row=row, column=4, padx=10, pady=5)
                
                # Bouton Voir
                view_btn = tk.Label(action_frame, text="👁️ Voir", font=('Segoe UI', 10),
                                   bg=self.colors['primary'], fg='white',
                                   cursor='hand2', padx=10, pady=5)
                view_btn.bind('<Button-1>', lambda e, pid=plan_id: self.view_saved_plan(pid))
                view_btn.pack(side='left', padx=2)
                
                # Bouton Supprimer
                delete_btn = tk.Label(action_frame, text="🗑️ Supprimer", font=('Segoe UI', 10),
                                     bg=self.colors['danger'], fg='white',
                                     cursor='hand2', padx=10, pady=5)
                delete_btn.bind('<Button-1>', lambda e, pid=plan_id: self.delete_saved_plan(pid))
                delete_btn.pack(side='left', padx=2)
        else:
            empty_frame = tk.Frame(main_content, bg=self.colors['background'])
            empty_frame.pack(fill='both', expand=True)
            
            tk.Label(empty_frame, text="📭 Aucune inscription pour le moment", 
                    font=('Segoe UI', 18), bg=self.colors['background'], 
                    fg=self.colors['text_secondary']).pack(pady=50)
            
            tk.Label(empty_frame, text="Générez votre premier plan pour le sauvegarder ici !", 
                    font=('Segoe UI', 14), bg=self.colors['background'], 
                    fg=self.colors['text_secondary']).pack(pady=10)
    
    def view_saved_plan(self, plan_id):
        """Affiche un plan sauvegardé"""
        self.cursor.execute('SELECT plan_text FROM saved_plans WHERE id = ?', (plan_id,))
        result = self.cursor.fetchone()
        
        if result:
            plan_text = result[0]
            
            popup = tk.Toplevel(self.root)
            popup.title("📋 Plan sauvegardé")
            popup.geometry("800x600")
            popup.configure(bg=self.colors['background'])
            
            text_widget = scrolledtext.ScrolledText(popup, font=('Consolas', 11),
                                                   bg=self.colors['card_bg'], fg=self.colors['text_primary'],
                                                   insertbackground=self.colors['primary'])
            text_widget.pack(fill='both', expand=True, padx=20, pady=20)
            text_widget.insert(1.0, plan_text)
            text_widget.config(state='disabled')
    
    def delete_saved_plan(self, plan_id):
        """Supprime un plan sauvegardé"""
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce plan ?"):
            self.cursor.execute('DELETE FROM saved_plans WHERE id = ?', (plan_id,))
            self.conn.commit()
            messagebox.showinfo("Succès", "✅ Plan supprimé avec succès")
            self.show_saved_plans()
    
    def show_meal_generator(self):
        """Affiche le générateur de repas"""
        self.clear_window()
        
        # Barre latérale
        sidebar = tk.Frame(self.root, bg=self.colors['card_bg'], width=250,
                          highlightbackground=self.colors['light_gray'], 
                          highlightthickness=1)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text="🍽️", font=('Segoe UI', 24),
                bg=self.colors['card_bg'], fg=self.colors['primary']).pack(pady=(30, 10))
        
        menu_items = [
            ("📊 Tableau de bord", self.show_dashboard),
            ("🍽️ Générer repas", self.show_meal_generator),
            ("📖 Recettes", self.show_recipes),
            ("💾 Mes inscriptions", self.show_saved_plans),
            ("👤 Profil", self.show_profile),
            ("🚪 Déconnexion", self.show_login_screen)
        ]
        
        for text, command in menu_items:
            btn = tk.Label(sidebar, text=text, font=('Segoe UI', 12),
                          bg=self.colors['card_bg'], fg=self.colors['text_secondary'],
                          cursor='hand2', padx=20, pady=15)
            btn.bind('<Button-1>', lambda e, cmd=command: cmd())
            btn.pack(fill='x')
        
        # Contenu principal
        main_content = tk.Frame(self.root, bg=self.colors['background'])
        main_content.pack(side='right', fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(main_content, text="🍽️ Générateur de Repas", 
                font=('Segoe UI', 28, 'bold'), bg=self.colors['background'], 
                fg=self.colors['text_primary']).pack(pady=(0, 30))
        
        # Carte paramètres
        settings_card = tk.Frame(main_content, bg=self.colors['card_bg'], 
                                highlightbackground=self.colors['light_gray'], 
                                highlightthickness=1, padx=30, pady=30)
        settings_card.pack(fill='x', pady=(0, 20))
        
        tk.Label(settings_card, text="⚙️ Paramètres du plan", font=('Segoe UI', 18, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 20))
        
        # Grille paramètres
        settings_grid = tk.Frame(settings_card, bg=self.colors['card_bg'])
        settings_grid.pack(fill='x')
        
        # Nom du plan
        tk.Label(settings_grid, text="Nom du plan:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=0, column=0, sticky='w', pady=10)
        
        self.plan_name_var = tk.StringVar(value=f"Plan {datetime.now().strftime('%d/%m/%Y')}")
        plan_name_entry = ttk.Entry(settings_grid, textvariable=self.plan_name_var, 
                                   width=20, font=('Segoe UI', 12))
        plan_name_entry.grid(row=0, column=1, padx=20, pady=10)
        
        # Calories cible
        tk.Label(settings_grid, text="Calories cible par jour:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=0, column=2, sticky='w', pady=10)
        
        self.calories_var = tk.StringVar(value="2000")
        calories_entry = ttk.Entry(settings_grid, textvariable=self.calories_var, 
                                  width=15, font=('Segoe UI', 12))
        calories_entry.grid(row=0, column=3, padx=20, pady=10)
        
        # Nombre de jours
        tk.Label(settings_grid, text="Nombre de jours:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=1, column=0, sticky='w', pady=10)
        
        self.days_var = tk.StringVar(value="7")
        days_entry = ttk.Entry(settings_grid, textvariable=self.days_var, 
                              width=15, font=('Segoe UI', 12))
        days_entry.grid(row=1, column=1, padx=20, pady=10)
        
        # Catégorie préférée
        tk.Label(settings_grid, text="Catégorie préférée:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=1, column=2, sticky='w', pady=10)
        
        self.category_var = tk.StringVar(value="Toutes")
        category_combo = ttk.Combobox(settings_grid, textvariable=self.category_var, 
                                     values=["Toutes", "Petit-déjeuner", "Déjeuner", "Dîner"], 
                                     width=12, font=('Segoe UI', 12))
        category_combo.grid(row=1, column=3, padx=20, pady=10)
        
        # Boutons
        button_frame = tk.Frame(settings_card, bg=self.colors['card_bg'])
        button_frame.pack(pady=20)
        
        # Bouton génération
        generate_btn = tk.Button(button_frame, text="🎯 Générer le plan", 
                                bg=self.colors['primary'], fg='white',
                                font=('Segoe UI', 12, 'bold'), relief='flat',
                                command=self.generate_meal_plan)
        generate_btn.pack(side='left', padx=5)
        
        # Bouton sauvegarde
        save_btn = tk.Button(button_frame, text="💾 Sauvegarder le plan", 
                            bg='white', fg=self.colors['primary'],
                            font=('Segoe UI', 12), relief='solid',
                            command=self.save_generated_plan)
        save_btn.pack(side='left', padx=5)
        
        # Zone résultats
        self.results_text = scrolledtext.ScrolledText(main_content, height=20, font=('Consolas', 11),
                                                     bg=self.colors['card_bg'], fg=self.colors['text_primary'],
                                                     insertbackground=self.colors['primary'])
        self.results_text.pack(fill='both', expand=True, pady=10)
        
        # Générer un plan par défaut
        self.generate_sample_plan()
    
    def generate_sample_plan(self):
        """Génère un plan d'exemple"""
        sample_text = "╔════════════════════════════════════════╗\n"
        sample_text += "║         BIENVENUE AU GÉNÉRATEUR        ║\n"
        sample_text += "║              DE REPAS                 ║\n"
        sample_text += "╚════════════════════════════════════════╝\n\n"
        sample_text += "📋 Configurez vos paramètres ci-dessus et cliquez sur\n"
        sample_text += "   '🎯 Générer le plan' pour créer votre plan personnalisé!\n\n"
        sample_text += "💡 Conseils :\n"
        sample_text += "   • Pour une perte de poids : 1500-1800 calories/jour\n"
        sample_text += "   • Pour le maintien : 2000-2200 calories/jour\n"
        sample_text += "   • Pour prise de masse : 2500-3000 calories/jour\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, sample_text)
    
    def generate_meal_plan(self):
        """Génère un plan alimentaire"""
        try:
            plan_name = self.plan_name_var.get()
            days = int(self.days_var.get())
            target_calories = int(self.calories_var.get())
            category = self.category_var.get()
        except ValueError:
            messagebox.showerror("Erreur", "🔢 Veuillez entrer des nombres valides")
            return
        
        # Récupérer les recettes selon la catégorie
        if category == "Toutes":
            self.cursor.execute('SELECT * FROM recipes')
        else:
            self.cursor.execute('SELECT * FROM recipes WHERE category = ?', (category,))
        
        all_recipes = self.cursor.fetchall()
        
        if not all_recipes:
            messagebox.showerror("Erreur", "❌ Aucune recette disponible pour cette catégorie")
            return
        
        # En-tête stylisé
        plan_text = "╔════════════════════════════════════════╗\n"
        plan_text += "║         📋 SMARTMEAL PLANNER          ║\n"
        plan_text += f"║            {plan_name:^16}           ║\n"
        plan_text += "╚════════════════════════════════════════╝\n\n"
        
        plan_text += f"🔮 Jours: {days} | 🎯 Calories/jour: {target_calories}\n"
        if category != "Toutes":
            plan_text += f"📂 Catégorie: {category}\n"
        plan_text += "═" * 50 + "\n\n"
        
        categories = {
            'Petit-déjeuner': [r for r in all_recipes if r[2] == 'Petit-déjeuner'],
            'Déjeuner': [r for r in all_recipes if r[2] == 'Déjeuner'],
            'Dîner': [r for r in all_recipes if r[2] == 'Dîner']
        }
        
        total_calories = 0
        
        for day in range(1, days + 1):
            plan_text += f"\n✨ JOUR {day}\n"
            plan_text += "─" * 35 + "\n"
            daily_calories = 0
            
            for meal_type in ['Petit-déjeuner', 'Déjeuner', 'Dîner']:
                available = categories[meal_type]
                if available:
                    recipe = random.choice(available)
                    plan_text += f"\n🍽️  {meal_type}:\n"
                    plan_text += f"   📛 {recipe[1]}\n"
                    plan_text += f"   ⏱️  {recipe[6]} min | 🔥 {recipe[5]} cal | 🎯 {recipe[7]}\n"
                    plan_text += f"   📝 {recipe[3][:80]}...\n"
                    daily_calories += recipe[5]
                else:
                    plan_text += f"\n🍽️  {meal_type}:\n"
                    plan_text += f"   ❌ Aucune recette disponible\n"
            
            plan_text += f"\n📊 TOTAL JOUR {day}: {daily_calories} calories\n"
            plan_text += "═" * 50 + "\n"
            total_calories += daily_calories
        
        # Résumé
        plan_text += f"\n📈 RÉSUMÉ DU PLAN\n"
        plan_text += "─" * 35 + "\n"
        plan_text += f"📅 Durée: {days} jours\n"
        plan_text += f"🎯 Calories/jour cible: {target_calories}\n"
        plan_text += f"🔥 Calories totales: {total_calories}\n"
        plan_text += f"📊 Moyenne/jour: {total_calories//days}\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, plan_text)
        
        # Stocker le plan généré pour sauvegarde
        self.current_generated_plan = {
            'text': plan_text,
            'name': plan_name,
            'calories': target_calories,
            'days': days,
            'category': category
        }
    
    def save_generated_plan(self):
        """Sauvegarde le plan généré"""
        if not hasattr(self, 'current_generated_plan'):
            messagebox.showerror("Erreur", "❌ Aucun plan à sauvegarder. Générez d'abord un plan!")
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO saved_plans (user_id, plan_name, plan_text, calories_target, days_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.current_user['id'], 
                  self.current_generated_plan['name'],
                  self.current_generated_plan['text'],
                  self.current_generated_plan['calories'],
                  self.current_generated_plan['days']))
            self.conn.commit()
            
            messagebox.showinfo("Succès", f"✅ Plan '{self.current_generated_plan['name']}' sauvegardé !")
            self.show_saved_plans()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Impossible de sauvegarder: {e}")
    
    def show_recipe_search(self):
        """Affiche la page de recherche de recettes"""
        self.show_recipes()
    
    def show_profile(self):
        """Affiche la page profil"""
        self.clear_window()
        
        # Barre latérale
        sidebar = tk.Frame(self.root, bg=self.colors['card_bg'], width=250,
                          highlightbackground=self.colors['light_gray'], 
                          highlightthickness=1)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        menu_items = [
            ("📊 Tableau de bord", self.show_dashboard),
            ("🍽️ Générer repas", self.show_meal_generator),
            ("📖 Recettes", self.show_recipes),
            ("💾 Mes inscriptions", self.show_saved_plans),
            ("👤 Profil", self.show_profile),
            ("🚪 Déconnexion", self.show_login_screen)
        ]
        
        for text, command in menu_items:
            btn = tk.Label(sidebar, text=text, font=('Segoe UI', 12),
                          bg=self.colors['card_bg'], fg=self.colors['text_secondary'],
                          cursor='hand2', padx=20, pady=15)
            btn.bind('<Button-1>', lambda e, cmd=command: cmd())
            btn.pack(fill='x')
        
        # Contenu principal
        main_content = tk.Frame(self.root, bg=self.colors['background'])
        main_content.pack(side='right', fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(main_content, text="👤 Mon Profil", 
                font=('Segoe UI', 28, 'bold'), bg=self.colors['background'], 
                fg=self.colors['text_primary']).pack(pady=(0, 30))
        
        # Carte profil
        profile_card = tk.Frame(main_content, bg=self.colors['card_bg'],
                               highlightbackground=self.colors['light_gray'], 
                               highlightthickness=1, padx=30, pady=30)
        profile_card.pack(fill='x', pady=(0, 20))
        
        # Avatar
        avatar_frame = tk.Frame(profile_card, bg=self.colors['card_bg'])
        avatar_frame.pack(pady=(0, 20))
        
        avatar = tk.Label(avatar_frame, text="👤", font=('Segoe UI', 48),
                         bg=self.colors['primary'], fg='white',
                         width=4, height=2)
        avatar.pack()
        
        # Informations utilisateur
        info_frame = tk.Frame(profile_card, bg=self.colors['card_bg'])
        info_frame.pack(fill='x')
        
        user_info = [
            ("Prénom", self.current_user.get('firstname', 'Invité')),
            ("Nom", self.current_user.get('lastname', '')),
            ("Email", self.current_user.get('email', 'demo@example.com')),
            ("Taille", f"{self.current_user.get('height', 0)} cm"),
            ("Poids", f"{self.current_user.get('weight', 0)} kg")
        ]
        
        for label, value in user_info:
            row = tk.Frame(info_frame, bg=self.colors['card_bg'])
            row.pack(fill='x', pady=10)
            
            tk.Label(row, text=label + ":", font=('Segoe UI', 12, 'bold'),
                    bg=self.colors['card_bg'], fg=self.colors['text_primary'],
                    width=15, anchor='w').pack(side='left')
            tk.Label(row, text=value, font=('Segoe UI', 12),
                    bg=self.colors['card_bg'], fg=self.colors['text_secondary'],
                    anchor='w').pack(side='left')
    
    def clear_window(self):
        """Vide la fenêtre"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def on_window_resize(self, event):
        """Gère le redimensionnement de la fenêtre"""
        if event.widget == self.root:
            new_width = event.width
            
            # Ajuster le nombre de cartes par ligne
            if new_width < 800:
                self.cards_per_row = 1
            elif new_width < 1200:
                self.cards_per_row = 2
            else:
                self.cards_per_row = 3
            
            # Rafraîchir si nécessaire
            if hasattr(self, 'recipes_cards_frame') and self.recipes_cards_frame.winfo_exists():
                self.refresh_recipes_display()
    
    def refresh_recipes_display(self):
        """Rafraîchit l'affichage des recettes"""
        search_term = self.recipe_search_var.get().lower() if hasattr(self, 'recipe_search_var') else ""
        category = self.recipe_category_var.get() if hasattr(self, 'recipe_category_var') else "Toutes"
        
        # Construire la requête SQL
        query = "SELECT * FROM recipes WHERE 1=1"
        params = []
        
        if category != "Toutes":
            query += " AND category = ?"
            params.append(category)
        
        if search_term:
            query += " AND (name LIKE ? OR ingredients LIKE ?)"
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
        
        query += " ORDER BY name"
        
        # Exécuter la requête
        self.cursor.execute(query, params)
        filtered_recipes = self.cursor.fetchall()
        
        # Effacer le frame existant
        for widget in self.recipes_cards_frame.winfo_children():
            widget.destroy()
        
        # Afficher les recettes filtrées
        if filtered_recipes:
            for i, recipe in enumerate(filtered_recipes):
                row = i // self.cards_per_row
                col = i % self.cards_per_row
                
                card = self.create_recipe_card(self.recipes_cards_frame, recipe)
                card.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
            
            # Configurer le poids des colonnes
            for col in range(self.cards_per_row):
                self.recipes_cards_frame.columnconfigure(col, weight=1, uniform="col")
        else:
            empty_label = tk.Label(self.recipes_cards_frame, 
                                  text="❌ Aucune recette ne correspond à votre recherche",
                                  font=('Segoe UI', 16), bg=self.colors['background'], 
                                  fg=self.colors['text_secondary'])
            empty_label.pack(pady=50)

def main():
    try:
        root = tk.Tk()
        app = ModernSmartMealPlanner(root)
        root.mainloop()
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        input("Appuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()
