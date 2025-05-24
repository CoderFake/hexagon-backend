import re
import unicodedata
from django.utils.text import slugify


class SlugConverter:
    """
    A utility class to convert strings into slugs, including handling Vietnamese characters.
    """
    VIETNAMESE_CHAR_MAP = {
        'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
        'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
        'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
        'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
        'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
        'đ': 'd',
        'À': 'A', 'Á': 'A', 'Ạ': 'A', 'Ả': 'A', 'Ã': 'A',
        'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ậ': 'A', 'Ẩ': 'A', 'Ẫ': 'A',
        'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ặ': 'A', 'Ẳ': 'A', 'Ẵ': 'A',
        'È': 'E', 'É': 'E', 'Ẹ': 'E', 'Ẻ': 'E', 'Ẽ': 'E',
        'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ệ': 'E', 'Ể': 'E', 'Ễ': 'E',
        'Ì': 'I', 'Í': 'I', 'Ị': 'I', 'Ỉ': 'I', 'Ĩ': 'I',
        'Ò': 'O', 'Ó': 'O', 'Ọ': 'O', 'Ỏ': 'O', 'Õ': 'O',
        'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ộ': 'O', 'Ổ': 'O', 'Ỗ': 'O',
        'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ợ': 'O', 'Ở': 'O', 'Ỡ': 'O',
        'Ù': 'U', 'Ú': 'U', 'Ụ': 'U', 'Ủ': 'U', 'Ũ': 'U',
        'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ự': 'U', 'Ử': 'U', 'Ữ': 'U',
        'Ỳ': 'Y', 'Ý': 'Y', 'Ỵ': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y',
        'Đ': 'D'
    }

    def __init__(self, separator='-', max_length=None):
        self.separator = separator
        self.max_length = max_length

    def remove_vietnamese_accents(self, text):
        if not text:
            return ""

        for vietnamese_char, latin_char in self.VIETNAMESE_CHAR_MAP.items():
            text = text.replace(vietnamese_char, latin_char)

        return text

    def clean_text(self, text):
        if not text:
            return ""

        text = text.strip()
        text = self.remove_vietnamese_accents(text)
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'\s+', self.separator, text)
        text = text.lower()
        text = re.sub(f'{re.escape(self.separator)}+', self.separator, text)
        text = text.strip(self.separator)

        if self.max_length and len(text) > self.max_length:
            text = text[:self.max_length].rstrip(self.separator)

        return text

    def to_slug(self, text):
        return self.clean_text(text)

    def create_unique_slug(self, model_class, title, slug_field='slug', instance=None):
        base_slug = self.to_slug(title)
        unique_slug = base_slug
        counter = 1

        while True:
            queryset = model_class.objects.filter(**{slug_field: unique_slug})

            if instance:
                queryset = queryset.exclude(pk=instance.pk)

            if not queryset.exists():
                break

            unique_slug = f"{base_slug}{self.separator}{counter}"
            counter += 1

        return unique_slug


class SlugMixin:
    """
    Mixin class to automatically generate slugs for Django models.
    """

    slug_converter = SlugConverter()
    slug_source_field = 'name'
    slug_field = 'slug'

    def save(self, *args, **kwargs):
        if not getattr(self, self.slug_field):
            source_text = getattr(self, self.slug_source_field, '')
            slug_value = self.slug_converter.create_unique_slug(
                self.__class__,
                source_text,
                self.slug_field,
                self
            )
            setattr(self, self.slug_field, slug_value)

        super().save(*args, **kwargs)

