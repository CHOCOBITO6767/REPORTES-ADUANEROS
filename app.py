import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pandas as pd

# 1. Cargar y preparar los datos del archivo Excel
archivo = "ESTADISTICA DELTA 2026.xlsx"
df = pd.read_excel(archivo, sheet_name="1")

df["Fecha"] = pd.to_datetime(df["Fecha"])
df["Mes_Num"] = df["Fecha"].dt.month
df["Año"] = df["Fecha"].dt.year

meses_es = {
    1: "Ene",
    2: "Feb",
    3: "Mar",
    4: "Abr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dic",
}
df["Mes_Nombre"] = df["Mes_Num"].map(meses_es)

regimen_map = {
    1: "Importación Definitiva (01)",
    40: "Zonas Francas (40)",
    90: "Perfeccionamiento Activo",
}
df["Regimen_Nombre"] = (
    df["Regimen"].map(regimen_map).fillna(df["Regimen"].astype(str))
)


# 2. SELECCIÓN DEL CLIENTE (Búsqueda automática de "ELYON")
# Puedes cambiar este texto entre comillas cuando quieras buscar otro cliente
termino_busqueda = "ELYON"

clientes_disponibles = df["Comerciante"].dropna().unique()
cliente_encontrado = None

for c in clientes_disponibles:
  if termino_busqueda.upper() in str(c).upper():
    cliente_encontrado = c
    break

if not cliente_encontrado:
  raise ValueError(
      f"No se encontró ningún cliente que contenga '{termino_busqueda}'."
  )

print(f"✅ Cliente seleccionado automáticamente: {cliente_encontrado}")

# Filtrar información completa para el cliente
df_client = df[df["Comerciante"] == cliente_encontrado].copy()

# KPIs Totales Anuales
total_duas = len(df_client)
peso_total = df_client["PesoBruto"].sum()
valor_cif = df_client["CIF"].sum()
tributos = df_client["TotalImpuestos"].sum()

# Agrupación cronológica completa por mes y año
agrupado_mes = (
    df_client.groupby(["Año", "Mes_Num", "Mes_Nombre"], as_index=False)
    .agg(
        DUAs=("Numero", "count"),
        Peso=("PesoBruto", "sum"),
        CIF=("CIF", "sum"),
        Tributos=("TotalImpuestos", "sum"),
    )
    .sort_values(by=["Año", "Mes_Num"])
)

anios_unicos = agrupado_mes["Año"].unique()
labels_mes = [
    f"{m} {a}" if len(anios_unicos) > 1 else m
    for m, a in zip(agrupado_mes["Mes_Nombre"], agrupado_mes["Año"])
]

regimen_counts = df_client["Regimen_Nombre"].value_counts()


# 3. DISEÑO Y RENDERIZADO DEL REPORTE EJECUTIVO
fig = plt.figure(figsize=(15, 12), facecolor="#F4F5F7")

# Banner Header
ax_header = fig.add_axes([0.05, 0.88, 0.90, 0.08])
ax_header.axis("off")
header_box = patches.FancyBboxPatch(
    (0, 0),
    1,
    1,
    transform=ax_header.transAxes,
    facecolor="#4A2E80",
    edgecolor="none",
    boxstyle="round,pad=0,rounding_size=0.15",
)
ax_header.add_patch(header_box)
ax_header.text(
    0.5,
    0.62,
    "REPORTE ESTADÍSTICO DE OPERACIONES ADUANERAS",
    color="white",
    fontsize=15,
    fontweight="bold",
    ha="center",
    va="center",
)
ax_header.text(
    0.5,
    0.28,
    f"CLIENTE: {cliente_encontrado}",
    color="#E9D8FD",
    fontsize=11,
    fontweight="bold",
    ha="center",
    va="center",
)

# Tarjetas de Indicadores (KPIs)
ax_kpi = fig.add_axes([0.05, 0.74, 0.90, 0.11])
ax_kpi.axis("off")
kpis = [
    ("DUAS PROCESADOS", f"{total_duas:,}"),
    ("PESO TOTAL", f"{peso_total:,.0f} kg"),
    ("VALOR CIF TOTAL", f"${valor_cif:,.0f}"),
    ("TRIBUTOS TOTALES", f"${tributos:,.0f}"),
]
positions = [0.0, 0.26, 0.52, 0.76]
for i, (title, val) in enumerate(kpis):
  x = positions[i]
  card = patches.FancyBboxPatch(
      (x, 0),
      0.24,
      1,
      transform=ax_kpi.transAxes,
      facecolor="white",
      edgecolor="#E2E8F0",
      linewidth=1.2,
      boxstyle="round,pad=0,rounding_size=0.1",
  )
  ax_kpi.add_patch(card)
  ax_kpi.text(
      x + 0.12,
      0.68,
      title,
      fontsize=9,
      color="#718096",
      fontweight="bold",
      ha="center",
      va="center",
  )
  ax_kpi.text(
      x + 0.12,
      0.32,
      val,
      fontsize=16,
      color="#4A2E80",
      fontweight="bold",
      ha="center",
      va="center",
  )

# Ubicación de los 4 gráficos
ax1 = fig.add_axes([0.07, 0.42, 0.39, 0.24])  # DUAs (Línea con área)
ax2 = fig.add_axes([0.56, 0.42, 0.39, 0.24])  # Peso (Línea con área)
ax3 = fig.add_axes([0.07, 0.08, 0.39, 0.24])  # CIF vs Tributos (Líneas)
ax4 = fig.add_axes([0.56, 0.08, 0.39, 0.24])  # Régimen (Gráfica de Dona)

COLOR_PURPLE = "#5B32A8"
COLOR_GRAY = "#94A3B8"

for ax in [ax1, ax2, ax3]:
  ax.set_facecolor("white")
  ax.spines["top"].set_visible(False)
  ax.spines["right"].set_visible(False)
  ax.spines["left"].set_color("#CBD5E1")
  ax.spines["bottom"].set_color("#CBD5E1")

x_vals = range(len(agrupado_mes))

# 1. Gráfico de Líneas: DUAs procesados por mes
ax1.plot(
    x_vals,
    agrupado_mes["DUAs"],
    marker="o",
    color=COLOR_PURPLE,
    linewidth=2.5,
    markersize=7,
    zorder=3,
)
ax1.fill_between(
    x_vals, agrupado_mes["DUAs"], color=COLOR_PURPLE, alpha=0.12, zorder=2
)
for x, y in zip(x_vals, agrupado_mes["DUAs"]):
  ax1.annotate(
      f"{y}",
      xy=(x, y),
      xytext=(0, 7),
      textcoords="offset points",
      ha="center",
      fontsize=8.5,
      fontweight="bold",
      color="#2D3748",
  )
ax1.set_xticks(x_vals)
ax1.set_xticklabels(labels_mes, fontsize=8.5, color="#475569")
ax1.set_ylim(
    0, max(agrupado_mes["DUAs"]) * 1.3 if len(agrupado_mes) > 0 else 10
)
ax1.set_title(
    "DUAs procesados por mes",
    fontsize=11,
    fontweight="bold",
    color="#1E293B",
    pad=12,
)
ax1.set_ylabel("Cantidad de DUAs", fontsize=8.5, color="#64748B")
ax1.grid(axis="y", linestyle="--", alpha=0.5, color="#E2E8F0")

# 2. Gráfico de Líneas: Peso importado por mes
ax2.plot(
    x_vals,
    agrupado_mes["Peso"],
    marker="o",
    color=COLOR_PURPLE,
    linewidth=2.5,
    markersize=6,
    zorder=3,
)
ax2.fill_between(
    x_vals, agrupado_mes["Peso"], color=COLOR_PURPLE, alpha=0.12, zorder=2
)
ax2.set_xticks(x_vals)
ax2.set_xticklabels(labels_mes, fontsize=8.5, color="#475569")
ax2.set_title(
    "Peso importado por mes (kg)",
    fontsize=11,
    fontweight="bold",
    color="#1E293B",
    pad=12,
)
ax2.set_ylabel("Kilogramos", fontsize=8.5, color="#64748B")
ax2.grid(axis="y", linestyle="--", alpha=0.5, color="#E2E8F0")

# 3. Gráfico de Líneas: Valor CIF vs Tributos
ax3.plot(
    x_vals,
    agrupado_mes["CIF"],
    marker="o",
    color=COLOR_PURPLE,
    linewidth=2.5,
    markersize=6,
    label="Valor CIF",
    zorder=3,
)
ax3.plot(
    x_vals,
    agrupado_mes["Tributos"],
    marker="s",
    color=COLOR_GRAY,
    linewidth=2,
    markersize=5,
    label="Tributos",
    zorder=3,
)
ax3.set_xticks(x_vals)
ax3.set_xticklabels(labels_mes, fontsize=8.5, color="#475569")
ax3.set_title(
    "Valor CIF vs. Tributos (USD)",
    fontsize=11,
    fontweight="bold",
    color="#1E293B",
    pad=12,
)
ax3.set_ylabel("USD", fontsize=8.5, color="#64748B")
ax3.legend(
    loc="upper left", frameon=True, facecolor="white", edgecolor="#E2E8F0"
)
ax3.grid(axis="y", linestyle="--", alpha=0.5, color="#E2E8F0")

# 4. Gráfico de Dona: DUAs por régimen / operación
colors_donut = ["#5B32A8", "#8B5CF6", "#C4B5FD", "#0284C7", "#D97706"]
wedges, texts, autotexts = ax4.pie(
    regimen_counts.values,
    labels=None,
    autopct="%1.1f%%",
    pctdistance=0.75,
    startangle=140,
    colors=colors_donut[: len(regimen_counts)],
    wedgeprops=dict(width=0.42, edgecolor="white", linewidth=2),
)
for autotext in autotexts:
  autotext.set_color("white")
  autotext.set_fontsize(8.5)
  autotext.set_fontweight("bold")

ax4.legend(
    wedges,
    regimen_counts.index,
    title="Régimen / Operación",
    loc="center left",
    bbox_to_anchor=(0.95, 0.5),
    frameon=False,
    fontsize=8.5,
)
ax4.set_title(
    "DUAs por régimen / operación",
    fontsize=11,
    fontweight="bold",
    color="#1E293B",
    pad=12,
)

# Guardar automáticamente la imagen del reporte
nombre_salida = f"Reporte_{cliente_encontrado.replace(' ', '_')}.png"
plt.savefig(nombre_salida, dpi=300, bbox_inches="tight")
plt.show()
print(f"¡Reporte generado con éxito para {cliente_encontrado}!")
