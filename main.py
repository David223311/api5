import requests
import os
from itertools import count
from terminaltables import AsciiTable


def predict_rub_salary_sj(salary):
    if salary["payment_from"] and salary["payment_to"]:
        average_salary = int((salary["payment_from"] + salary["payment_to"]) / 2)
    elif salary["payment_from"]:
        average_salary = int(salary["payment_from"] * 1.2)
    elif salary["payment_to"]:
        average_salary = int(salary["payment_to"] * 0.8)
    else:
        average_salary = None
    return average_salary


def predict_rub_salary_hh(salary):
    if salary and salary["currency"] == "RUR":
        if salary["from"] and salary["to"]:
            average_salary = int((salary["from"] + salary["to"]) / 2)
        elif salary["from"]:
            average_salary = int(salary["from"] * 1.2)
        elif salary["to"]:
            average_salary = int(salary["to"] * 0.8)
        else:
            average_salary = None
        return average_salary


def get_vacansy_hh():
    prorgamm_langs = ["python", "Java", "PHP"]
    vacansy_by_language = {}
    for prorgamm_lang in prorgamm_langs:
        all_salary = []
        for page in count(0):
            url = "https://api.hh.ru/vacancies/"
            params = {"text": prorgamm_lang, "area": 1, "period": 30, "page": page}
            response = requests.get(url, params=params)
            response.raise_for_status()
            if page >= response.json()["pages"] - 1:
                break
            found_vacancy = response.json()["found"]
            for vacansy in response.json()["items"]:
                vacansy_predicte = predict_rub_salary_hh(vacansy["salary"])
                if vacansy_predicte:
                    all_salary.append(vacansy_predicte)
        average_salary = None
        if all_salary:
            average_salary = int(sum(all_salary) / len(all_salary))
        vacansy_by_language[prorgamm_lang] = {
            "vacancies_found": found_vacancy,
            "vacancies_processed": len(all_salary),
            "average_salary": average_salary,
        }
    return vacansy_by_language


def get_vacansy_sj(secret_key):
    prorgamm_langs = ["python", "Java", "PHP"]
    vacansy_by_language = {}
    for prorgamm_lang in prorgamm_langs:
        all_salary = []
        for page in count(0, 1):
            url = "https://api.superjob.ru/2.0/vacancies/"
            headers = {"X-Api-App-Id": secret_key}
            params = {"town": "Moscow", "keyword": prorgamm_lang, "page": page}
            response = requests.get(url, params=params, headers=headers)
            found_vacancy = response.json()["total"]
            if not response.json()["objects"]:
                break
            for profession in response.json()["objects"]:
                predict_rub_salary = predict_rub_salary_sj(profession)
                if predict_rub_salary:
                    all_salary.append(predict_rub_salary)
        average_salary = None
        if all_salary:
            average_salary = int(sum(all_salary) / len(all_salary))
        vacansy_by_language[prorgamm_lang] = {
            "vacancies_found": found_vacancy,
            "vacancies_processed": len(all_salary),
            "average_salary": average_salary,
        }
    return vacansy_by_language


def table(vacansies, title):
    table_data = [
        [
            "Язык программирования ",
            "Вакансий найдено",
            "Вакансий обработано",
            "Средняя зарплата",
        ]
    ]
    for language, vacansy in vacansies.items():
        table_data.append(
            [
                language,
                vacansy["vacancies_found"],
                vacansy["vacancies_processed"],
                vacansy["average_salary"],
            ]
        )
    table = AsciiTable(table_data, title)
    return table.table


def main():
    secret_key = os.environ["SUPERJOB_API_KEY"]
    print(table(get_vacansy_sj(secret_key), "SJ Moscow"))
    print(table(get_vacansy_hh(), "HH Moscow"))


if __name__ == "__main__":
    main()
