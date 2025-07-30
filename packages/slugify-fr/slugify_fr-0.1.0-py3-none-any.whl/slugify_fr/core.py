import re
import unicodedata

def slugify(text: str, separator: str = "-") -> str:
    """
    Convertit un texte en slug URL-friendly optimisé pour le français.
    
    Args:
        text: Le texte à convertir
        separator: Le séparateur à utiliser (défaut: "-")
    
    Returns:
        str: Le slug généré
    
    Examples:
        >>> slugify("Café à la crème")
        'cafe-a-la-creme'
        >>> slugify("L'été en France")
        'l-ete-en-france'
    """
    if not text:
        return ""
    
    # Normalisation Unicode (décompose les accents)
    text = unicodedata.normalize('NFD', text)
    
    # Supprime les diacritiques (accents)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    
    # Minuscules
    text = text.lower()
    
    # Remplace les apostrophes et guillemets par des espaces
    text = re.sub(r"['\"""''`]", ' ', text)
    
    # Garde seulement lettres, chiffres et espaces
    text = re.sub(r'[^a-z0-9\s]', '', text)
    
    # Remplace les espaces multiples par un seul
    text = re.sub(r'\s+', ' ', text)
    
    # Supprime espaces début/fin et remplace par separator
    text = text.strip().replace(' ', separator)
    
    return text