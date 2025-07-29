import re
from typing import List, Dict, Any


def extract_data_from_text(text: str) -> Dict[str, List[str]]:
    """
    Извлекает из текста номера телефонов, email-ы, названия банков/платежных систем
    и их реквизиты (номера карт и электронных кошельков).
    """

    # Паттерны для поиска
    patterns = {
        'phones': [
            # Российские номера с +7 или 8, различные форматы
            r'(?:\+7|8)[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}',
            # Номера без кода страны
            r'(?<!\d)[0-9]{3}[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}(?!\d)',
            # Короткие номера
            r'(?<!\d)[0-9]{3}[\s\-]?[0-9]{4}(?!\d)',
        ],

        'emails': [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        ],

        'banks': [
            # Российские банки
            r'(?i)\b(?:сбербанк|втб|газпромбанк|альфа[\s\-]?банк|тинькофф|открытие|'
            r'россельхозбанк|райффайзен|уралсиб|росбанк|ак барс|мтс[\s\-]?банк|'
            r'совкомбанк|хоум[\s\-]?кредит|ренессанс|промсвязьбанк|кредит[\s\-]?европа)\b',

            # Платежные системы
            r'(?i)\b(?:яндекс[\s\.]?деньги|яндекс[\s\.]?денег|киви|qiwi|webmoney|'
            r'вебмани|paypal|пэйпал|visa|виза|mastercard|мастеркард|мир|'
            r'apple[\s\-]?pay|google[\s\-]?pay|samsung[\s\-]?pay)\b'
        ],

        'card_numbers': [
            # Номера банковских карт (группы по 4 цифры)
            r'\b(?:[0-9]{4}[\s\-]?){3}[0-9]{4}\b',
            # Номера карт без разделителей
            r'\b[0-9]{16}\b'
        ],

        'wallets': [
            # QIWI кошельки (номер телефона)
            r'(?i)(?:qiwi|киви)[\s\w]*(?:кошел[её]к|wallet)[\s\w]*(?:\+7|8)?[0-9]{10}',
            # Яндекс.Деньги
            r'(?i)(?:яндекс[\s\.]?ден[её]г|yandex[\s\.]?money)[\s\w]*[0-9]{11,16}',
            # WebMoney
            r'(?i)webmoney[\s\w]*[RZE][0-9]{12}',
            # Общие электронные кошельки (последовательности цифр после ключевых слов)
            r'(?i)(?:кошел[её]к|wallet|счет|account)[\s\w]*[0-9]{8,20}'
        ],

        'fio': [
            # Имя Отчество Фамилия (полное ФИО)
            r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\b',
            # Имя Фамилия (без отчества)
            r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?!\s+[А-ЯЁ][а-яё]+)\b',
            # Имя Отчество Ф. (отчество полное, фамилия сокращенная)
            r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\b',
            # Имя Ф. (имя полное, фамилия сокращенная)
            r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\b'
        ]
    }

    results = {
        'phones': [],
        'emails': [],
        'banks': [],
        'card_numbers': [],
        'wallets': [],
        'fio': []
    }

    # Поиск телефонов
    for pattern in patterns['phones']:
        matches = re.findall(pattern, text)
        results['phones'].extend(matches)

    # Поиск email-ов
    for pattern in patterns['emails']:
        matches = re.findall(pattern, text)
        results['emails'].extend(matches)

    # Поиск банков и платежных систем
    for pattern in patterns['banks']:
        matches = re.findall(pattern, text)
        results['banks'].extend(matches)

    # Поиск номеров карт
    for pattern in patterns['card_numbers']:
        matches = re.findall(pattern, text)
        # Фильтруем только валидные номера карт (начинающиеся с 4, 5, 6, 2 и т.д.)
        valid_cards = []
        for match in matches:
            clean_number = re.sub(r'[\s\-]', '', match)
            if clean_number[0] in '23456' and len(clean_number) == 16:
                valid_cards.append(match)
        results['card_numbers'].extend(valid_cards)

    # Поиск электронных кошельков
    for pattern in patterns['wallets']:
        matches = re.findall(pattern, text)
        results['wallets'].extend(matches)

    # Поиск ФИО
    all_fio_matches = []
    for pattern in patterns['fio']:
        matches = re.findall(pattern, text)
        all_fio_matches.extend(matches)

    # Фильтруем ФИО по наличию настоящих имен
    filtered_fio = []
    for fio in all_fio_matches:
        words = fio.split()
        first_word = words[0].lower()

        # Проверяем, что первое слово - это имя из нашего списка
        if first_word in names:
            # Дополнительно проверяем длину слов
            valid = True
            for word in words:
                clean_word = word.rstrip('.')
                if len(clean_word) < 2:
                    valid = False
                    break

            if valid:
                filtered_fio.append(fio)

    results['fio'] = filtered_fio

    # Удаляем дубликаты
    for key in results:
        results[key] = list(set(results[key]))

    return results


def clean_phone_number(phone: str) -> int:
    """Очищает номер телефона от лишних символов."""
    return int(re.sub(r'[+\s\-()]', '', phone))


def format_results(results: Dict[str, List[str]]) -> str:
    """Форматирует результаты для вывода."""
    output = []

    if results['phones']:
        output.append("📞 ТЕЛЕФОНЫ:")
        for phone in results['phones']:
            clean = clean_phone_number(phone)
            output.append(f"  • {phone} ({clean})")
        output.append("")

    if results['emails']:
        output.append("📧 EMAIL-Ы:")
        for email in results['emails']:
            output.append(f"  • {email}")
        output.append("")

    if results['banks']:
        output.append("🏦 БАНКИ И ПЛАТЕЖНЫЕ СИСТЕМЫ:")
        for bank in results['banks']:
            output.append(f"  • {bank}")
        output.append("")

    if results['card_numbers']:
        output.append("💳 НОМЕРА КАРТ:")
        for card in results['card_numbers']:
            masked = card[:4] + ' **** **** ' + card[-4:]
            output.append(f"  • {card} (замаскированный: {masked})")
        output.append("")

    if results['wallets']:
        output.append("💰 ЭЛЕКТРОННЫЕ КОШЕЛЬКИ:")
        for wallet in results['wallets']:
            output.append(f"  • {wallet}")
        output.append("")

    if results['fio']:
        output.append("👤 ФИО:")
        for fio in results['fio']:
            # Определяем тип ФИО (только запрошенные форматы)
            words = fio.split()
            if len(words) == 3 and not any('.' in word for word in words):
                fio_type = "Имя Отчество Фамилия"
            elif len(words) == 2 and not any('.' in word for word in words):
                fio_type = "Имя Фамилия"
            elif len(words) == 3 and words[2].endswith('.'):
                fio_type = "Имя Отчество Ф."
            elif len(words) == 2 and words[1].endswith('.'):
                fio_type = "Имя Ф."
            else:
                continue  # Пропускаем неподходящие форматы

            output.append(f"  • {fio} ({fio_type})")
        output.append("")

    return "\n".join(output) if output else "Данные не найдены."


# Пример использования
if __name__ == "__main__":
    # Тестовый текст
    test_text = """
    Свяжитесь со мной по телефону +7 (999)123-45-67 или 8-800-555-35-35.
    Email для связи: example@gmail.com или test.user@yandex.ru

    Принимаю оплату на карту Сбербанка 5536 9137 8765 4321
    Также можете перевести на Тинькофф или через QIWI кошелек +79991234567

    WebMoney кошелек: R123456789012
    Яндекс.Деньги: 410012345678901

    Работаю с ВТБ, Альфа-банком, принимаю Visa и MasterCard.
    PayPal тоже подходит: paypal@example.com

    Контактные лица:
    - Ростов Великий
    - Велкам в клаб
    - зхуй пизда руль
    - опа а
    - Иванов Петр Сергеевич (директор)
    - Смирнова Анна Владимировна (бухгалтер)
    - Петров И. С. (менеджер)
    - Сидоров Анатолий Сидоров. (консультант)
    - Козлов Дмитрий Александрович
    - Волкова Мария Ивановна
    - Федоров П. И.
    - Нестор М.
    - А. С. Пушкин
    - Лермонтов М. Ю.
    """

    print("Анализ текста:")
    print("=" * 50)
    print(test_text)
    print("=" * 50)

    results = extract_data_from_text(test_text)
    formatted_output = format_results(results)

    print("\nРЕЗУЛЬТАТЫ ИЗВЛЕЧЕНИЯ:")
    print("=" * 50)
    print(formatted_output)

    # Также можно получить сырые данные
    print("\nСЫРЫЕ ДАННЫЕ (словарь):")
    print("=" * 50)
    for key, values in results.items():
        if values:
            print(f"{key}: {values}")