import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import sqlite3
import json
import random
from datetime import datetime, timedelta

class SmartMealPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartMeal-Planner - Repas sains & intelligents")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0fdf4')
        
        # Style moderne
        self.style = ttk.Style()
        self.style.configure('Green.TButton', background='#10b981', foreground='white', font=('Arial', 12, 'bold'))
        self.style.configure('Green.TFrame', background='#f0fdf4')
        
        self.current_user = None
        self.setup_database()
        self.show_login_screen()
    
    def setup_database(self):
        """Initialise la base de données"""
        self.conn = sqlite3.connect('meal_planner.db')
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
                activity_level TEXT,
                goals TEXT,
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
        
        # Table plans alimentaires
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS meal_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                breakfast TEXT,
                lunch TEXT,
                dinner TEXT,
                snacks TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        self.populate_sample_recipes()
        self.conn.commit()
    
    def populate_sample_recipes(self):
        """Remplit la base avec des recettes d'exemple"""
        sample_recipes = [
            {
                'name': 'Omelette aux légumes',
                'category': 'Petit-déjeuner',
                'ingredients': '2 œufs, 50g épinards, 30g champignons, 20g fromage, 1 c.à.s huile olive',
                'instructions': 'Battre les œufs, faire revenir les légumes, ajouter les œufs, cuire 5 min',
                'calories': 280,
                'prep_time': 15,
                'difficulty': 'Facile'
            },
            {
                'name': 'Salade de quinoa',
                'category': 'Déjeuner',
                'ingredients': '100g quinoa, 1 avocat, 100g tomates, 50g concombre, jus citron',
                'instructions': 'Cuire le quinoa, couper les légumes, mélanger avec assaisonnement',
                'calories': 350,
                'prep_time': 20,
                'difficulty': 'Facile'
            },
            {
                'name': 'Saumon et légumes rôtis',
                'category': 'Dîner',
                'ingredients': '150g saumon, 200g brocoli, 100g carottes, ail, herbes',
                'instructions': 'Assaisonner le saumon, rôtir les légumes 25 min à 200°C',
                'calories': 420,
                'prep_time': 30,
                'difficulty': 'Moyen'
            }
        ]
        
        for recipe in sample_recipes:
            self.cursor.execute('''
                INSERT OR IGNORE INTO recipes (name, category, ingredients, instructions, calories, prep_time, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (recipe['name'], recipe['category'], recipe['ingredients'], 
                  recipe['instructions'], recipe['calories'], recipe['prep_time'], recipe['difficulty']))
    
    def show_login_screen(self):
        """Affiche l'écran de connexion/inscription"""
        self.clear_window()
        
        # Frame principal
        main_frame = ttk.Frame(self.root, style='Green.TFrame')
        main_frame.pack(fill='both', expand=True, padx=50, pady=50)
        
        # Titre
        title_label = tk.Label(main_frame, text="SmartMeal-Planner", 
                              font=('Arial', 28, 'bold'), fg='#059669', bg='#f0fdf4')
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(main_frame, text="Repas sains & intelligents", 
                                 font=('Arial', 16), fg='#047857', bg='#f0fdf4')
        subtitle_label.pack(pady=10)
        
        # Frame des boutons
        button_frame = ttk.Frame(main_frame, style='Green.TFrame')
        button_frame.pack(pady=50)
        
        # Bouton Connexion
        login_btn = ttk.Button(button_frame, text="Se connecter", 
                              style='Green.TButton', command=self.show_login_form)
        login_btn.pack(pady=15, ipadx=30, ipady=10)
        
        # Bouton Inscription
        register_btn = ttk.Button(button_frame, text="Créer un compte", 
                                 style='Green.TButton', command=self.show_register_form)
        register_btn.pack(pady=15, ipadx=30, ipady=10)
        
        # Bouton Mode Démo
        demo_btn = ttk.Button(button_frame, text="Essayer en mode démo", 
                             command=self.demo_mode)
        demo_btn.pack(pady=15, ipadx=30, ipady=10)
    
    def show_login_form(self):
        """Affiche le formulaire de connexion"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, style='Green.TFrame')
        main_frame.pack(fill='both', expand=True, padx=100, pady=50)
        
        # Titre
        tk.Label(main_frame, text="Connexion", font=('Arial', 24, 'bold'), 
                fg='#059669', bg='#f0fdf4').pack(pady=20)
        
        # Formulaire
        form_frame = ttk.Frame(main_frame, style='Green.TFrame')
        form_frame.pack(pady=30)
        
        tk.Label(form_frame, text="Email:", bg='#f0fdf4').grid(row=0, column=0, sticky='w', pady=10)
        email_entry = ttk.Entry(form_frame, width=30, font=('Arial', 12))
        email_entry.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(form_frame, text="Mot de passe:", bg='#f0fdf4').grid(row=1, column=0, sticky='w', pady=10)
        password_entry = ttk.Entry(form_frame, width=30, show='*', font=('Arial', 12))
        password_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Boutons
        btn_frame = ttk.Frame(main_frame, style='Green.TFrame')
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Se connecter", style='Green.TButton',
                  command=lambda: self.login(email_entry.get(), password_entry.get())).pack(side='left', padx=10)
        
        ttk.Button(btn_frame, text="Retour", 
                  command=self.show_login_screen).pack(side='left', padx=10)
    
    def show_register_form(self):
        """Affiche le formulaire d'inscription"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, style='Green.TFrame')
        main_frame.pack(fill='both', expand=True, padx=50, pady=30)
        
        tk.Label(main_frame, text="Créer un compte", font=('Arial', 24, 'bold'), 
                fg='#059669', bg='#f0fdf4').pack(pady=20)
        
        # Formulaire en grille
        form_frame = ttk.Frame(main_frame, style='Green.TFrame')
        form_frame.pack(pady=20)
        
        # Ligne 1 - Prénom et Nom
        tk.Label(form_frame, text="Prénom:", bg='#f0fdf4').grid(row=0, column=0, sticky='w', pady=5)
        firstname_entry = ttk.Entry(form_frame, width=20, font=('Arial', 12))
        firstname_entry.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(form_frame, text="Nom:", bg='#f0fdf4').grid(row=0, column=2, sticky='w', pady=5, padx=(20,0))
        lastname_entry = ttk.Entry(form_frame, width=20, font=('Arial', 12))
        lastname_entry.grid(row=0, column=3, pady=5, padx=5)
        
        # Ligne 2 - Email
        tk.Label(form_frame, text="Email:", bg='#f0fdf4').grid(row=1, column=0, sticky='w', pady=5)
        email_entry = ttk.Entry(form_frame, width=50, font=('Arial', 12))
        email_entry.grid(row=1, column=1, columnspan=3, pady=5, padx=5, sticky='we')
        
        # Ligne 3 - Mot de passe
        tk.Label(form_frame, text="Mot de passe:", bg='#f0fdf4').grid(row=2, column=0, sticky='w', pady=5)
        password_entry = ttk.Entry(form_frame, width=50, show='*', font=('Arial', 12))
        password_entry.grid(row=2, column=1, columnspan=3, pady=5, padx=5, sticky='we')
        
        # Ligne 4 - Taille et Poids
        tk.Label(form_frame, text="Taille (cm):", bg='#f0fdf4').grid(row=3, column=0, sticky='w', pady=5)
        height_entry = ttk.Entry(form_frame, width=20, font=('Arial', 12))
        height_entry.grid(row=3, column=1, pady=5, padx=5)
        
        tk.Label(form_frame, text="Poids (kg):", bg='#f0fdf4').grid(row=3, column=2, sticky='w', pady=5, padx=(20,0))
        weight_entry = ttk.Entry(form_frame, width=20, font=('Arial', 12))
        weight_entry.grid(row=3, column=3, pady=5, padx=5)
        
        # Boutons
        btn_frame = ttk.Frame(main_frame, style='Green.TFrame')
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Créer le compte", style='Green.TButton',
                  command=lambda: self.register(
                      firstname_entry.get(), lastname_entry.get(), email_entry.get(),
                      password_entry.get(), height_entry.get(), weight_entry.get()
                  )).pack(side='left', padx=10)
        
        ttk.Button(btn_frame, text="Retour", 
                  command=self.show_login_screen).pack(side='left', padx=10)
    
    def login(self, email, password):
        """Gère la connexion"""
        if not email or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        self.cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = self.cursor.fetchone()
        
        if user and user[4] == password:  # En production, utiliser hashlib
            self.current_user = {
                'id': user[0],
                'firstname': user[1],
                'lastname': user[2],
                'email': user[3],
                'height': user[5],
                'weight': user[6]
            }
            self.show_dashboard()
        else:
            messagebox.showerror("Erreur", "Email ou mot de passe incorrect")
    
    def register(self, firstname, lastname, email, password, height, weight):
        """Gère l'inscription"""
        if not all([firstname, lastname, email, password, height, weight]):
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO users (firstname, lastname, email, password, height, weight)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (firstname, lastname, email, password, int(height), float(weight)))
            self.conn.commit()
            
            messagebox.showinfo("Succès", "Compte créé avec succès !")
            self.show_login_screen()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Cet email est déjà utilisé")
        except ValueError:
            messagebox.showerror("Erreur", "Taille et poids doivent être des nombres")
    
    def demo_mode(self):
        """Mode démo sans connexion"""
        self.current_user = {'firstname': 'Utilisateur', 'id': 0}
        self.show_dashboard()
    
    def show_dashboard(self):
        """Affiche le tableau de bord principal"""
        self.clear_window()
        
        # Barre de navigation
        nav_frame = ttk.Frame(self.root, style='Green.TFrame')
        nav_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(nav_frame, text=f"Bonjour, {self.current_user['firstname']} !", 
                font=('Arial', 16, 'bold'), fg='#059669', bg='#f0fdf4').pack(side='left')
        
        ttk.Button(nav_frame, text="Déconnexion", 
                  command=self.show_login_screen).pack(side='right')
        
        # Contenu principal
        main_frame = ttk.Frame(self.root, style='Green.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Onglets
        notebook = ttk.Notebook(main_frame)
        
        # Onglet 1: Génération de repas
        meal_frame = ttk.Frame(notebook)
        self.setup_meal_generation(meal_frame)
        notebook.add(meal_frame, text="🍽️ Générer des repas")
        
        # Onglet 2: Mes plans
        plans_frame = ttk.Frame(notebook)
        self.setup_meal_plans(plans_frame)
        notebook.add(plans_frame, text="📅 Mes plans")
        
        # Onglet 3: Recettes
        recipes_frame = ttk.Frame(notebook)
        self.setup_recipes(recipes_frame)
        notebook.add(recipes_frame, text="📖 Recettes")
        
        # Onglet 4: Profil
        profile_frame = ttk.Frame(notebook)
        self.setup_profile(profile_frame)
        notebook.add(profile_frame, text="👤 Profil")
        
        notebook.pack(fill='both', expand=True)
    
    def setup_meal_generation(self, parent):
        """Configure l'onglet de génération de repas"""
        # Paramètres
        settings_frame = ttk.LabelFrame(parent, text="Paramètres", padding=10)
        settings_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(settings_frame, text="Calories cible:").grid(row=0, column=0, sticky='w')
        calories_var = tk.StringVar(value="2000")
        ttk.Entry(settings_frame, textvariable=calories_var, width=10).grid(row=0, column=1, padx=5)
        
        tk.Label(settings_frame, text="Nombre de jours:").grid(row=0, column=2, sticky='w', padx=(20,0))
        days_var = tk.StringVar(value="7")
        ttk.Entry(settings_frame, textvariable=days_var, width=10).grid(row=0, column=3, padx=5)
        
        # Bouton génération
        ttk.Button(settings_frame, text="Générer le plan", style='Green.TButton',
                  command=lambda: self.generate_meal_plan(int(days_var.get()), int(calories_var.get()))).grid(row=1, column=0, columnspan=4, pady=10)
        
        # Résultats
        self.results_text = scrolledtext.ScrolledText(parent, height=20, font=('Arial', 11))
        self.results_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def generate_meal_plan(self, days, target_calories):
        """Génère un plan alimentaire"""
        self.cursor.execute('SELECT * FROM recipes')
        all_recipes = self.cursor.fetchall()
        
        if not all_recipes:
            messagebox.showwarning("Attention", "Aucune recette disponible")
            return
        
        plan_text = f"📋 PLAN ALIMENTAIRE - {days} JOURS\n"
        plan_text += f"🎯 Calories cible par jour: {target_calories}\n"
        plan_text += "="*50 + "\n\n"
        
        categories = {
            'Petit-déjeuner': [r for r in all_recipes if r[2] == 'Petit-déjeuner'],
            'Déjeuner': [r for r in all_recipes if r[2] == 'Déjeuner'],
            'Dîner': [r for r in all_recipes if r[2] == 'Dîner']
        }
        
        for day in range(1, days + 1):
            plan_text += f"\n📅 JOUR {day}:\n"
            daily_calories = 0
            
            for meal_type in ['Petit-déjeuner', 'Déjeuner', 'Dîner']:
                available = categories[meal_type]
                if available:
                    recipe = random.choice(available)
                    plan_text += f"\n{meal_type}:\n"
                    plan_text += f"  🍽️ {recipe[1]}\n"
                    plan_text += f"  ⏱️ {recipe[6]} min | 🔥 {recipe[5]} cal\n"
                    plan_text += f"  📝 {recipe[3]}\n"
                    daily_calories += recipe[5]
            
            plan_text += f"\n🔥 Total calories: {daily_calories}\n"
            plan_text += "-"*40 + "\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, plan_text)
        
        # Sauvegarder le plan
        if messagebox.askyesno("Sauvegarder", "Voulez-vous sauvegarder ce plan ?"):
            self.save_meal_plan(plan_text)
    
    def save_meal_plan(self, plan_text):
        """Sauvegarde le plan alimentaire"""
        filename = f"meal_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(plan_text)
        messagebox.showinfo("Succès", f"Plan sauvegardé sous: {filename}")
    
    def setup_meal_plans(self, parent):
        """Configure l'onglet des plans alimentaires"""
        tk.Label(parent, text="Vos plans alimentaires sauvegardés", 
                font=('Arial', 16, 'bold'), fg='#059669', bg='#f0fdf4').pack(pady=10)
        
        # Liste des plans (simplifiée)
        plans_list = tk.Listbox(parent, height=15, font=('Arial', 12))
        plans_list.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Ajouter quelques plans d'exemple
        plans_list.insert(tk.END, "📋 Plan équilibré - 7 jours (15 Nov 2024)")
        plans_list.insert(tk.END, "📋 Plan perte de poids - 5 jours (10 Nov 2024)")
        plans_list.insert(tk.END, "📋 Plan énergie - 3 jours (8 Nov 2024)")
    
    def setup_recipes(self, parent):
        """Configure l'onglet des recettes"""
        # Barre de recherche
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(search_frame, text="Rechercher:").pack(side='left')
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side='left', padx=5)
        ttk.Button(search_frame, text="🔍", command=lambda: self.search_recipes(search_entry.get())).pack(side='left')
        
        # Liste des recettes
        self.recipes_list = tk.Listbox(parent, height=15, font=('Arial', 12))
        self.recipes_list.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Charger les recettes
        self.load_recipes()
    
    def load_recipes(self):
        """Charge toutes les recettes"""
        self.cursor.execute('SELECT name, category, calories, prep_time FROM recipes')
        recipes = self.cursor.fetchall()
        
        self.recipes_list.delete(0, tk.END)
        for recipe in recipes:
            self.recipes_list.insert(tk.END, f"🍽️ {recipe[0]} | {recipe[1]} | {recipe[2]} cal | {recipe[3]} min")
    
    def search_recipes(self, query):
        """Recherche des recettes"""
        if not query:
            self.load_recipes()
            return
        
        self.cursor.execute('''
            SELECT name, category, calories, prep_time FROM recipes 
            WHERE name LIKE ? OR category LIKE ? OR ingredients LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        recipes = self.cursor.fetchall()
        self.recipes_list.delete(0, tk.END)
        
        for recipe in recipes:
            self.recipes_list.insert(tk.END, f"🍽️ {recipe[0]} | {recipe[1]} | {recipe[2]} cal | {recipe[3]} min")
    
    def setup_profile(self, parent):
        """Configure l'onglet profil"""
        if not self.current_user or self.current_user['id'] == 0:
            tk.Label(parent, text="Mode démo - Profil non disponible", 
                    font=('Arial', 14), fg='#666', bg='#f0fdf4').pack(pady=50)
            return
        
        # Informations utilisateur
        info_frame = ttk.LabelFrame(parent, text="Vos informations", padding=20)
        info_frame.pack(fill='x', padx=20, pady=20)
        
        user_info = f"""
        👤 Nom: {self.current_user['firstname']} {self.current_user['lastname']}
        📧 Email: {self.current_user['email']}
        📏 Taille: {self.current_user['height']} cm
        ⚖️ Poids: {self.current_user['weight']} kg
        """
        
        tk.Label(info_frame, text=user_info, font=('Arial', 12), 
                justify='left', bg='#f0fdf4').pack()
        
        # Statistiques
        stats_frame = ttk.LabelFrame(parent, text="Statistiques", padding=20)
        stats_frame.pack(fill='x', padx=20, pady=20)
        
        stats_text = """
        📊 Plans générés: 12
        🍽️ Recettes essayées: 8
        📅 Jours suivis: 45
        🎯 Objectif: En cours...
        """
        
        tk.Label(stats_frame, text=stats_text, font=('Arial', 12), 
                justify='left', bg='#f0fdf4').pack()
    
    def clear_window(self):
        """Vide la fenêtre"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def __del__(self):
        """Fermeture de la base de données"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    root = tk.Tk()
    app = SmartMealPlanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()