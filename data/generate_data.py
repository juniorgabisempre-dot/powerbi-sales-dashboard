"""
generate_data.py
-----------------
Gera um dataset sintético de vendas em modelo dimensional (esquema estrela)
pronto para ser importado no Power BI Desktop:

    dim_date.csv      - dimensão de data (2024-01-01 a 2025-12-31)
    dim_customer.csv  - dimensão de clientes
    dim_product.csv   - dimensão de produtos
    fact_sales.csv    - fato de vendas, ligando as três dimensões

Nenhum dado real é utilizado — tudo é gerado com `Faker` a partir de uma
seed fixa, para reprodutibilidade.
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

SEED = 7
OUT_DIR = Path(__file__).resolve().parent

CATALOG = {
    "Eletrônicos": ["Fone de Ouvido Bluetooth", "Carregador Portátil 10000mAh",
                     "Mouse Sem Fio", "Teclado Mecânico", "Caixa de Som Bluetooth",
                     "Smartwatch Fitness"],
    "Casa e Cozinha": ["Panela Antiaderente 24cm", "Liquidificador 3 Velocidades",
                        "Jogo de Talheres Inox", "Air Fryer 4L", "Cafeteira Elétrica"],
    "Papelaria": ["Caderno Universitário 200fl", "Kit Canetas Coloridas",
                  "Mochila Escolar", "Agenda 2026", "Organizador de Mesa"],
    "Esporte e Lazer": ["Tênis de Corrida", "Garrafa Térmica 1L",
                         "Bola de Futebol Society", "Tapete de Yoga",
                         "Mochila de Trilha 30L"],
    "Moda": ["Camiseta Básica Algodão", "Jaqueta Corta-Vento", "Boné Aba Curva",
              "Mochila Casual", "Óculos de Sol UV400"],
}
STATES = ["SP", "RJ", "MG", "BA", "RS", "PR", "PE", "CE", "SC", "GO"]
SEGMENTS = ["Varejo", "Corporativo", "Pequena Empresa"]
REGIONS = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

MONTHS_PT = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
             "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
WEEKDAYS_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
               "Sexta-feira", "Sábado", "Domingo"]


def build_dim_date(start: date, end: date) -> list[dict]:
    rows = []
    date_id = 1
    d = start
    while d <= end:
        rows.append({
            "date_id": date_id,
            "date": d.isoformat(),
            "year": d.year,
            "quarter": f"T{(d.month - 1) // 3 + 1}",
            "month": d.month,
            "month_name": MONTHS_PT[d.month - 1],
            "day": d.day,
            "day_of_week": WEEKDAYS_PT[d.weekday()],
            "is_weekend": int(d.weekday() >= 5),
        })
        date_id += 1
        d += timedelta(days=1)
    return rows


def build_dim_customer(fake: Faker, n: int, start: date, end: date) -> list[dict]:
    rows = []
    span = (end - start).days
    for i in range(1, n + 1):
        name = fake.name()
        rows.append({
            "customer_id": f"CUST-{i:04d}",
            "customer_name": name,
            "email": fake.unique.email(),
            "state": random.choice(STATES),
            "segment": random.choice(SEGMENTS),
            "signup_date": (start + timedelta(days=random.randint(0, span))).isoformat(),
        })
    return rows


def build_dim_product() -> list[dict]:
    rows = []
    pid = 1
    for category, items in CATALOG.items():
        for item in items:
            cost = round(random.uniform(10, 210), 2)
            price = round(cost * random.uniform(1.4, 2.2), 2)
            rows.append({
                "product_id": f"PROD-{pid:04d}",
                "product_name": item,
                "category": category,
                "unit_cost": cost,
                "list_price": price,
            })
            pid += 1
    return rows


def build_fact_sales(n: int, dim_date, dim_customer, dim_product) -> list[dict]:
    rows = []
    for i in range(1, n + 1):
        d = random.choice(dim_date)
        cust = random.choice(dim_customer)
        prod = random.choice(dim_product)
        rows.append({
            "sale_id": f"SALE-{i:06d}",
            "date_id": d["date_id"],
            "customer_id": cust["customer_id"],
            "product_id": prod["product_id"],
            "region": random.choice(REGIONS),
            "quantity": random.randint(1, 6),
            "unit_price": prod["list_price"],
            "discount_pct": random.choice([0, 0, 0, 0.05, 0.1, 0.15, 0.2]),
        })
    return rows


def save_csv(rows: list[dict], filename: str) -> None:
    path = OUT_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"[generate_data] {len(rows)} linhas -> {path}")


def main() -> None:
    fake = Faker("pt_BR")
    Faker.seed(SEED)
    random.seed(SEED)

    start, end = date(2024, 1, 1), date(2025, 12, 31)

    dim_date = build_dim_date(start, end)
    dim_customer = build_dim_customer(fake, 60, start, end)
    dim_product = build_dim_product()
    fact_sales = build_fact_sales(300, dim_date, dim_customer, dim_product)

    save_csv(dim_date, "dim_date.csv")
    save_csv(dim_customer, "dim_customer.csv")
    save_csv(dim_product, "dim_product.csv")
    save_csv(fact_sales, "fact_sales.csv")


if __name__ == "__main__":
    main()
