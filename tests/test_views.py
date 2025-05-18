import pytest
from unittest.mock import patch, Mock
from datetime import datetime
import pandas as pd

from src.views import main_web, main_events


@pytest.fixture
def mock_data():
    """Фикстура с тестовыми данными DataFrame"""
    return pd.DataFrame({
        "Сумма платежа": [-1000, -2000, 3000, -500],
        "Статус": ["OK", "OK", "OK", "FAILED"],
        "Категория": ["Супермаркеты", "Транспорт", "Каршеринг", "Переводы"],
        "Дата платежа": ["01-01-2023", "15-01-2023", "01-01-2023", "20-01-2023"],
        "Номер карты": ["1234", "5678", "1234", "5678"],
        "Описание": ["Магнит", "Такси", "Яндекс-Драйв", "Олег"]
    })
