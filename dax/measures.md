# Medidas DAX

Este documento reúne as medidas DAX usadas no dashboard, cada uma com o
código pronto para colar no Power BI Desktop e uma explicação da pergunta de
negócio que ela responde.

Todas as medidas assumem que a tabela de fatos `fact_sales` está relacionada
a `dim_date`, `dim_customer` e `dim_product` conforme o modelo descrito no
[README](../README.md), e que já existe uma medida base `Total Sales`
(a maioria das outras depende dela).

---

## 1. Total Sales

**Pergunta de negócio:** Qual é a receita total, considerando o desconto aplicado?

```dax
Total Sales =
SUMX (
    fact_sales,
    fact_sales[quantity] * fact_sales[unit_price] * (1 - fact_sales[discount_pct])
)
```

---

## 2. Total Orders

**Pergunta de negócio:** Quantos pedidos (vendas) foram registrados no período selecionado?

```dax
Total Orders =
DISTINCTCOUNT ( fact_sales[sale_id] )
```

---

## 3. Avg Ticket

**Pergunta de negócio:** Qual é o valor médio gasto por pedido (ticket médio)?

```dax
Avg Ticket =
DIVIDE ( [Total Sales], [Total Orders] )
```

`DIVIDE` é usado em vez de `/` para retornar `BLANK()` automaticamente
quando não há pedidos no contexto, evitando erros de divisão por zero.

---

## 4. YoY Growth %

**Pergunta de negócio:** Como a receita deste ano se compara à receita do mesmo período no ano anterior?

```dax
Sales PY =
CALCULATE (
    [Total Sales],
    SAMEPERIODLASTYEAR ( dim_date[date] )
)

YoY Growth % =
DIVIDE ( [Total Sales] - [Sales PY], [Sales PY] )
```

> `Sales PY` é uma medida auxiliar — crie-a antes de `YoY Growth %`.
> `SAMEPERIODLASTYEAR` exige que `dim_date[date]` esteja marcada como a
> coluna de data da tabela (Marcar como Tabela de Data no Power BI).

---

## 5. Running Total Sales

**Pergunta de negócio:** Qual é a receita acumulada ao longo do tempo (útil para gráficos de tendência)?

```dax
Running Total Sales =
CALCULATE (
    [Total Sales],
    FILTER (
        ALLSELECTED ( dim_date[date] ),
        dim_date[date] <= MAX ( dim_date[date] )
    )
)
```

---

## 6. Top Category Share

**Pergunta de negócio:** Qual a participação percentual da categoria mais vendida sobre o total, no contexto atual (ex.: dentro de uma região ou período filtrado)?

```dax
Top Category Share =
VAR SalesByCategory =
    ADDCOLUMNS (
        VALUES ( dim_product[category] ),
        "@CategorySales", [Total Sales]
    )
VAR TopCategorySales =
    MAXX ( SalesByCategory, [@CategorySales] )
RETURN
    DIVIDE ( TopCategorySales, [Total Sales] )
```

---

## Resumo

| Medida | Responde a |
|---|---|
| `Total Sales` | Receita total líquida de desconto |
| `Total Orders` | Volume de pedidos |
| `Avg Ticket` | Ticket médio por pedido |
| `YoY Growth %` | Crescimento da receita ano a ano |
| `Running Total Sales` | Receita acumulada ao longo do tempo |
| `Top Category Share` | Concentração de vendas na categoria líder |
