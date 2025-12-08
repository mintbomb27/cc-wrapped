import os
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

MODEL_PATH = "model.pkl"

class TransactionCategorizer:
    def __init__(self):
        self.categories = [
            "Food & Drink", "Shopping", "Travel", "Groceries", "Bills", "Health", "Other"
        ]
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
            except:
                self.train_initial_model()
        else:
            self.train_initial_model()

    def train_initial_model(self):
        # Initial training data with Indian context
        data = [
            # Travel
            ("Uber", "Travel"),
            ("Lyft", "Travel"),
            ("Ola", "Travel"),
            ("Rapido", "Travel"),
            ("ZOOMCAR", "Travel"),
            ("Delta", "Travel"),
            ("IndiGo", "Travel"),
            ("SpiceJet", "Travel"),
            ("IRCTC", "Travel"),
            
            # Food & Drink
            ("Starbucks", "Food & Drink"),
            ("McDonalds", "Food & Drink"),
            ("Swiggy", "Food & Drink"),
            ("Zomato", "Food & Drink"),
            ("Dominos", "Food & Drink"),
            ("KFC", "Food & Drink"),
            ("Cafe Coffee Day", "Food & Drink"),
            
            # Groceries
            ("Walmart", "Groceries"),
            ("BigBasket", "Groceries"),
            ("Grofers", "Groceries"),
            ("Blinkit", "Groceries"),
            ("Zepto", "Groceries"),
            ("Kroger", "Groceries"),
            ("Whole Foods", "Groceries"),
            ("DMart", "Groceries"),
            ("Reliance Fresh", "Groceries"),
            ("More Supermarket", "Groceries"),
            ("Adambakkam Cooperativ", "Groceries"),
            
            # Shopping
            ("Target", "Shopping"),
            ("Amazon", "Shopping"),
            ("Flipkart", "Shopping"),
            ("Myntra", "Shopping"),
            ("Ajio", "Shopping"),
            ("Nykaa", "Shopping"),
            
            # Bills
            ("Netflix", "Bills"),
            ("Spotify", "Bills"),
            ("Amazon Prime", "Bills"),
            ("Hotstar", "Bills"),
            ("Airtel", "Bills"),
            ("Jio", "Bills"),
            
            # Health
            ("CVS", "Health"),
            ("Apollo Pharmacy", "Health"),
            ("Medlife", "Health"),
            ("PharmEasy", "Health"),
            
            # Other
            ("ATM", "Other"),
            ("CATAM", "Other"),
        ]
        X, y = zip(*data)
        self.model = make_pipeline(CountVectorizer(), MultinomialNB())
        self.model.fit(X, y)
        self.save_model()

    def save_model(self):
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.model, f)

    def predict(self, description: str) -> str:
        if not self.model:
            return "Uncategorized"
        try:
            return self.model.predict([description])[0]
        except:
            return "Uncategorized"

    def train(self, descriptions: list, categories: list):
        # Retrain model with new data AND old data?
        # For simplicity, we just partial_fit if supported or just re-fit everything if we had a DB of labeled data.
        # Since we don't have a DB of global labeled data comfortably loaded here, 
        # we will use the current model to predict, accept feedback, and ideally re-train.
        # But MultinomialNB supports partial_fit if we expose the vectorizer.
        # Implementation Plan: Simple wrapper.
        # For now, let's just re-fit if we passed enough data, or assume this is a placeholder for more complex logic.
        # We will implement a simple update using partial_fit is tricky with Pipeline.
        # Let's just create a new pipeline and fit on new data combined with some base data?
        # Or just append to a local CSV/DB of training data and retrain?
        
        # Sticking to valid logic: 
        # 1. Load existing training data (transaction history from DB).
        # 2. Add new feedback.
        # 3. Retrain.
        pass

categorizer = TransactionCategorizer()
