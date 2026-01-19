import re 

class AnalyzerService:
    def __init__(self):
        # Inclues articles, prepositions, conjunctions, pronouns and auxiliary verbs
        self.STOPWORDS_ES = {
            # articles, prepositions
            "a", "al", "ante", "bajo", "con", "contra", "de", "del", "desde", "durante", 
            "en", "entre", "hacia", "hasta", "mediante", "para", "por", "segun", "según", 
            "sin", "sobre", "tras", "versus", "via", "vía", "el", "la", "lo", "los", "las", 
            "un", "una", "unos", "unas",
            
            # Conjunctions and connectors
            "y", "e", "ni", "o", "u", "pero", "mas", "más", "sino", "aunque", "porque", 
            "pues", "entonces", "luego", "asi", "así", "siquiera", "si", "sí", "ya", "que", "qué",
            
            # Pronouns and determiners
            "yo", "tu", "tú", "el", "él", "ella", "ello", "ellas", "ellos", "nosotros", 
            "nosotras", "vosotros", "vosotras", "usted", "ustedes", "me", "te", "se", 
            "nos", "os", "mi", "mí", "mis", "tu", "tú", "tus", "su", "sus", "mío", "mia", 
            "mía", "míos", "mias", "mías", "tuyo", "tuya", "tuyos", "tuyas", "suyo", "suya", 
            "suyos", "suyas", "nuestro", "nuestra", "nuestros", "nuestras", "vuestro", 
            "vuestra", "vuestros", "vuestras", "este", "esta", "esto", "estos", "estas", 
            "ese", "esa", "eso", "esos", "esas", "aquel", "aquella", "aquello", "aquellos", 
            "aquellas", "quien", "quién", "quienes", "quiénes", "cual", "cuál", "cuales", 
            "cuáles", "cuanto", "cuánto", "cuanta", "cuánta", "cuantos", "cuántos", 
            "cuantas", "cuántas", "algo", "nada", "alguno", "alguna", "algunos", "algunas", 
            "ninguno", "ninguna", "ningunos", "ningunas", "otro", "otra", "otros", "otras", 
            "todo", "toda", "todos", "todas", "poco", "poca", "pocos", "pocas", "mucho", 
            "mucha", "muchos", "muchas", "demasiado", "demasiada", "demasiados", "demasiadas",
            
            # Common adverbs (without semantic weight of content)
            "aqui", "aquí", "aca", "acá", "ahi", "ahí", "alli", "allí", "alla", "allá", 
            "cerca", "lejos", "antes", "despues", "después", "ayer", "hoy", "mañana", 
            "siempre", "nunca", "jamas", "jamás", "quizas", "quizás", "tal", "bien", "mal", 
            "muy", "tan", "demasiado", "solo", "sólo",
            
            # Auxiliary Verbs (Ser, Estar, Haber - Common Conjugations)
            "ser", "soy", "eres", "es", "somos", "sois", "son", "fui", "fuiste", "fue", 
            "fuimos", "fuisteis", "fueron", "era", "eras", "eramos", "éramos", "erais", "eran",
            "estoy", "estas", "estás", "esta", "está", "estamos", "estais", "estáis", "estan", "están",
            "estaba", "estabas", "estabamos", "estábamos", "estabais", "estaban", "estado",
            "haber", "he", "has", "ha", "hay", "hemos", "habeis", "habéis", "han", "habia", 
            "había", "habias", "habías", "habia", "había", "habíamos", "habiais", "habian", "habían",
            "hacer", "hace", "hacen", "hacia", "hacía", "hice", "hizo", "hecho",
            
            # Others
            "incluso", "ademas", "además", "tambien", "también", "tampoco", "mientras", 
            "durante", "excepto", "salvo", "menos"
        }
    

    def _split(self, text: str | None) -> list[str]:
        """Basic tokenization."""
        if not text: return []
        return re.findall(r"\b\w+\b", text.lower())

    def _filter(self, text: str | None) -> list[str]:
        """Filters words with meaningful (no stop words)."""
        return [w for w in self._split(text) if w not in self.STOPWORDS_ES]

    def count_total(self, text: str | None) -> int:
        """Total words (including garbage)."""
        return len(self._split(text))

    def count_meaningful(self, text: str | None) -> int:
        """Count of words with meaningful (no stop words)."""
        return len(self._filter(text))

    def count_unique(self, text: str | None) -> int:
        """Count of unique words with meaning. """
        return len(set(self._filter(text)))

    def get_diversity(self, unique: int, total: int) -> float:
        """Lexical richness ratio."""
        if total == 0: return 0.0
        return round(unique / total, 3)
    