import requests


def send_sms_htmlweb(phone, text, api_key):
    """
    Отправка SMS через API htmlweb.ru
    :param phone: Номер телефона (формат: 79123456789)
    :param text: Текст сообщения
    :param api_key: Ваш API-ключ
    :return: Ответ сервера
    """
    url = "http://htmlweb.ru/sendsms/api.php"
    params = {
        "send_sms": "",
        "sms_text": text,
        "sms_to": phone,
        "api_key": api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Проверка на ошибки HTTP
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Ошибка при отправке SMS: {e}"


if __name__ == "__main__":
    API_KEY = "b6d79dde7c3af9a235ab5915b3740600"
    PHONE = "79279071414"
    MESSAGE = "Test SMS from Python"

    result = send_sms_htmlweb(PHONE, MESSAGE, API_KEY)
    print("Результат:", result)