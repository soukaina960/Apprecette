import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import random
from datetime import datetime

class ModernSmartMealPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("🍽️ SmartMeal-Planner - Repas sains & intelligents")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0f172a')  # Fond bleu nuit moderne
        
        # Configuration des styles modernes
        self.setup_styles()
        
        self.current_user = None
        self.setup_database()
        self.show_login_screen()
    
    def setup_styles(self):
        """Configure les styles modernes"""
        style = ttk.Style()
        
        # Thème moderne
        style.theme_use('clam')
        
        # Couleurs modernes
        self.colors = {
            'primary': '#10b981',
            'primary_dark': '#059669',
            'primary_light': '#34d399',
            'background': '#0f172a',
            'card_bg': '#1e293b',
            'text_primary': '#f1f5f9',
            'text_secondary': '#94a3b8',
            'accent': '#f59e0b'
        }
        
        # Configuration des styles
        style.configure('Modern.TFrame', background=self.colors['background'])
        style.configure('Card.TFrame', background=self.colors['card_bg'], relief='flat', borderwidth=0)
        
        style.configure('Primary.TButton', 
                       background=self.colors['primary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 12, 'bold'))
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['primary_dark']),
                           ('pressed', self.colors['primary_dark'])])
        
        style.configure('Secondary.TButton',
                       background=self.colors['card_bg'],
                       foreground=self.colors['primary_light'],
                       borderwidth=1,
                       relief='solid',
                       font=('Segoe UI', 11))
        
        style.configure('Modern.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        
        style.configure('Title.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 24, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 14))
    
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
        
        # Table inscriptions (pour les plans sauvegardés)
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
        
        self.populate_sample_recipes()
        self.conn.commit()
    
    def populate_sample_recipes(self):
        """Remplit la base avec des recettes d'exemple modernes"""
        sample_recipes = [
            # Petit-déjeuners
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
            
            # Déjeuners
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
            
            # Dîners
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
        
        # Vérifier si la table est vide avant d'insérer
        self.cursor.execute('SELECT COUNT(*) FROM recipes')
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            for recipe in sample_recipes:
                self.cursor.execute('''
                    INSERT INTO recipes 
                    (name, category, ingredients, instructions, calories, prep_time, difficulty)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', recipe)
    
    def create_card(self, parent, title, subtitle, icon, color, command=None):
        """Crée une carte moderne"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief='flat', 
                       highlightbackground=self.colors['primary'], 
                       highlightthickness=1, bd=0)
        
        # Icône
        icon_label = tk.Label(card, text=icon, font=('Segoe UI', 24), 
                             bg=self.colors['card_bg'], fg=color)
        icon_label.pack(pady=(20, 10))
        
        # Titre
        title_label = tk.Label(card, text=title, font=('Segoe UI', 16, 'bold'), 
                              bg=self.colors['card_bg'], fg=self.colors['text_primary'])
        title_label.pack(pady=5)
        
        # Sous-titre
        subtitle_label = tk.Label(card, text=subtitle, font=('Segoe UI', 12), 
                                 bg=self.colors['card_bg'], fg=self.colors['text_secondary'],
                                 wraplength=200)
        subtitle_label.pack(pady=(0, 20))
        
        if command:
            card.bind('<Button-1>', lambda e: command())
            icon_label.bind('<Button-1>', lambda e: command())
            title_label.bind('<Button-1>', lambda e: command())
            subtitle_label.bind('<Button-1>', lambda e: command())
            card.configure(cursor='hand2')
            icon_label.configure(cursor='hand2')
            title_label.configure(cursor='hand2')
            subtitle_label.configure(cursor='hand2')
        
        return card
    
    def show_login_screen(self):
        """Affiche l'écran de connexion moderne"""
        self.clear_window()
        
        # Frame principal avec dégradé simulé
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True)
        
        # Container central
        container = tk.Frame(main_frame, bg=self.colors['background'])
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo et titre
        logo_label = tk.Label(container, text="🍽️", font=('Segoe UI', 48),
                             bg=self.colors['background'], fg=self.colors['primary'])
        logo_label.pack(pady=(0, 10))
        
        title_label = tk.Label(container, text="SmartMeal-Planner", 
                              font=('Segoe UI', 32, 'bold'), 
                              bg=self.colors['background'], fg=self.colors['text_primary'])
        title_label.pack(pady=(0, 5))
        
        subtitle_label = tk.Label(container, text="Repas sains & intelligents", 
                                 font=('Segoe UI', 16), 
                                 bg=self.colors['background'], fg=self.colors['text_secondary'])
        subtitle_label.pack(pady=(0, 50))
        
        # Cartes d'action
        actions_frame = tk.Frame(container, bg=self.colors['background'])
        actions_frame.pack(pady=20)
        
        # Carte Connexion
        login_card = self.create_card(
            actions_frame, "Se connecter", "Accédez à votre compte", "🔐", self.colors['primary_light'],
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
            actions_frame, "Mode Démo", "Essayez sans compte", "🎯", self.colors['primary'],
            self.demo_mode
        )
        demo_card.grid(row=0, column=2, padx=15, pady=10, sticky='nsew')
        
        # Footer
        footer_label = tk.Label(main_frame, text="🍎 Mangez mieux. Vivez mieux. 🏃‍♂️", 
                               font=('Segoe UI', 12), 
                               bg=self.colors['background'], fg=self.colors['text_secondary'])
        footer_label.pack(side='bottom', pady=20)
    
    def show_login_form(self):
        """Affiche le formulaire de connexion moderne"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True, padx=50, pady=50)
        
        # Retour
        back_btn = tk.Label(main_frame, text="← Retour", font=('Segoe UI', 12),
                           bg=self.colors['background'], fg=self.colors['primary_light'],
                           cursor='hand2')
        back_btn.bind('<Button-1>', lambda e: self.show_login_screen())
        back_btn.pack(anchor='nw')
        
        # Container formulaire
        form_container = tk.Frame(main_frame, bg=self.colors['background'])
        form_container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Titre
        tk.Label(form_container, text="🔐 Connexion", font=('Segoe UI', 28, 'bold'),
                bg=self.colors['background'], fg=self.colors['text_primary']).pack(pady=(0, 30))
        
        # Carte formulaire
        form_card = tk.Frame(form_container, bg=self.colors['card_bg'], relief='flat',
                            padx=40, pady=40)
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
        login_btn = ttk.Button(form_card, text="Se connecter", style='Primary.TButton',
                              command=self.login)
        login_btn.pack(pady=30, fill='x')
        
        # Lien inscription
        register_link = tk.Label(form_card, text="Pas de compte ? Créer un compte", 
                                font=('Segoe UI', 10), bg=self.colors['card_bg'], 
                                fg=self.colors['primary_light'], cursor='hand2')
        register_link.bind('<Button-1>', lambda e: self.show_register_form())
        register_link.pack()
    
    def show_register_form(self):
        """Affiche le formulaire d'inscription moderne"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True, padx=50, pady=50)
        
        # Retour
        back_btn = tk.Label(main_frame, text="← Retour", font=('Segoe UI', 12),
                           bg=self.colors['background'], fg=self.colors['primary_light'],
                           cursor='hand2')
        back_btn.bind('<Button-1>', lambda e: self.show_login_screen())
        back_btn.pack(anchor='nw')
        
        # Container formulaire
        form_container = tk.Frame(main_frame, bg=self.colors['background'])
        form_container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Titre
        tk.Label(form_container, text="🚀 Créer un compte", font=('Segoe UI', 28, 'bold'),
                bg=self.colors['background'], fg=self.colors['text_primary']).pack(pady=(0, 30))
        
        # Carte formulaire
        form_card = tk.Frame(form_container, bg=self.colors['card_bg'], relief='flat',
                            padx=40, pady=40)
        form_card.pack(pady=20)
        
        # Grille pour les champs
        form_grid = tk.Frame(form_card, bg=self.colors['card_bg'])
        form_grid.pack(fill='x')
        
        # Ligne 1 - Prénom et Nom
        tk.Label(form_grid, text="Prénom", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=0, column=0, sticky='w', pady=10)
        tk.Label(form_grid, text="Nom", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=0, column=1, sticky='w', pady=10, padx=(20,0))
        
        self.firstname_entry = ttk.Entry(form_grid, width=20, font=('Segoe UI', 12))
        self.firstname_entry.grid(row=1, column=0, sticky='w')
        
        self.lastname_entry = ttk.Entry(form_grid, width=20, font=('Segoe UI', 12))
        self.lastname_entry.grid(row=1, column=1, sticky='w', padx=(20,0))
        
        # Ligne 2 - Email
        tk.Label(form_grid, text="Email", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=2, column=0, sticky='w', pady=(20,5))
        self.reg_email_entry = ttk.Entry(form_grid, width=42, font=('Segoe UI', 12))
        self.reg_email_entry.grid(row=3, column=0, columnspan=2, sticky='we')
        
        # Ligne 3 - Mot de passe
        tk.Label(form_grid, text="Mot de passe", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=4, column=0, sticky='w', pady=(20,5))
        self.reg_password_entry = ttk.Entry(form_grid, width=42, show='•', font=('Segoe UI', 12))
        self.reg_password_entry.grid(row=5, column=0, columnspan=2, sticky='we')
        
        # Ligne 4 - Taille et Poids
        tk.Label(form_grid, text="Taille (cm)", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=6, column=0, sticky='w', pady=(20,5))
        tk.Label(form_grid, text="Poids (kg)", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=6, column=1, sticky='w', pady=(20,5), padx=(20,0))
        
        self.height_entry = ttk.Entry(form_grid, width=20, font=('Segoe UI', 12))
        self.height_entry.grid(row=7, column=0, sticky='w')
        
        self.weight_entry = ttk.Entry(form_grid, width=20, font=('Segoe UI', 12))
        self.weight_entry.grid(row=7, column=1, sticky='w', padx=(20,0))
        
        # Bouton inscription
        register_btn = ttk.Button(form_card, text="Créer mon compte", style='Primary.TButton',
                                 command=self.register)
        register_btn.pack(pady=30, fill='x')
        
        # Lien connexion
        login_link = tk.Label(form_card, text="Déjà un compte ? Se connecter", 
                             font=('Segoe UI', 10), bg=self.colors['card_bg'], 
                             fg=self.colors['primary_light'], cursor='hand2')
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
        """Affiche le tableau de bord moderne"""
        self.clear_window()
        
        # Barre latérale
        sidebar = tk.Frame(self.root, bg=self.colors['card_bg'], width=250)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Logo sidebar
        tk.Label(sidebar, text="🍽️", font=('Segoe UI', 24),
                bg=self.colors['card_bg'], fg=self.colors['primary']).pack(pady=(30, 10))
        
        tk.Label(sidebar, text="SmartMeal", font=('Segoe UI', 16, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(pady=(0, 30))
        
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
        main_content.pack(side='right', fill='both', expand=True, padx=20, pady=20)
        
        # En-tête
        header = tk.Frame(main_content, bg=self.colors['background'])
        header.pack(fill='x', pady=(0, 30))
        
        tk.Label(header, text=f"👋 Bonjour, {self.current_user['firstname']} !", 
                font=('Segoe UI', 24, 'bold'), bg=self.colors['background'], 
                fg=self.colors['text_primary']).pack(side='left')
        
        # Cartes de statistiques
        stats_frame = tk.Frame(main_content, bg=self.colors['background'])
        stats_frame.pack(fill='x', pady=(0, 30))
        
        # Compter le nombre d'inscriptions de l'utilisateur
        self.cursor.execute('SELECT COUNT(*) FROM saved_plans WHERE user_id = ?', 
                          (self.current_user['id'],))
        plan_count = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM recipes')
        recipe_count = self.cursor.fetchone()[0]
        
        stats_cards = [
            ("📅", str(plan_count), "Plans sauvegardés", "#10b981"),
            ("🍽️", str(recipe_count), "Recettes disponibles", "#f59e0b"),
            ("🔥", "45", "Jours suivis", "#ef4444"),
            ("🎯", "85%", "Objectif atteint", "#8b5cf6")
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
        
        # Récupérer les 3 derniers plans sauvegardés
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
    
    def show_saved_plans(self):
        """Affiche les plans sauvegardés (inscriptions)"""
        self.clear_window()
        
        # Barre latérale
        sidebar = tk.Frame(self.root, bg=self.colors['card_bg'], width=250)
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
        main_content.pack(side='right', fill='both', expand=True, padx=20, pady=20)
        
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
                                     bg='#ef4444', fg='white',
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
            
            # Fenêtre popup
            popup = tk.Toplevel(self.root)
            popup.title("📋 Plan sauvegardé")
            popup.geometry("800x600")
            popup.configure(bg=self.colors['background'])
            
            # Zone de texte
            text_widget = scrolledtext.ScrolledText(popup, font=('Consolas', 11),
                                                   bg=self.colors['card_bg'], fg=self.colors['text_primary'],
                                                   insertbackground='white')
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
    
    def create_stats_card(self, parent, icon, value, text, color):
        """Crée une carte de statistiques"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief='flat', padx=20, pady=20)
        
        tk.Label(card, text=icon, font=('Segoe UI', 20), bg=self.colors['card_bg'], fg=color).pack(anchor='w')
        tk.Label(card, text=value, font=('Segoe UI', 24, 'bold'), bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(anchor='w')
        tk.Label(card, text=text, font=('Segoe UI', 12), bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack(anchor='w')
        
        return card
    
    def create_plan_card(self, parent, title, details, status):
        """Crée une carte de plan"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief='flat', padx=20, pady=15)
        
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
    
    def show_meal_generator(self):
        """Affiche le générateur de repas"""
        self.clear_window()
        
        # Barre latérale (réutilisée)
        sidebar = tk.Frame(self.root, bg=self.colors['card_bg'], width=250)
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
        main_content.pack(side='right', fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(main_content, text="🍽️ Générateur de Repas", 
                font=('Segoe UI', 28, 'bold'), bg=self.colors['background'], 
                fg=self.colors['text_primary']).pack(pady=(0, 30))
        
        # Carte paramètres
        settings_card = tk.Frame(main_content, bg=self.colors['card_bg'], padx=30, pady=30)
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
        plan_name_entry = ttk.Entry(settings_grid, textvariable=self.plan_name_var, width=20, font=('Segoe UI', 12))
        plan_name_entry.grid(row=0, column=1, padx=20, pady=10)
        
        # Calories cible
        tk.Label(settings_grid, text="Calories cible par jour:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=0, column=2, sticky='w', pady=10)
        
        self.calories_var = tk.StringVar(value="2000")
        calories_entry = ttk.Entry(settings_grid, textvariable=self.calories_var, width=15, font=('Segoe UI', 12))
        calories_entry.grid(row=0, column=3, padx=20, pady=10)
        
        # Nombre de jours
        tk.Label(settings_grid, text="Nombre de jours:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=1, column=0, sticky='w', pady=10)
        
        self.days_var = tk.StringVar(value="7")
        days_entry = ttk.Entry(settings_grid, textvariable=self.days_var, width=15, font=('Segoe UI', 12))
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
        generate_btn = ttk.Button(button_frame, text="🎯 Générer le plan", style='Primary.TButton',
                                 command=self.generate_meal_plan)
        generate_btn.pack(side='left', padx=5)
        
        # Bouton sauvegarde
        save_btn = ttk.Button(button_frame, text="💾 Sauvegarder le plan", style='Secondary.TButton',
                             command=self.save_generated_plan)
        save_btn.pack(side='left', padx=5)
        
        # Zone résultats
        self.results_text = scrolledtext.ScrolledText(main_content, height=20, font=('Consolas', 11),
                                                     bg=self.colors['card_bg'], fg=self.colors['text_primary'],
                                                     insertbackground='white')
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
        """Génère un plan alimentaire avec style"""
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
        """Sauvegarde le plan généré dans la base de données"""
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
        self.clear_window()
        
        # Barre latérale
        sidebar = tk.Frame(self.root, bg=self.colors['card_bg'], width=250)
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
        main_content.pack(side='right', fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(main_content, text="🔍 Recherche de Recettes", 
                font=('Segoe UI', 28, 'bold'), bg=self.colors['background'], 
                fg=self.colors['text_primary']).pack(pady=(0, 30))
        
        # Carte recherche
        search_card = tk.Frame(main_content, bg=self.colors['card_bg'], padx=30, pady=30)
        search_card.pack(fill='x', pady=(0, 20))
        
        tk.Label(search_card, text="🔎 Critères de recherche", font=('Segoe UI', 18, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 20))
        
        # Grille critères
        criteria_grid = tk.Frame(search_card, bg=self.colors['card_bg'])
        criteria_grid.pack(fill='x')
        
        # Catégorie
        tk.Label(criteria_grid, text="Catégorie:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=0, column=0, sticky='w', pady=10)
        
        self.search_category_var = tk.StringVar(value="Toutes")
        category_combo = ttk.Combobox(criteria_grid, textvariable=self.search_category_var, 
                                     values=["Toutes", "Petit-déjeuner", "Déjeuner", "Dîner"], 
                                     width=20, font=('Segoe UI', 12))
        category_combo.grid(row=0, column=1, padx=20, pady=10)
        
        # Difficulté
        tk.Label(criteria_grid, text="Difficulté:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=0, column=2, sticky='w', pady=10)
        
        self.search_difficulty_var = tk.StringVar(value="Toutes")
        difficulty_combo = ttk.Combobox(criteria_grid, textvariable=self.search_difficulty_var, 
                                       values=["Toutes", "Facile", "Moyen"], 
                                       width=15, font=('Segoe UI', 12))
        difficulty_combo.grid(row=0, column=3, padx=20, pady=10)
        
        # Calories max
        tk.Label(criteria_grid, text="Calories max:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=1, column=0, sticky='w', pady=10)
        
        self.search_calories_var = tk.StringVar(value="500")
        calories_entry = ttk.Entry(criteria_grid, textvariable=self.search_calories_var, width=15, font=('Segoe UI', 12))
        calories_entry.grid(row=1, column=1, padx=20, pady=10)
        
        # Temps max
        tk.Label(criteria_grid, text="Temps max (min):", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=1, column=2, sticky='w', pady=10)
        
        self.search_time_var = tk.StringVar(value="60")
        time_entry = ttk.Entry(criteria_grid, textvariable=self.search_time_var, width=15, font=('Segoe UI', 12))
        time_entry.grid(row=1, column=3, padx=20, pady=10)
        
        # Recherche texte
        tk.Label(criteria_grid, text="Mot-clé:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).grid(row=2, column=0, sticky='w', pady=10)
        
        self.search_keyword_var = tk.StringVar()
        keyword_entry = ttk.Entry(criteria_grid, textvariable=self.search_keyword_var, width=20, font=('Segoe UI', 12))
        keyword_entry.grid(row=2, column=1, padx=20, pady=10, columnspan=3, sticky='we')
        
        # Bouton recherche
        search_btn = ttk.Button(search_card, text="🔍 Rechercher", style='Primary.TButton',
                               command=self.perform_recipe_search)
        search_btn.pack(pady=20)
        
        # Zone résultats
        self.search_results_text = scrolledtext.ScrolledText(main_content, height=20, font=('Consolas', 11),
                                                           bg=self.colors['card_bg'], fg=self.colors['text_primary'],
                                                           insertbackground='white')
        self.search_results_text.pack(fill='both', expand=True, pady=10)
    
    def perform_recipe_search(self):
        """Effectue la recherche de recettes"""
        try:
            # Construire la requête SQL
            query = "SELECT * FROM recipes WHERE 1=1"
            params = []
            
            # Catégorie
            category = self.search_category_var.get()
            if category != "Toutes":
                query += " AND category = ?"
                params.append(category)
            
            # Difficulté
            difficulty = self.search_difficulty_var.get()
            if difficulty != "Toutes":
                query += " AND difficulty = ?"
                params.append(difficulty)
            
            # Calories max
            if self.search_calories_var.get():
                query += " AND calories <= ?"
                params.append(int(self.search_calories_var.get()))
            
            # Temps max
            if self.search_time_var.get():
                query += " AND prep_time <= ?"
                params.append(int(self.search_time_var.get()))
            
            # Mot-clé
            keyword = self.search_keyword_var.get()
            if keyword:
                query += " AND (name LIKE ? OR ingredients LIKE ?)"
                params.append(f"%{keyword}%")
                params.append(f"%{keyword}%")
            
            # Exécuter la requête
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            # Afficher les résultats
            self.display_search_results(results)
            
        except ValueError:
            messagebox.showerror("Erreur", "🔢 Veuillez entrer des nombres valides")
    
    def display_search_results(self, results):
        """Affiche les résultats de recherche"""
        if not results:
            results_text = "❌ Aucune recette ne correspond à vos critères de recherche.\n"
            results_text += "   Essayez de modifier vos filtres."
        else:
            results_text = f"✅ {len(results)} recette(s) trouvée(s):\n"
            results_text += "═" * 60 + "\n\n"
            
            for i, recipe in enumerate(results, 1):
                results_text += f"📋 RECETTE #{i}\n"
                results_text += f"🍽️  Nom: {recipe[1]}\n"
                results_text += f"📂 Catégorie: {recipe[2]}\n"
                results_text += f"🔥 Calories: {recipe[5]}\n"
                results_text += f"⏱️  Temps: {recipe[6]} min\n"
                results_text += f"🎯 Difficulté: {recipe[7]}\n"
                results_text += f"🥕 Ingrédients: {recipe[3][:100]}...\n"
                results_text += "─" * 40 + "\n\n"
        
        self.search_results_text.delete(1.0, tk.END)
        self.search_results_text.insert(1.0, results_text)
    
    def show_recipes(self):
        """Affiche toutes les recettes avec fonctionnalité de recherche"""
        self.show_recipe_search()
    
    def show_profile(self):
        """Affiche la page profil"""
        messagebox.showinfo("Info", "👤 Page profil - Fonctionnalité à venir!")
    
    def clear_window(self):
        """Vide la fenêtre"""
        for widget in self.root.winfo_children():
            widget.destroy()

def main():
    try:
        root = tk.Tk()
        app = ModernSmartMealPlanner(root)
        root.mainloop()
    except Exception as e:
        print(f"Erreur: {e}")
        input("Appuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()