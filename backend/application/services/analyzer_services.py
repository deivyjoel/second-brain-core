import re 

class AnalyzerService:
    def __init__(self):

        self.STOPWORDS_ES = {
        "a", "acá", "ahí", "al", "algo", "algunas", "algunos",
        "ante", "antes", "aquel", "aquella", "aquellas", "aquellos",
        "aquí", "así", "aun", "aunque", "bajo", "bien", "cada",
        "casi", "como", "con", "contra", "cual", "cuales",
        "cuando", "cuanto", "de", "del", "desde", "donde", "dos",
        "el", "ella", "ellas", "ellos", "en", "entonces", "entre",
        "era", "erais", "eran", "eras", "eres", "es", "esa", "esas",
        "ese", "eso", "esos", "esta", "estaba", "estaban", "estado",
        "estáis", "estamos", "están", "estar", "estas", "este",
        "esto", "estos", "fue", "fueron", "fui", "ha", "había",
        "habían", "haber", "hace", "hacia", "han", "hasta", "hay",
        "he", "incluso", "la", "las", "le", "les", "lo", "los",
        "me", "mi", "mis", "más", "muy", "no", "nos", "nosotros",
        "o", "os", "otra", "otras", "otro", "otros", "para", "pero",
        "poco", "por", "porque", "que", "qué", "quien", "quienes",
        "se", "sea", "ser", "si", "sí", "sin", "sobre", "su", "sus",
        "tal", "también", "te", "tendrá", "tengo", "ti", "tiene",
        "todo", "todos", "tu", "tus", "un", "una", "uno", "unos",
        "vosotros", "y", "ya"
        }

# --- HELPERS (Privados) ---
    def _split(self, text: str | None) -> list[str]:
        """Tokenización básica."""
        if not text: return []
        return re.findall(r"\b\w+\b", text.lower())

    def _filter(self, text: str | None) -> list[str]:
        """Filtra palabras de contenido (sin stopwords)."""
        return [w for w in self._split(text) if w not in self.STOPWORDS_ES]

    # --- MÉTODOS PÚBLICOS (Cortos y claros) ---
    def count_total(self, text: str | None) -> int:
        """Total de palabras (incluyendo basura)."""
        return len(self._split(text))

    def count_meaningful(self, text: str | None) -> int:
        """Conteo de palabras con significado (sin stopwords)."""
        return len(self._filter(text))

    def count_unique(self, text: str | None) -> int:
        """Vocabulario único (semántico)."""
        return len(set(self._filter(text)))

    def get_diversity(self, unique: int, total: int) -> float:
        """Ratio de riqueza léxica."""
        if total == 0: return 0.0
        return round(unique / total, 3)