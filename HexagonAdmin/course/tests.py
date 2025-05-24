from utils import SlugConverter

if __name__ == "__main__":
    converter = SlugConverter()

    test_cases = [
        "toán lớp 5",
        "math for 5 grade",
        "Khóa học Tiếng Anh cơ bản",
        "Programming with Python & Django",
        "Lịch sử Việt Nam hiện đại",
        "Machine Learning Fundamentals",
        "Đồ án tốt nghiệp 2024"
    ]

    print("Kiểm tra chuyển đổi slug:")
    for text in test_cases:
        slug = converter.to_slug(text)
        print(f"'{text}' -> '{slug}'")

    print("\nKiểm tra với separator khác:")
    converter_underscore = SlugConverter(separator='_', max_length=20)
    for text in test_cases[:3]:
        slug = converter_underscore.to_slug(text)
        print(f"'{text}' -> '{slug}'")