import pytest
from slugify_fr import slugify

class TestSlugify:
    def test_basic_conversion(self):
        assert slugify("Hello World") == "hello-world"
    
    def test_french_accents(self):
        assert slugify("Café") == "cafe"
        assert slugify("Hôtel") == "hotel"
        assert slugify("Crème brûlée") == "creme-brulee"
    
    def test_apostrophes(self):
        assert slugify("L'été") == "l-ete"
        assert slugify("Aujourd'hui") == "aujourd-hui"
    
    def test_special_characters(self):
        assert slugify("Coût: 10€!") == "cout-10"
        assert slugify("Test @#$% symbols") == "test-symbols"
    
    def test_multiple_spaces(self):
        assert slugify("Multi    spaces   here") == "multi-spaces-here"
    
    def test_custom_separator(self):
        assert slugify("Hello World", separator="_") == "hello_world"
    
    def test_empty_string(self):
        assert slugify("") == ""
        assert slugify("   ") == ""
    
    def test_only_special_chars(self):
        assert slugify("@#$%^&*()") == ""