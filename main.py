import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font as tkfont
import sqlite3
import random
from datetime import datetime
from PIL import Image, ImageTk

from io import BytesIO
import os

class ModernSmartMealPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("🍽️ SmartMeal Planner - Repas Sains & Intelligents")
        self.root.geometry("1600x1000")
        
        # Configuration des styles et couleurs modernes
        self.setup_styles()
        self.setup_images()
        
        self.current_user = None
        self.setup_database()
        
        # Police personnalisée
        self.setup_fonts()
        
        # Afficher l'écran de connexion
        self.show_login_screen()
    
    def setup_fonts(self):
        """Configure les polices personnalisées"""
        try:
            self.title_font = ('Montserrat', 36, 'bold')
            self.subtitle_font = ('Montserrat', 16)
            self.heading_font = ('Montserrat', 24, 'bold')
            self.body_font = ('Segoe UI', 11)
            self.button_font = ('Segoe UI', 12, 'bold')
        except:
            # Fallback aux polices standards
            self.title_font = ('Helvetica', 32, 'bold')
            self.subtitle_font = ('Helvetica', 14)
            self.heading_font = ('Helvetica', 20, 'bold')
            self.body_font = ('Arial', 10)
            self.button_font = ('Arial', 11, 'bold')
    
    def setup_styles(self):
        """Configure les styles modernes"""
        self.colors = {
            'primary': '#00C897',  # Vert émeraude moderne
            'primary_light': '#5CE3B8',
            'primary_dark': '#008A68',
            'secondary': '#FF6B6B',  # Corail
            'accent': '#FFD166',  # Jaune doux
            'background': '#1A1A2E',  # Fond bleu nuit
            'card_bg': '#162447',  # Bleu carte
            'card_hover': '#1F4068',  # Bleu carte hover
            'text_primary': '#FFFFFF',
            'text_secondary': '#B8B8D1',
            'text_muted': '#8A8AA3',
            'success': '#06D6A0',
            'warning': '#FFD166',
            'danger': '#EF476F',
            'gradient_start': '#00C897',
            'gradient_end': '#0077B6'
        }
        
        # Configuration de la fenêtre principale
        self.root.configure(bg=self.colors['background'])
        
        # Style ttk
        style = ttk.Style()
        style.theme_use('clam')
        
        # Style pour les boutons
        style.configure('Gradient.TButton',
                      font=self.button_font,
                      borderwidth=0,
                      focuscolor='none',
                      relief='flat',
                      background=self.colors['primary'],
                      foreground=self.colors['text_primary'],
                      padding=15)
        
        style.map('Gradient.TButton',
                 background=[('active', self.colors['primary_dark']),
                           ('pressed', self.colors['primary_dark'])])
        
        style.configure('Outline.TButton',
                       font=self.button_font,
                       borderwidth=2,
                       relief='solid',
                       background='transparent',
                       foreground=self.colors['primary'],
                       padding=10)
        
        # Style pour les cartes
        style.configure('Card.TFrame',
                       background=self.colors['card_bg'],
                       relief='flat')
        
        # Style pour les labels
        style.configure('Title.TLabel',
                       font=self.title_font,
                       background=self.colors['background'],
                       foreground=self.colors['text_primary'])
        
        style.configure('Subtitle.TLabel',
                       font=self.subtitle_font,
                       background=self.colors['background'],
                       foreground=self.colors['text_secondary'])
    
    def setup_images(self):
        """Configure les images par défaut pour les recettes"""
        # Images par défaut (peuvent être remplacées par des URLs réelles)
        self.recipe_images = {
            'default': self.create_color_image(self.colors['primary'], (300, 200)),
            'breakfast': self.create_color_image('#FFD166', (300, 200)),
            'lunch': self.create_color_image('#06D6A0', (300, 200)),
            'dinner': self.create_color_image('#0077B6', (300, 200)),
            'vegetarian': self.create_color_image('#7BDFA0', (300, 200))
        }
        
        # Icônes pour les catégories
        self.category_icons = {
            'Petit-déjeuner': '🥐',
            'Déjeuner': '🍲',
            'Dîner': '🍽️',
            'Végétarien': '🥗',
            'Healthy': '🥑',
            'Rapide': '⚡'
        }
    
    def create_color_image(self, color, size):
        """Crée une image de couleur unie (pour les placeholders)"""
        img = Image.new('RGB', size, color)
        return ImageTk.PhotoImage(img)
    
    def setup_database(self):
        """Initialise la base de données avec des recettes améliorées"""
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
                age INTEGER,
                goal TEXT,
                activity_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table recettes avec plus de détails
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL,
                calories INTEGER,
                protein REAL,
                carbs REAL,
                fat REAL,
                prep_time INTEGER,
                difficulty TEXT,
                image_url TEXT,
                tags TEXT
            )
        ''')
        
        # Table plans sauvegardés
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
        
        # Table favoris
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                recipe_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
        
        self.populate_sample_recipes()
        self.conn.commit()
    
    def populate_sample_recipes(self):
        """Remplit la base avec des recettes modernes et détaillées"""
        sample_recipes = [
            # Petit-déjeuners
            ('Bowl Avoine Énergie', 'Petit-déjeuner', 'Healthy',
             'Flocons davoine 50g, Lait damande 200ml, Myrtilles 100g, Noix 30g, Miel 1cs, Graines de chia 10g',
             '1. Faire tremper les flocons davoine dans le lait pendant 5 min\n2. Ajouter les myrtilles et les noix\n3. Arroser de miel et saupoudrer de graines de chia\n4. Servir frais',
             320, 12, 45, 8, 10, 'Facile', None, 'healthy,rapide,végétarien'),
            
            ('Smoothie Vert Vitalité', 'Petit-déjeuner', 'Detox',
             'Épinards 50g, Banane 1, Avocat ½, Lait damande 200ml, Graines de chia 1cs, Miel 1cs',
             '1. Laver les épinards\n2. Éplucher la banane et lavocat\n3. Tout mixer pendant 2 min\n4. Ajouter les graines de chia et servir immédiatement',
             280, 8, 35, 10, 5, 'Facile', None, 'detox,rapide,végétalien'),
            
            ('Toast Avocat Œuf', 'Petit-déjeuner', 'Protéiné',
             'Pain complet 2 tranches, Avocat 1, Œufs 2, Graines de sésame 1cs, Piment rouge, Citron',
             '1. Griller le pain\n2. Écraser lavocat avec du jus de citron\n3. Cuire les œufs au plat\n4. Étaler lavocat sur le pain, ajouter les œufs et garnir',
             350, 18, 30, 15, 12, 'Facile', None, 'protéiné,équilibré'),
            
            # Déjeuners
            ('Bowl Buddha Coloré', 'Déjeuner', 'Végétarien',
             'Quinoa 100g, Patate douce 200g, Avocat 1, Carotte 1, Concombre ½, Sauce tahini 2cs',
             '1. Cuire le quinoa 15 min\n2. Rôtir la patate douce au four\n3. Couper les légumes en dés\n4. Assembler et napper de sauce tahini',
             420, 15, 60, 12, 25, 'Moyen', None, 'végétarien,coloré,healthy'),
            
            ('Wrap Poulet Caesar', 'Déjeuner', 'Protéiné',
             'Tortilla complète 1, Poulet grillé 150g, Laitue romaine 50g, Parmesan 30g, Sauce caesar light 2cs, Tomates cerises',
             '1. Faire griller le poulet\n2. Chauffer la tortilla\n3. Garnir avec tous les ingrédients\n4. Rouler et servir chaud',
             380, 35, 30, 10, 15, 'Facile', None, 'protéiné,rapide'),
            
            ('Salade Quinoa Feta', 'Déjeuner', 'Méditerranéen',
             'Quinoa 100g, Feta 80g, Concombre 1, Olives noires 50g, Huile dolive 2cs, Citron 1, Menthe fraîche',
             '1. Cuire le quinoa\n2. Couper les légumes en dés\n3. Émietter la feta\n4. Mélanger et assaisonner',
             320, 14, 40, 12, 20, 'Facile', None, 'méditerranéen,végétarien,frais'),
            
            # Dîners
            ('Saumon Teriyaki', 'Dîner', 'Asiatique',
             'Saumon 200g, Brocoli 150g, Riz basmati 100g, Sauce teriyaki 3cs, Graines de sésame, Gingembre',
             '1. Cuire le riz\n2. Faire revenir le saumon 5 min chaque côté\n3. Cuire le brocoli à la vapeur\n4. Napper de sauce teriyaki et servir',
             450, 35, 40, 18, 30, 'Moyen', None, 'poisson,protéiné,asiatique'),
            
            ('Curry Végétarien', 'Dîner', 'Indien',
             'Lait de coco 400ml, Curcuma 1cs, Gingembre, Légumes de saison 500g, Riz basmati 150g, Coriandre',
             '1. Faire revenir les épices\n2. Ajouter les légumes\n3. Verser le lait de coco et mijoter 20 min\n4. Servir avec du riz',
             380, 12, 45, 20, 35, 'Moyen', None, 'végétarien,épicé,confort'),
            
            ('Poke Bowl Thon', 'Dîner', 'Hawaïen',
             'Thon frais 180g, Riz vinaigré 150g, Avocat 1, Algues wakame 30g, Graines de sésame, Sauce soja',
             '1. Préparer le riz vinaigré\n2. Couper le thon en dés\n3. Préparer lavocat\n4. Assembler en couches et garnir',
             400, 40, 35, 12, 20, 'Facile', None, 'poisson,protéiné,frais'),
        ]
        
        # Vérifier si la table est vide avant d'insérer
        self.cursor.execute('SELECT COUNT(*) FROM recipes')
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            for recipe in sample_recipes:
                self.cursor.execute('''
                    INSERT INTO recipes 
                    (name, category, subcategory, ingredients, instructions, 
                     calories, protein, carbs, fat, prep_time, difficulty, image_url, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', recipe)
    
    def create_gradient_frame(self, parent, color1, color2, width, height):
        """Crée un frame avec un dégradé de couleur"""
        canvas = tk.Canvas(parent, width=width, height=height, highlightthickness=0)
        canvas.pack()
        
        # Créer un dégradé (simplifié)
        for i in range(height):
            ratio = i / height
            r = int((1-ratio) * int(color1[1:3], 16) + ratio * int(color2[1:3], 16))
            g = int((1-ratio) * int(color1[3:5], 16) + ratio * int(color2[3:5], 16))
            b = int((1-ratio) * int(color1[5:7], 16) + ratio * int(color2[5:7], 16))
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_line(0, i, width, i, fill=color)
        
        return canvas
    
    def create_modern_card(self, parent, title, subtitle, icon, color, command=None, width=280, height=200):
        """Crée une carte moderne avec effets visuels"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], width=width, height=height,
                       relief='flat', highlightthickness=0)
        card.pack_propagate(False)
        
        # Effet hover
        def on_enter(e):
            if command:
                card.configure(bg=self.colors['card_hover'])
        
        def on_leave(e):
            if command:
                card.configure(bg=self.colors['card_bg'])
        
        # Contenu de la carte
        content_frame = tk.Frame(card, bg=self.colors['card_bg'])
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Icône
        icon_label = tk.Label(content_frame, text=icon, font=('Segoe UI', 42),
                             bg=self.colors['card_bg'], fg=color)
        icon_label.pack(pady=(10, 15))
        
        # Titre
        title_label = tk.Label(content_frame, text=title, font=('Segoe UI', 18, 'bold'),
                              bg=self.colors['card_bg'], fg=self.colors['text_primary'])
        title_label.pack(pady=5)
        
        # Sous-titre
        subtitle_label = tk.Label(content_frame, text=subtitle, font=('Segoe UI', 12),
                                 bg=self.colors['card_bg'], fg=self.colors['text_secondary'],
                                 wraplength=220)
        subtitle_label.pack(pady=(0, 15))
        
        # Indicateur d'action
        if command:
            action_label = tk.Label(content_frame, text="→", font=('Segoe UI', 20, 'bold'),
                                   bg=self.colors['card_bg'], fg=color)
            action_label.pack()
            
            # Bind events
            card.bind('<Enter>', on_enter)
            card.bind('<Leave>', on_leave)
            for widget in [card, icon_label, title_label, subtitle_label, action_label]:
                widget.bind('<Button-1>', lambda e: command())
                widget.configure(cursor='hand2')
        
        return card
    
    def create_recipe_card(self, parent, recipe_data, width=300, height=380):
        """Crée une carte de recette moderne avec image"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], width=width, height=height,
                       relief='flat', highlightthickness=0)
        card.pack_propagate(False)
        
        # Image de la recette (placeholder)
        image_frame = tk.Frame(card, bg=self.colors['primary'], height=180)
        image_frame.pack(fill='x')
        image_frame.pack_propagate(False)
        
        # Icône de catégorie sur l'image
        category_icon = self.category_icons.get(recipe_data[2], '🍽️')
        icon_label = tk.Label(image_frame, text=category_icon, font=('Segoe UI', 48),
                             bg=self.colors['primary'], fg='white')
        icon_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Badge de catégorie
        badge = tk.Label(image_frame, text=recipe_data[2], font=('Segoe UI', 10, 'bold'),
                        bg=self.colors['accent'], fg='black', padx=10, pady=3)
        badge.place(x=10, y=10)
        
        # Contenu texte
        content_frame = tk.Frame(card, bg=self.colors['card_bg'], padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Nom de la recette
        name_label = tk.Label(content_frame, text=recipe_data[1], font=('Segoe UI', 16, 'bold'),
                             bg=self.colors['card_bg'], fg=self.colors['text_primary'],
                             wraplength=260, justify='left')
        name_label.pack(anchor='w', pady=(0, 10))
        
        # Informations nutritionnelles
        info_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        info_frame.pack(fill='x', pady=(0, 15))
        
        # Calories
        cal_frame = tk.Frame(info_frame, bg=self.colors['card_bg'])
        cal_frame.pack(side='left', padx=(0, 15))
        tk.Label(cal_frame, text="🔥", font=('Segoe UI', 12),
                bg=self.colors['card_bg'], fg=self.colors['danger']).pack(side='left')
        tk.Label(cal_frame, text=f"{recipe_data[6]} cal", font=('Segoe UI', 11),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(side='left', padx=5)
        
        # Temps
        time_frame = tk.Frame(info_frame, bg=self.colors['card_bg'])
        time_frame.pack(side='left')
        tk.Label(time_frame, text="⏱️", font=('Segoe UI', 12),
                bg=self.colors['card_bg'], fg=self.colors['warning']).pack(side='left')
        tk.Label(time_frame, text=f"{recipe_data[11]} min", font=('Segoe UI', 11),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(side='left', padx=5)
        
        # Difficulté
        diff_frame = tk.Frame(info_frame, bg=self.colors['card_bg'])
        diff_frame.pack(side='left', padx=15)
        tk.Label(diff_frame, text="🎯", font=('Segoe UI', 12),
                bg=self.colors['card_bg'], fg=self.colors['success']).pack(side='left')
        tk.Label(diff_frame, text=recipe_data[12], font=('Segoe UI', 11),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(side='left', padx=5)
        
        # Ingrédients (abrévié)
        ingredients_text = recipe_data[4][:60] + "..." if len(recipe_data[4]) > 60 else recipe_data[4]
        tk.Label(content_frame, text=ingredients_text, font=('Segoe UI', 10),
                bg=self.colors['card_bg'], fg=self.colors['text_secondary'],
                wraplength=260, justify='left', anchor='w').pack(anchor='w', pady=(0, 15))
        
        # Bouton Voir plus
        view_btn = tk.Label(content_frame, text="Voir la recette →", font=('Segoe UI', 11, 'bold'),
                           bg=self.colors['primary'], fg='white',
                           cursor='hand2', padx=20, pady=8)
        view_btn.pack(anchor='e')
        view_btn.bind('<Button-1>', lambda e: self.show_recipe_detail(recipe_data[0]))
        
        # Effet hover
        def on_enter(e):
            card.configure(bg=self.colors['card_hover'])
            content_frame.configure(bg=self.colors['card_hover'])
            info_frame.configure(bg=self.colors['card_hover'])
            for widget in [cal_frame, time_frame, diff_frame, name_label]:
                widget.configure(bg=self.colors['card_hover'])
        
        def on_leave(e):
            card.configure(bg=self.colors['card_bg'])
            content_frame.configure(bg=self.colors['card_bg'])
            info_frame.configure(bg=self.colors['card_bg'])
            for widget in [cal_frame, time_frame, diff_frame, name_label]:
                widget.configure(bg=self.colors['card_bg'])
        
        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
        
        return card
    
    def show_login_screen(self):
        """Affiche l'écran de connexion moderne avec dégradé"""
        self.clear_window()
        
        # Frame principal avec dégradé
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True)
        
        # Créer un effet de dégradé
        gradient_canvas = self.create_gradient_frame(
            main_frame, 
            self.colors['gradient_start'], 
            self.colors['gradient_end'],
            1600, 1000
        )
        gradient_canvas.pack(fill='both', expand=True)
        
        # Overlay sombre
        overlay = tk.Frame(gradient_canvas, bg='#1A1A2E90')  # Semi-transparent
        overlay.place(relwidth=1, relheight=1)
        
        # Contenu centré
        content_frame = tk.Frame(overlay, bg='transparent')
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo et titre avec animation
        logo_label = tk.Label(content_frame, text="🍽️", font=('Segoe UI', 72),
                             bg='transparent', fg=self.colors['text_primary'])
        logo_label.pack(pady=(0, 20))
        
        # Titre avec gradient text
        title_frame = tk.Frame(content_frame, bg='transparent')
        title_frame.pack(pady=(0, 10))
        
        tk.Label(title_frame, text="SmartMeal", font=self.title_font,
                bg='transparent', fg=self.colors['primary']).pack(side='left')
        tk.Label(title_frame, text="Planner", font=self.title_font,
                bg='transparent', fg=self.colors['text_primary']).pack(side='left', padx=5)
        
        tk.Label(content_frame, text="Votre compagnon nutritionnel intelligent", 
                font=self.subtitle_font, bg='transparent', fg=self.colors['text_secondary']).pack(pady=(0, 60))
        
        # Cartes d'action en grille
        actions_frame = tk.Frame(content_frame, bg='transparent')
        actions_frame.pack()
        
        actions = [
            ("🔐", "Se connecter", "Accédez à votre espace personnel", self.show_login_form, self.colors['primary']),
            ("🚀", "Créer un compte", "Commencez votre transformation", self.show_register_form, self.colors['secondary']),
            ("🎯", "Mode Démo", "Découvrez sans engagement", self.demo_mode, self.colors['accent'])
        ]
        
        for i, (icon, title, subtitle, command, color) in enumerate(actions):
            card = self.create_modern_card(actions_frame, title, subtitle, icon, color, command)
            card.grid(row=0, column=i, padx=15, pady=10)
        
        # Footer
        footer = tk.Frame(overlay, bg='transparent')
        footer.pack(side='bottom', pady=30)
        
        tk.Label(footer, text="🍎 Mangez Mieux • 🏃‍♂️ Vivez Mieux • 💪 Soyez Mieux",
                font=('Segoe UI', 12), bg='transparent', fg=self.colors['text_muted']).pack()
    
    def show_login_form(self):
        """Affiche le formulaire de connexion élégant"""
        self.clear_window()
        
        # Frame principal avec fond
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True)
        
        # Sidebar décorative
        sidebar = tk.Frame(main_frame, bg=self.colors['primary'], width=400)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Contenu sidebar
        sidebar_content = tk.Frame(sidebar, bg=self.colors['primary'])
        sidebar_content.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(sidebar_content, text="🍽️", font=('Segoe UI', 72),
                bg=self.colors['primary'], fg='white').pack(pady=(0, 30))
        
        tk.Label(sidebar_content, text="Content de vous revoir !", 
                font=self.heading_font, bg=self.colors['primary'], fg='white').pack(pady=(0, 15))
        
        tk.Label(sidebar_content, text="Accédez à vos plans, recettes\net suivez votre progression", 
                font=self.subtitle_font, bg=self.colors['primary'], fg='white', 
                justify='center').pack()
        
        # Formulaire
        form_frame = tk.Frame(main_frame, bg=self.colors['background'], padx=80)
        form_frame.pack(side='right', fill='both', expand=True)
        
        # En-tête formulaire
        header_frame = tk.Frame(form_frame, bg=self.colors['background'])
        header_frame.pack(fill='x', pady=(60, 40))
        
        # Bouton retour
        back_btn = tk.Label(header_frame, text="←", font=('Segoe UI', 24),
                           bg=self.colors['background'], fg=self.colors['text_secondary'],
                           cursor='hand2')
        back_btn.bind('<Button-1>', lambda e: self.show_login_screen())
        back_btn.pack(side='left')
        
        tk.Label(header_frame, text="Connexion", font=self.heading_font,
                bg=self.colors['background'], fg=self.colors['text_primary']).pack(side='left', padx=20)
        
        # Formulaire
        form_content = tk.Frame(form_frame, bg=self.colors['background'])
        form_content.pack(fill='x', pady=20)
        
        # Champ email
        tk.Label(form_content, text="Email", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['background'], fg=self.colors['text_primary']).pack(anchor='w', pady=(20, 8))
        
        email_frame = tk.Frame(form_content, bg=self.colors['card_bg'], height=50)
        email_frame.pack(fill='x', pady=(0, 20))
        email_frame.pack_propagate(False)
        
        self.email_entry = tk.Entry(email_frame, font=self.body_font, bg=self.colors['card_bg'],
                                   fg=self.colors['text_primary'], bd=0, insertbackground='white')
        self.email_entry.pack(fill='both', expand=True, padx=15)
        self.email_entry.insert(0, "votre@email.com")
        
        # Champ mot de passe
        tk.Label(form_content, text="Mot de passe", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['background'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 8))
        
        password_frame = tk.Frame(form_content, bg=self.colors['card_bg'], height=50)
        password_frame.pack(fill='x', pady=(0, 30))
        password_frame.pack_propagate(False)
        
        self.password_entry = tk.Entry(password_frame, font=self.body_font, bg=self.colors['card_bg'],
                                      fg=self.colors['text_primary'], bd=0, show='•', 
                                      insertbackground='white')
        self.password_entry.pack(fill='both', expand=True, padx=15)
        
        # Bouton connexion
        login_btn = tk.Label(form_content, text="Se connecter", font=self.button_font,
                            bg=self.colors['primary'], fg='white',
                            cursor='hand2', padx=40, pady=15)
        login_btn.bind('<Button-1>', lambda e: self.login())
        login_btn.pack(pady=(10, 30))
        
        # Lien inscription
        register_link = tk.Label(form_content, text="Pas encore de compte ? Créer un compte →", 
                                font=('Segoe UI', 11), bg=self.colors['background'], 
                                fg=self.colors['primary_light'], cursor='hand2')
        register_link.bind('<Button-1>', lambda e: self.show_register_form())
        register_link.pack()
    
    def show_register_form(self):
        """Affiche le formulaire d'inscription élégant"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True)
        
        # Formulaire à gauche
        form_frame = tk.Frame(main_frame, bg=self.colors['background'], padx=80)
        form_frame.pack(side='left', fill='both', expand=True)
        
        # En-tête
        header_frame = tk.Frame(form_frame, bg=self.colors['background'])
        header_frame.pack(fill='x', pady=(60, 40))
        
        back_btn = tk.Label(header_frame, text="←", font=('Segoe UI', 24),
                           bg=self.colors['background'], fg=self.colors['text_secondary'],
                           cursor='hand2')
        back_btn.bind('<Button-1>', lambda e: self.show_login_screen())
        back_btn.pack(side='left')
        
        tk.Label(header_frame, text="Créer un compte", font=self.heading_font,
                bg=self.colors['background'], fg=self.colors['text_primary']).pack(side='left', padx=20)
        
        # Formulaire à deux colonnes
        form_grid = tk.Frame(form_frame, bg=self.colors['background'])
        form_grid.pack(fill='x', pady=20)
        
        # Champs de base
        fields = [
            ("Prénom", "firstname"),
            ("Nom", "lastname"),
            ("Email", "email"),
            ("Mot de passe", "password"),
            ("Âge", "age"),
            ("Taille (cm)", "height"),
            ("Poids (kg)", "weight")
        ]
        
        self.register_entries = {}
        
        for i, (label_text, field_name) in enumerate(fields):
            row = i // 2
            col = i % 2
            
            frame = tk.Frame(form_grid, bg=self.colors['background'])
            frame.grid(row=row, column=col, padx=15, pady=10, sticky='ew')
            
            tk.Label(frame, text=label_text, font=('Segoe UI', 11, 'bold'),
                    bg=self.colors['background'], fg=self.colors['text_secondary']).pack(anchor='w')
            
            entry_frame = tk.Frame(frame, bg=self.colors['card_bg'], height=45)
            entry_frame.pack(fill='x', pady=(5, 0))
            entry_frame.pack_propagate(False)
            
            entry = tk.Entry(entry_frame, font=self.body_font, bg=self.colors['card_bg'],
                            fg=self.colors['text_primary'], bd=0, insertbackground='white')
            if field_name == 'password':
                entry.config(show='•')
            entry.pack(fill='both', expand=True, padx=15)
            
            self.register_entries[field_name] = entry
        
        # Objectif
        tk.Label(form_grid, text="Objectif", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['background'], fg=self.colors['text_secondary']).grid(row=4, column=0, sticky='w', padx=15, pady=(20, 5))
        
        goal_frame = tk.Frame(form_grid, bg=self.colors['card_bg'])
        goal_frame.grid(row=5, column=0, columnspan=2, sticky='ew', padx=15, pady=(0, 20))
        
        self.goal_var = tk.StringVar(value="maintenir")
        goals = [("💪 Prise de masse", "gain"), ("⚖️ Maintenir", "maintenir"), ("🔥 Perte de poids", "loss")]
        
        for text, value in goals:
            btn = tk.Radiobutton(goal_frame, text=text, variable=self.goal_var, value=value,
                                font=self.body_font, bg=self.colors['card_bg'],
                                fg=self.colors['text_primary'], selectcolor=self.colors['primary'])
            btn.pack(side='left', padx=10)
        
        # Niveau d'activité
        tk.Label(form_grid, text="Niveau d'activité", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['background'], fg=self.colors['text_secondary']).grid(row=6, column=0, sticky='w', padx=15, pady=(0, 5))
        
        activity_frame = tk.Frame(form_grid, bg=self.colors['card_bg'])
        activity_frame.grid(row=7, column=0, columnspan=2, sticky='ew', padx=15, pady=(0, 30))
        
        self.activity_var = tk.StringVar(value="moderate")
        activities = [
            ("🛋️ Sédentaire", "sedentary"),
            ("🚶‍♂️ Léger", "light"),
            ("🏃‍♂️ Modéré", "moderate"),
            ("💪 Actif", "active"),
            ("🔥 Très actif", "very_active")
        ]
        
        for text, value in activities:
            btn = tk.Radiobutton(activity_frame, text=text, variable=self.activity_var, value=value,
                                font=self.body_font, bg=self.colors['card_bg'],
                                fg=self.colors['text_primary'], selectcolor=self.colors['primary'])
            btn.pack(side='left', padx=10)
        
        # Bouton d'inscription
        register_btn = tk.Label(form_grid, text="Créer mon compte", font=self.button_font,
                               bg=self.colors['primary'], fg='white',
                               cursor='hand2', padx=40, pady=15)
        register_btn.bind('<Button-1>', lambda e: self.register())
        register_btn.grid(row=8, column=0, columnspan=2, pady=20)
        
        # Lien connexion
        login_link = tk.Label(form_grid, text="Déjà un compte ? Se connecter →", 
                             font=('Segoe UI', 11), bg=self.colors['background'], 
                             fg=self.colors['primary_light'], cursor='hand2')
        login_link.bind('<Button-1>', lambda e: self.show_login_form())
        login_link.grid(row=9, column=0, columnspan=2, pady=10)
        
        # Sidebar à droite
        sidebar = tk.Frame(main_frame, bg=self.colors['card_bg'], width=300)
        sidebar.pack(side='right', fill='y')
        sidebar.pack_propagate(False)
        
        sidebar_content = tk.Frame(sidebar, bg=self.colors['card_bg'], padx=30)
        sidebar_content.pack(fill='both', expand=True)
        
        tk.Label(sidebar_content, text="🎯 Bienvenue !", font=self.heading_font,
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(pady=(40, 20))
        
        benefits = [
            ("📊", "Suivi personnalisé de vos progrès"),
            ("🍽️", "Plans de repas adaptés à vos objectifs"),
            ("📱", "Accès depuis tous vos appareils"),
            ("👨‍⚕️", "Recommandations nutritionnelles expertes"),
            ("💾", "Sauvegarde illimitée de vos plans")
        ]
        
        for icon, text in benefits:
            frame = tk.Frame(sidebar_content, bg=self.colors['card_bg'])
            frame.pack(fill='x', pady=10)
            tk.Label(frame, text=icon, font=('Segoe UI', 20),
                    bg=self.colors['card_bg'], fg=self.colors['primary']).pack(side='left')
            tk.Label(frame, text=text, font=self.body_font,
                    bg=self.colors['card_bg'], fg=self.colors['text_secondary'],
                    wraplength=200).pack(side='left', padx=10)
    
    def login(self):
        """Gère la connexion"""
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
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
                'weight': user[6],
                'age': user[7],
                'goal': user[8],
                'activity_level': user[9]
            }
            messagebox.showinfo("Succès", f"Bienvenue {user[1]} !")
            self.show_dashboard()
        else:
            messagebox.showerror("Erreur", "Email ou mot de passe incorrect")
    
    def register(self):
        """Gère l'inscription"""
        try:
            data = {k: v.get() for k, v in self.register_entries.items()}
            
            if not all(data.values()):
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
                return
            
            self.cursor.execute('''
                INSERT INTO users (firstname, lastname, email, password, age, height, weight, goal, activity_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data['firstname'], data['lastname'], data['email'], data['password'],
                  int(data['age']), int(data['height']), float(data['weight']),
                  self.goal_var.get(), self.activity_var.get()))
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Compte créé avec succès !")
            self.show_login_screen()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Cet email est déjà utilisé")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")
    
    def demo_mode(self):
        """Mode démo sans connexion"""
        self.current_user = {
            'id': 0,
            'firstname': 'Invité',
            'lastname': 'Demo',
            'email': 'demo@example.com',
            'height': 175,
            'weight': 70,
            'age': 30,
            'goal': 'maintenir',
            'activity_level': 'moderate'
        }
        self.show_dashboard()
    
    def show_dashboard(self):
        """Affiche le tableau de bord moderne"""
        self.clear_window()
        
        # Sidebar
        sidebar = tk.Frame(self.root, bg=self.colors['card_bg'], width=280)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Logo sidebar
        logo_frame = tk.Frame(sidebar, bg=self.colors['card_bg'], height=120)
        logo_frame.pack(fill='x')
        logo_frame.pack_propagate(False)
        
        tk.Label(logo_frame, text="🍽️", font=('Segoe UI', 36),
                bg=self.colors['card_bg'], fg=self.colors['primary']).place(relx=0.5, rely=0.5, anchor='center')
        
        # Menu sidebar
        menu_frame = tk.Frame(sidebar, bg=self.colors['card_bg'])
        menu_frame.pack(fill='both', expand=True, padx=20)
        
        menu_items = [
            ("📊", "Tableau de bord", self.show_dashboard),
            ("🍽️", "Générateur de repas", self.show_meal_generator),
            ("📖", "Recettes", self.show_recipes),
            ("💾", "Plans sauvegardés", self.show_saved_plans),
            ("⭐", "Favoris", self.show_favorites),
            ("📈", "Progression", self.show_progress),
            ("👤", "Profil", self.show_profile)
        ]
        
        for icon, text, command in menu_items:
            btn = self.create_menu_button(menu_frame, icon, text, command)
            btn.pack(fill='x', pady=5)
        
        # Bouton déconnexion
        logout_btn = self.create_menu_button(menu_frame, "🚪", "Déconnexion", self.show_login_screen)
        logout_btn.pack(side='bottom', fill='x', pady=20)
        
        # Contenu principal
        main_content = tk.Frame(self.root, bg=self.colors['background'])
        main_content.pack(side='right', fill='both', expand=True, padx=30, pady=30)
        
        # Header
        header = tk.Frame(main_content, bg=self.colors['background'])
        header.pack(fill='x', pady=(0, 30))
        
        tk.Label(header, text=f"👋 Bonjour, {self.current_user['firstname']} !", 
                font=self.heading_font, bg=self.colors['background'], 
                fg=self.colors['text_primary']).pack(side='left')
        
        # Date
        date_label = tk.Label(header, text=datetime.now().strftime("%d %B %Y"),
                             font=('Segoe UI', 12), bg=self.colors['background'],
                             fg=self.colors['text_secondary'])
        date_label.pack(side='right')
        
        # Cartes de statistiques
        stats_frame = tk.Frame(main_content, bg=self.colors['background'])
        stats_frame.pack(fill='x', pady=(0, 40))
        
        # Récupérer les statistiques
        self.cursor.execute('SELECT COUNT(*) FROM saved_plans WHERE user_id = ?', 
                          (self.current_user['id'],))
        plan_count = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM recipes')
        recipe_count = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM favorites WHERE user_id = ?',
                          (self.current_user['id'],))
        favorite_count = self.cursor.fetchone()[0]
        
        stats_data = [
            ("📅", str(plan_count), "Plans", self.colors['primary']),
            ("🍽️", str(recipe_count), "Recettes", self.colors['secondary']),
            ("⭐", str(favorite_count), "Favoris", self.colors['accent']),
            ("🎯", "85%", "Objectif", self.colors['success'])
        ]
        
        for i, (icon, value, label, color) in enumerate(stats_data):
            card = self.create_stat_card(stats_frame, icon, value, label, color)
            card.grid(row=0, column=i, padx=10, sticky='nsew')
        
        # Section recommandations
        tk.Label(main_content, text="🔥 Recommandations pour vous", 
                font=('Segoe UI', 18, 'bold'), bg=self.colors['background'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(20, 15))
        
        # Récupérer des recettes aléatoires
        self.cursor.execute('SELECT * FROM recipes ORDER BY RANDOM() LIMIT 3')
        random_recipes = self.cursor.fetchall()
        
        recipes_frame = tk.Frame(main_content, bg=self.colors['background'])
        recipes_frame.pack(fill='x', pady=(0, 40))
        
        for i, recipe in enumerate(random_recipes):
            card = self.create_recipe_card(recipes_frame, recipe, width=320)
            card.grid(row=0, column=i, padx=10)
        
        # Actions rapides
        tk.Label(main_content, text="⚡ Actions rapides", 
                font=('Segoe UI', 18, 'bold'), bg=self.colors['background'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 15))
        
        actions_frame = tk.Frame(main_content, bg=self.colors['background'])
        actions_frame.pack(fill='x')
        
        quick_actions = [
            ("🎯", "Générer un plan", "Plan personnalisé 7 jours", self.show_meal_generator),
            ("🔍", "Rechercher", "Trouver des recettes", self.show_recipe_search),
            ("📋", "Voir mes plans", "Plans sauvegardés", self.show_saved_plans),
            ("🍎", "Conseils santé", "Astuces nutrition", self.show_health_tips)
        ]
        
        for i, (icon, title, subtitle, command) in enumerate(quick_actions):
            card = self.create_quick_action_card(actions_frame, icon, title, subtitle, command)
            card.grid(row=0, column=i, padx=10)
    
    def create_menu_button(self, parent, icon, text, command):
        """Crée un bouton de menu moderne"""
        btn = tk.Frame(parent, bg=self.colors['card_bg'], height=50)
        btn.pack_propagate(False)
        
        def on_enter(e):
            btn.configure(bg=self.colors['card_hover'])
            icon_label.configure(bg=self.colors['card_hover'])
            text_label.configure(bg=self.colors['card_hover'])
        
        def on_leave(e):
            btn.configure(bg=self.colors['card_bg'])
            icon_label.configure(bg=self.colors['card_bg'])
            text_label.configure(bg=self.colors['card_bg'])
        
        # Contenu
        icon_label = tk.Label(btn, text=icon, font=('Segoe UI', 18),
                             bg=self.colors['card_bg'], fg=self.colors['text_secondary'])
        icon_label.pack(side='left', padx=20)
        
        text_label = tk.Label(btn, text=text, font=('Segoe UI', 12),
                             bg=self.colors['card_bg'], fg=self.colors['text_primary'])
        text_label.pack(side='left', fill='y')
        
        # Bind events
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        btn.bind('<Button-1>', lambda e: command())
        
        for widget in [btn, icon_label, text_label]:
            widget.bind('<Button-1>', lambda e: command())
            widget.configure(cursor='hand2')
        
        return btn
    
    def create_stat_card(self, parent, icon, value, label, color):
        """Crée une carte de statistique"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], width=180, height=120)
        card.pack_propagate(False)
        
        content = tk.Frame(card, bg=self.colors['card_bg'])
        content.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(content, text=icon, font=('Segoe UI', 24),
                bg=self.colors['card_bg'], fg=color).pack()
        
        tk.Label(content, text=value, font=('Segoe UI', 28, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(pady=5)
        
        tk.Label(content, text=label, font=('Segoe UI', 12),
                bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack()
        
        return card
    
    def create_quick_action_card(self, parent, icon, title, subtitle, command):
        """Crée une carte d'action rapide"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], width=220, height=100)
        card.pack_propagate(False)
        
        def on_enter(e):
            card.configure(bg=self.colors['card_hover'])
        
        def on_leave(e):
            card.configure(bg=self.colors['card_bg'])
        
        content = tk.Frame(card, bg=self.colors['card_bg'], padx=20)
        content.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(content, text=icon, font=('Segoe UI', 24),
                bg=self.colors['card_bg'], fg=self.colors['primary']).pack(anchor='w')
        
        tk.Label(content, text=title, font=('Segoe UI', 14, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(anchor='w', pady=(5, 2))
        
        tk.Label(content, text=subtitle, font=('Segoe UI', 10),
                bg=self.colors['card_bg'], fg=self.colors['text_secondary'],
                wraplength=180).pack(anchor='w')
        
        # Bind events
        if command:
            card.bind('<Enter>', on_enter)
            card.bind('<Leave>', on_leave)
            card.bind('<Button-1>', lambda e: command())
            for widget in content.winfo_children():
                widget.bind('<Button-1>', lambda e: command())
                widget.configure(cursor='hand2')
            card.configure(cursor='hand2')
        
        return card
    
    def show_meal_generator(self):
        """Affiche le générateur de repas"""
        self.clear_window()
        self.show_sidebar()
        
        # Contenu principal
        main_content = tk.Frame(self.root, bg=self.colors['background'])
        main_content.pack(side='right', fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(main_content, text="🎯 Générateur de Repas", 
                font=self.heading_font, bg=self.colors['background'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 30))
        
        # Formulaire de génération
        form_card = tk.Frame(main_content, bg=self.colors['card_bg'], padx=30, pady=30)
        form_card.pack(fill='x', pady=(0, 20))
        
        tk.Label(form_card, text="⚙️ Paramètres du plan", font=('Segoe UI', 18, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 20))
        
        # Grille paramètres
        grid = tk.Frame(form_card, bg=self.colors['card_bg'])
        grid.pack(fill='x')
        
        # Nombre de jours
        tk.Label(grid, text="Nombre de jours:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=0, column=0, sticky='w', pady=10)
        
        self.days_var = tk.StringVar(value="7")
        days_combo = ttk.Combobox(grid, textvariable=self.days_var, 
                                 values=["3", "5", "7", "14", "30"], 
                                 width=10, font=self.body_font)
        days_combo.grid(row=0, column=1, padx=20, pady=10)
        
        # Calories cible
        tk.Label(grid, text="Calories par jour:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=0, column=2, sticky='w', pady=10)
        
        self.calories_var = tk.StringVar(value="2000")
        calories_combo = ttk.Combobox(grid, textvariable=self.calories_var, 
                                     values=["1500", "1800", "2000", "2200", "2500", "3000"], 
                                     width=10, font=self.body_font)
        calories_combo.grid(row=0, column=3, padx=20, pady=10)
        
        # Régime alimentaire
        tk.Label(grid, text="Régime:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=1, column=0, sticky='w', pady=10)
        
        self.diet_var = tk.StringVar(value="Tout")
        diet_combo = ttk.Combobox(grid, textvariable=self.diet_var, 
                                 values=["Tout", "Végétarien", "Végétalien", "Sans gluten", "Faible en glucides"], 
                                 width=12, font=self.body_font)
        diet_combo.grid(row=1, column=1, padx=20, pady=10)
        
        # Difficulté
        tk.Label(grid, text="Difficulté:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=1, column=2, sticky='w', pady=10)
        
        self.difficulty_var = tk.StringVar(value="Tout")
        difficulty_combo = ttk.Combobox(grid, textvariable=self.difficulty_var, 
                                       values=["Tout", "Facile", "Moyen", "Difficile"], 
                                       width=10, font=self.body_font)
        difficulty_combo.grid(row=1, column=3, padx=20, pady=10)
        
        # Boutons
        btn_frame = tk.Frame(form_card, bg=self.colors['card_bg'])
        btn_frame.pack(pady=20)
        
        generate_btn = tk.Label(btn_frame, text="🎯 Générer le plan", font=self.button_font,
                               bg=self.colors['primary'], fg='white',
                               cursor='hand2', padx=30, pady=12)
        generate_btn.bind('<Button-1>', lambda e: self.generate_meal_plan())
        generate_btn.pack(side='left', padx=5)
        
        save_btn = tk.Label(btn_frame, text="💾 Sauvegarder", font=self.button_font,
                           bg=self.colors['secondary'], fg='white',
                           cursor='hand2', padx=30, pady=12)
        save_btn.bind('<Button-1>', lambda e: self.save_generated_plan())
        save_btn.pack(side='left', padx=5)
        
        # Zone de résultats
        results_frame = tk.Frame(main_content, bg=self.colors['card_bg'])
        results_frame.pack(fill='both', expand=True, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, font=('Consolas', 11),
                                                     bg=self.colors['card_bg'], fg=self.colors['text_primary'],
                                                     insertbackground='white', wrap=tk.WORD)
        self.results_text.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Générer un exemple
        self.generate_sample_plan()
    
    def generate_sample_plan(self):
        """Génère un plan d'exemple"""
        sample_text = "╔════════════════════════════════════════╗\n"
        sample_text += "║     BIENVENUE AU GÉNÉRATEUR DE REPAS    ║\n"
        sample_text += "╚════════════════════════════════════════╝\n\n"
        sample_text += "Configurez vos paramètres ci-dessus et cliquez sur\n"
        sample_text += "'🎯 Générer le plan' pour créer votre plan personnalisé!\n\n"
        sample_text += "💡 Conseils nutritionnels :\n"
        sample_text += "   • Pour une perte de poids : 1500-1800 calories/jour\n"
        sample_text += "   • Pour le maintien : 2000-2200 calories/jour\n"
        sample_text += "   • Pour prise de masse : 2500-3000 calories/jour\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, sample_text)
    
    def generate_meal_plan(self):
        """Génère un plan alimentaire personnalisé"""
        try:
            days = int(self.days_var.get())
            target_calories = int(self.calories_var.get())
            diet = self.diet_var.get()
            difficulty = self.difficulty_var.get()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides")
            return
        
        # Construire la requête SQL
        query = "SELECT * FROM recipes WHERE 1=1"
        params = []
        
        if diet != "Tout":
            if diet == "Végétarien":
                query += " AND (tags LIKE ? OR tags LIKE ?)"
                params.extend(['%végétarien%', '%vegetarian%'])
            elif diet == "Végétalien":
                query += " AND (tags LIKE ? OR tags LIKE ?)"
                params.extend(['%végétalien%', '%vegan%'])
        
        if difficulty != "Tout":
            query += " AND difficulty = ?"
            params.append(difficulty.lower())
        
        self.cursor.execute(query, params)
        all_recipes = self.cursor.fetchall()
        
        if not all_recipes:
            messagebox.showerror("Erreur", "Aucune recette ne correspond à vos critères")
            return
        
        # Organiser par catégorie
        categories = {
            'Petit-déjeuner': [r for r in all_recipes if r[2] == 'Petit-déjeuner'],
            'Déjeuner': [r for r in all_recipes if r[2] == 'Déjeuner'],
            'Dîner': [r for r in all_recipes if r[2] == 'Dîner']
        }
        
        # Générer le plan
        plan_text = self.create_plan_header(days, target_calories, diet, difficulty)
        total_calories = 0
        
        for day in range(1, days + 1):
            daily_text = f"\n{'='*60}\n"
            daily_text += f"✨ JOUR {day:02d}\n"
            daily_text += f"{'='*60}\n\n"
            
            daily_calories = 0
            
            for meal_type in ['Petit-déjeuner', 'Déjeuner', 'Dîner']:
                available = categories.get(meal_type, [])
                if available:
                    recipe = random.choice(available)
                    daily_text += f"🍽️  {meal_type}\n"
                    daily_text += f"   📛 {recipe[1]}\n"
                    daily_text += f"   ⏱️  {recipe[11]} min | 🔥 {recipe[6]} cal | 🎯 {recipe[12]}\n"
                    daily_text += f"   📝 {recipe[4][:100]}...\n\n"
                    daily_calories += recipe[6]
                else:
                    daily_text += f"🍽️  {meal_type}\n"
                    daily_text += f"   ⚠️  Aucune recette disponible\n\n"
            
            daily_text += f"📊 TOTAL JOUR {day:02d}: {daily_calories} calories\n"
            plan_text += daily_text
            total_calories += daily_calories
        
        # Ajouter le résumé
        plan_text += self.create_plan_summary(days, target_calories, total_calories)
        
        # Afficher le plan
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, plan_text)
        
        # Stocker pour sauvegarde
        self.current_generated_plan = {
            'text': plan_text,
            'days': days,
            'calories': target_calories,
            'diet': diet,
            'difficulty': difficulty
        }
    
    def create_plan_header(self, days, calories, diet, difficulty):
        """Crée l'en-tête du plan"""
        header = "╔══════════════════════════════════════════════════╗\n"
        header += "║              📋 SMARTMEAL PLANNER               ║\n"
        header += "║           Plan Alimentaire Personnalisé         ║\n"
        header += "╚══════════════════════════════════════════════════╝\n\n"
        
        header += f"🔮 Durée: {days} jours\n"
        header += f"🎯 Objectif: {calories} calories/jour\n"
        header += f"🥗 Régime: {diet}\n"
        header += f"⚡ Difficulté: {difficulty}\n"
        header += f"📅 Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        header += "═" * 60 + "\n\n"
        
        return header
    
    def create_plan_summary(self, days, target_calories, total_calories):
        """Crée le résumé du plan"""
        avg_daily = total_calories // days
        deviation = abs(avg_daily - target_calories)
        
        summary = "\n" + "═" * 60 + "\n"
        summary += "📈 RÉSUMÉ DU PLAN\n"
        summary += "═" * 60 + "\n\n"
        
        summary += f"📅 Durée totale: {days} jours\n"
        summary += f"🎯 Calories cible/jour: {target_calories} cal\n"
        summary += f"🔥 Calories totales: {total_calories} cal\n"
        summary += f"📊 Moyenne réelle/jour: {avg_daily} cal\n"
        summary += f"📉 Écart moyen: {deviation} cal\n\n"
        
        # Évaluation
        if deviation <= 100:
            summary += "✅ Excellent ! Le plan est très proche de votre objectif.\n"
        elif deviation <= 300:
            summary += "⚠️  Bon ! Le plan est raisonnablement proche de votre objectif.\n"
        else:
            summary += "📝 À ajuster ! Considérez modifier vos paramètres.\n"
        
        summary += "\n💡 Conseils :\n"
        summary += "   • Buvez au moins 2L d'eau par jour\n"
        summary += "   • Faites 30 minutes d'activité physique quotidienne\n"
        summary += "   • Écoutez votre corps et ajustez selon vos besoins\n"
        
        return summary
    
    def save_generated_plan(self):
        """Sauvegarde le plan généré"""
        if not hasattr(self, 'current_generated_plan'):
            messagebox.showerror("Erreur", "Aucun plan à sauvegarder")
            return
        
        # Fenêtre de sauvegarde
        save_window = tk.Toplevel(self.root)
        save_window.title("Sauvegarder le plan")
        save_window.geometry("400x300")
        save_window.configure(bg=self.colors['background'])
        
        tk.Label(save_window, text="💾 Sauvegarder le plan", 
                font=self.heading_font, bg=self.colors['background'],
                fg=self.colors['text_primary']).pack(pady=30)
        
        tk.Label(save_window, text="Nom du plan:", font=('Segoe UI', 12),
                bg=self.colors['background'], fg=self.colors['text_secondary']).pack(pady=10)
        
        plan_name_var = tk.StringVar(value=f"Plan {datetime.now().strftime('%d/%m')}")
        name_entry = tk.Entry(save_window, font=self.body_font, 
                             bg=self.colors['card_bg'], fg=self.colors['text_primary'],
                             textvariable=plan_name_var)
        name_entry.pack(pady=10, padx=50, fill='x')
        
        def save():
            name = plan_name_var.get()
            if not name:
                messagebox.showerror("Erreur", "Veuillez entrer un nom")
                return
            
            try:
                self.cursor.execute('''
                    INSERT INTO saved_plans (user_id, plan_name, plan_text, calories_target, days_count)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.current_user['id'], name, 
                      self.current_generated_plan['text'],
                      self.current_generated_plan['calories'],
                      self.current_generated_plan['days']))
                self.conn.commit()
                
                messagebox.showinfo("Succès", f"Plan '{name}' sauvegardé !")
                save_window.destroy()
                self.show_saved_plans()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
        
        save_btn = tk.Label(save_window, text="Sauvegarder", font=self.button_font,
                           bg=self.colors['primary'], fg='white',
                           cursor='hand2', padx=30, pady=10)
        save_btn.bind('<Button-1>', lambda e: save())
        save_btn.pack(pady=30)
    
    def show_sidebar(self):
        """Affiche la sidebar"""
        sidebar = tk.Frame(self.root, bg=self.colors['card_bg'], width=280)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        menu_items = [
            ("📊", "Tableau de bord", self.show_dashboard),
            ("🍽️", "Générateur", self.show_meal_generator),
            ("📖", "Recettes", self.show_recipes),
            ("💾", "Plans", self.show_saved_plans),
            ("⭐", "Favoris", self.show_favorites),
            ("📈", "Progression", self.show_progress),
            ("👤", "Profil", self.show_profile)
        ]
        
        for icon, text, command in menu_items:
            btn = self.create_menu_button(sidebar, icon, text, command)
            btn.pack(fill='x')
    
    def show_recipes(self):
        """Affiche la page des recettes avec recherche"""
        self.clear_window()
        self.show_sidebar()
        
        main_content = tk.Frame(self.root, bg=self.colors['background'])
        main_content.pack(side='right', fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(main_content, text="📖 Recettes & Idées Repas", 
                font=self.heading_font, bg=self.colors['background'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 30))
        
        # Barre de recherche
        search_frame = tk.Frame(main_content, bg=self.colors['card_bg'], padx=20, pady=20)
        search_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(search_frame, text="🔍 Rechercher une recette", 
                font=('Segoe UI', 16, 'bold'), bg=self.colors['card_bg'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 15))
        
        # Champs de recherche
        search_grid = tk.Frame(search_frame, bg=self.colors['card_bg'])
        search_grid.pack(fill='x')
        
        # Mot-clé
        tk.Label(search_grid, text="Mot-clé:", font=('Segoe UI', 11),
                bg=self.colors['card_bg'], fg=self.colors['text_secondary']).grid(row=0, column=0, sticky='w', padx=(0, 10))
        
        self.search_keyword = tk.Entry(search_grid, font=self.body_font, 
                                      bg=self.colors['background'], fg=self.colors['text_primary'],
                                      width=20)
        self.search_keyword.grid(row=0, column=1, padx=(0, 20))
        
        # Catégorie
        tk.Label(search_grid, text="Catégorie:", font=('Segoe UI', 11),
                bg=self.colors['card_bg'], fg=self.colors['text_secondary']).grid(row=0, column=2, sticky='w', padx=(0, 10))
        
        self.search_category = ttk.Combobox(search_grid, values=["Toutes", "Petit-déjeuner", "Déjeuner", "Dîner"],
                                           font=self.body_font, width=15)
        self.search_category.set("Toutes")
        self.search_category.grid(row=0, column=3, padx=(0, 20))
        
        # Difficulté
        tk.Label(search_grid, text="Difficulté:", font=('Segoe UI', 11),
                bg=self.colors['card_bg'], fg=self.colors['text_secondary']).grid(row=0, column=4, sticky='w', padx=(0, 10))
        
        self.search_difficulty = ttk.Combobox(search_grid, values=["Toutes", "Facile", "Moyen"],
                                             font=self.body_font, width=12)
        self.search_difficulty.set("Toutes")
        self.search_difficulty.grid(row=0, column=5)
        
        # Bouton recherche
        search_btn = tk.Label(search_grid, text="Rechercher", font=('Segoe UI', 11, 'bold'),
                             bg=self.colors['primary'], fg='white',
                             cursor='hand2', padx=15, pady=8)
        search_btn.bind('<Button-1>', lambda e: self.search_recipes())
        search_btn.grid(row=0, column=6, padx=(20, 0))
        
        # Zone des résultats
        results_frame = tk.Frame(main_content, bg=self.colors['background'])
        results_frame.pack(fill='both', expand=True)
        
        # Canvas pour le défilement
        self.canvas = tk.Canvas(results_frame, bg=self.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['background'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Charger toutes les recettes initialement
        self.search_recipes()
    
    def search_recipes(self):
        """Effectue la recherche de recettes"""
        # Nettoyer l'affichage précédent
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Construire la requête
        query = "SELECT * FROM recipes WHERE 1=1"
        params = []
        
        keyword = self.search_keyword.get()
        if keyword:
            query += " AND (name LIKE ? OR ingredients LIKE ? OR tags LIKE ?)"
            params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])
        
        category = self.search_category.get()
        if category != "Toutes":
            query += " AND category = ?"
            params.append(category)
        
        difficulty = self.search_difficulty.get()
        if difficulty != "Toutes":
            query += " AND difficulty = ?"
            params.append(difficulty.lower())
        
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        
        # Afficher les résultats
        if not results:
            tk.Label(self.scrollable_frame, text="Aucune recette trouvée",
                    font=('Segoe UI', 14), bg=self.colors['background'],
                    fg=self.colors['text_secondary']).pack(pady=50)
            return
        
        # Afficher en grille
        row, col = 0, 0
        for recipe in results:
            card = self.create_recipe_card(self.scrollable_frame, recipe)
            card.grid(row=row, column=col, padx=10, pady=10)
            
            col += 1
            if col > 2:  # 3 cartes par ligne
                col = 0
                row += 1
        
        # Ajuster la taille du canvas
        self.scrollable_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def show_recipe_detail(self, recipe_id):
        """Affiche les détails d'une recette"""
        self.cursor.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,))
        recipe = self.cursor.fetchone()
        
        if not recipe:
            messagebox.showerror("Erreur", "Recette non trouvée")
            return
        
        # Fenêtre de détail
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Recette - {recipe[1]}")
        detail_window.geometry("900x700")
        detail_window.configure(bg=self.colors['background'])
        
        # Image header
        header_frame = tk.Frame(detail_window, bg=self.colors['primary'], height=200)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=self.category_icons.get(recipe[2], '🍽️'), 
                font=('Segoe UI', 72), bg=self.colors['primary'], fg='white').place(relx=0.5, rely=0.5, anchor='center')
        
        # Contenu
        content_frame = tk.Frame(detail_window, bg=self.colors['background'], padx=40, pady=30)
        content_frame.pack(fill='both', expand=True)
        
        # Titre
        tk.Label(content_frame, text=recipe[1], font=('Segoe UI', 28, 'bold'),
                bg=self.colors['background'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 10))
        
        # Badges
        badges_frame = tk.Frame(content_frame, bg=self.colors['background'])
        badges_frame.pack(anchor='w', pady=(0, 20))
        
        badges = [
            (recipe[2], self.colors['primary']),
            (f"{recipe[11]} min", self.colors['secondary']),
            (f"{recipe[6]} cal", self.colors['accent']),
            (recipe[12], self.colors['success'])
        ]
        
        for text, color in badges:
            badge = tk.Label(badges_frame, text=text, font=('Segoe UI', 10, 'bold'),
                            bg=color, fg='white', padx=10, pady=5)
            badge.pack(side='left', padx=5)
        
        # Informations nutritionnelles
        tk.Label(content_frame, text="📊 Valeurs nutritionnelles", 
                font=('Segoe UI', 16, 'bold'), bg=self.colors['background'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(10, 10))
        
        nutrition_frame = tk.Frame(content_frame, bg=self.colors['card_bg'], padx=20, pady=15)
        nutrition_frame.pack(fill='x', pady=(0, 20))
        
        nutrients = [
            ("🔥 Calories", f"{recipe[6]} cal"),
            ("💪 Protéines", f"{recipe[7]}g"),
            ("🌾 Glucides", f"{recipe[8]}g"),
            ("🥑 Lipides", f"{recipe[9]}g")
        ]
        
        for i, (label, value) in enumerate(nutrients):
            tk.Label(nutrition_frame, text=label, font=('Segoe UI', 11),
                    bg=self.colors['card_bg'], fg=self.colors['text_secondary']).grid(row=0, column=i*2, padx=10)
            tk.Label(nutrition_frame, text=value, font=('Segoe UI', 14, 'bold'),
                    bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=1, column=i*2, padx=10)
        
        # Ingrédients
        tk.Label(content_frame, text="🥕 Ingrédients", 
                font=('Segoe UI', 16, 'bold'), bg=self.colors['background'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(10, 10))
        
        ingredients_text = scrolledtext.ScrolledText(content_frame, height=6, font=self.body_font,
                                                    bg=self.colors['card_bg'], fg=self.colors['text_primary'],
                                                    wrap=tk.WORD)
        ingredients_text.pack(fill='x', pady=(0, 20))
        ingredients_text.insert(1.0, recipe[4])
        ingredients_text.config(state='disabled')
        
        # Instructions
        tk.Label(content_frame, text="📝 Instructions", 
                font=('Segoe UI', 16, 'bold'), bg=self.colors['background'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(10, 10))
        
        instructions_text = scrolledtext.ScrolledText(content_frame, height=8, font=self.body_font,
                                                     bg=self.colors['card_bg'], fg=self.colors['text_primary'],
                                                     wrap=tk.WORD)
        instructions_text.pack(fill='both', expand=True)
        instructions_text.insert(1.0, recipe[5])
        instructions_text.config(state='disabled')
    
    def show_saved_plans(self):
        """Affiche les plans sauvegardés"""
        self.clear_window()
        self.show_sidebar()
        
        main_content = tk.Frame(self.root, bg=self.colors['background'])
        main_content.pack(side='right', fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(main_content, text="💾 Plans Sauvegardés", 
                font=self.heading_font, bg=self.colors['background'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 30))
        
        # Récupérer les plans
        self.cursor.execute('''
            SELECT id, plan_name, days_count, calories_target, created_at 
            FROM saved_plans 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (self.current_user['id'],))
        
        plans = self.cursor.fetchall()
        
        if not plans:
            tk.Label(main_content, text="📭 Aucun plan sauvegardé",
                    font=('Segoe UI', 16), bg=self.colors['background'],
                    fg=self.colors['text_secondary']).place(relx=0.5, rely=0.5, anchor='center')
            return
        
        # Canvas pour le défilement
        canvas = tk.Canvas(main_content, bg=self.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Afficher les plans
        for i, (plan_id, name, days, calories, created_at) in enumerate(plans):
            card = self.create_saved_plan_card(scrollable_frame, plan_id, name, days, calories, created_at)
            card.pack(fill='x', pady=10)
    
    def create_saved_plan_card(self, parent, plan_id, name, days, calories, created_at):
        """Crée une carte pour un plan sauvegardé"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(card, bg=self.colors['card_bg'])
        header_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(header_frame, text=name, font=('Segoe UI', 18, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(side='left')
        
        tk.Label(header_frame, text=f"📅 {created_at[:10]}", font=('Segoe UI', 11),
                bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack(side='right')
        
        # Informations
        info_frame = tk.Frame(card, bg=self.colors['card_bg'])
        info_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(info_frame, text=f"⏱️  {days} jours", font=('Segoe UI', 12),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(side='left', padx=(0, 20))
        
        tk.Label(info_frame, text=f"🔥 {calories} cal/jour", font=('Segoe UI', 12),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(side='left')
        
        # Boutons d'action
        btn_frame = tk.Frame(card, bg=self.colors['card_bg'])
        btn_frame.pack(fill='x')
        
        view_btn = tk.Label(btn_frame, text="👁️ Voir", font=('Segoe UI', 11, 'bold'),
                           bg=self.colors['primary'], fg='white',
                           cursor='hand2', padx=15, pady=8)
        view_btn.bind('<Button-1>', lambda e: self.view_saved_plan(plan_id))
        view_btn.pack(side='left', padx=2)
        
        delete_btn = tk.Label(btn_frame, text="🗑️ Supprimer", font=('Segoe UI', 11, 'bold'),
                             bg=self.colors['danger'], fg='white',
                             cursor='hand2', padx=15, pady=8)
        delete_btn.bind('<Button-1>', lambda e: self.delete_saved_plan(plan_id))
        delete_btn.pack(side='left', padx=2)
        
        return card
    
    def view_saved_plan(self, plan_id):
        """Affiche un plan sauvegardé"""
        self.cursor.execute('SELECT plan_text FROM saved_plans WHERE id = ?', (plan_id,))
        result = self.cursor.fetchone()
        
        if result:
            plan_text = result[0]
            
            window = tk.Toplevel(self.root)
            window.title("Plan sauvegardé")
            window.geometry("800x600")
            window.configure(bg=self.colors['background'])
            
            text_widget = scrolledtext.ScrolledText(window, font=('Consolas', 11),
                                                   bg=self.colors['card_bg'], fg=self.colors['text_primary'])
            text_widget.pack(fill='both', expand=True, padx=20, pady=20)
            text_widget.insert(1.0, plan_text)
            text_widget.config(state='disabled')
    
    def delete_saved_plan(self, plan_id):
        """Supprime un plan sauvegardé"""
        if messagebox.askyesno("Confirmation", "Supprimer ce plan ?"):
            self.cursor.execute('DELETE FROM saved_plans WHERE id = ?', (plan_id,))
            self.conn.commit()
            messagebox.showinfo("Succès", "Plan supprimé")
            self.show_saved_plans()
    
    def show_favorites(self):
        """Affiche les recettes favorites"""
        messagebox.showinfo("Info", "Fonctionnalité à venir !")
    
    def show_progress(self):
        """Affiche la page de progression"""
        messagebox.showinfo("Info", "Fonctionnalité à venir !")
    
    def show_profile(self):
        """Affiche la page profil"""
        self.clear_window()
        self.show_sidebar()
        
        main_content = tk.Frame(self.root, bg=self.colors['background'])
        main_content.pack(side='right', fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(main_content, text="👤 Mon Profil", 
                font=self.heading_font, bg=self.colors['background'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 30))
        
        # Carte profil
        profile_card = tk.Frame(main_content, bg=self.colors['card_bg'], padx=30, pady=30)
        profile_card.pack(fill='x', pady=(0, 20))
        
        # Photo de profil (placeholder)
        profile_frame = tk.Frame(profile_card, bg=self.colors['primary'], width=100, height=100)
        profile_frame.pack(pady=(0, 20))
        profile_frame.pack_propagate(False)
        
        tk.Label(profile_frame, text="👤", font=('Segoe UI', 48),
                bg=self.colors['primary'], fg='white').place(relx=0.5, rely=0.5, anchor='center')
        
        # Informations
        tk.Label(profile_card, text=f"{self.current_user['firstname']} {self.current_user['lastname']}", 
                font=('Segoe UI', 24, 'bold'), bg=self.colors['card_bg'],
                fg=self.colors['text_primary']).pack(pady=(0, 10))
        
        tk.Label(profile_card, text=self.current_user['email'], 
                font=('Segoe UI', 14), bg=self.colors['card_bg'],
                fg=self.colors['text_secondary']).pack(pady=(0, 30))
        
        # Détails
        details_frame = tk.Frame(profile_card, bg=self.colors['card_bg'])
        details_frame.pack(fill='x')
        
        details = [
            ("📏 Taille", f"{self.current_user['height']} cm"),
            ("⚖️ Poids", f"{self.current_user['weight']} kg"),
            ("🎯 Objectif", self.current_user['goal'].capitalize()),
            ("🏃‍♂️ Activité", self.current_user['activity_level'].capitalize())
        ]
        
        for i, (label, value) in enumerate(details):
            if i % 2 == 0:
                row_frame = tk.Frame(details_frame, bg=self.colors['card_bg'])
                row_frame.pack(fill='x', pady=10)
            
            frame = tk.Frame(row_frame, bg=self.colors['card_bg'])
            frame.pack(side='left', padx=20)
            
            tk.Label(frame, text=label, font=('Segoe UI', 11),
                    bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack(anchor='w')
            tk.Label(frame, text=value, font=('Segoe UI', 16, 'bold'),
                    bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(anchor='w')
    
    def show_recipe_search(self):
        """Affiche la recherche de recettes"""
        self.show_recipes()
    
    def show_health_tips(self):
        """Affiche des conseils santé"""
        tips = [
            "💧 Buvez au moins 2L d'eau par jour",
            "🥦 Consommez 5 portions de fruits et légumes",
            "⚡ Limitez les sucres ajoutés",
            "🌙 Dormez 7-8 heures par nuit",
            "🏃‍♂️ 30 min d'activité physique quotidienne",
            "🧘‍♀️ Gérez votre stress",
            "⏰ Mangez à heures régulières",
            "🥑 Privilégiez les graisses saines"
        ]
        
        tip = random.choice(tips)
        messagebox.showinfo("💡 Conseil santé", tip)
    
    def clear_window(self):
        """Vide la fenêtre"""
        for widget in self.root.winfo_children():
            widget.destroy()

def main():
    try:
        root = tk.Tk()
        app = ModernSmartMealPlanner(root)
        
        # Centre la fenêtre
        root.eval('tk::PlaceWindow . center')
        
        root.mainloop()
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        input("Appuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()
