"""
LibrairieCI - Service d'impression des reçus
"""
import tempfile, os, webbrowser
from datetime import datetime


def imprimer_recu(numero: str, vendeur: str, panier: list, total: float):
    """Génère un reçu HTML et l'ouvre dans le navigateur pour impression."""
    now = datetime.now().strftime("%d/%m/%Y à %H:%M")

    lignes_html = ""
    for item in panier:
        sous_total = item["prix"] * item["qte"]
        lignes_html += f"""
        <tr>
            <td>{item['titre']}</td>
            <td style="text-align:center">{item['qte']}</td>
            <td style="text-align:right">{int(item['prix']):,} FCFA</td>
            <td style="text-align:right"><strong>{int(sous_total):,} FCFA</strong></td>
        </tr>""".replace(",", " ")

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Reçu LibrairieCI – {numero}</title>
<style>
  @page {{ size: 80mm auto; margin: 0; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Courier New', monospace; }}
  body {{ width: 80mm; max-width: 80mm; padding: 8px; font-size: 12px; color: #111; }}
  .header {{ text-align: center; padding: 10px 0; border-bottom: 2px dashed #aaa; }}
  .header h1 {{ font-size: 20px; color: #00823C; }}
  .header p {{ font-size: 11px; color: #555; margin-top: 3px; }}
  .info {{ padding: 8px 0; border-bottom: 1px dashed #ccc; font-size: 11px; }}
  .info p {{ margin: 2px 0; }}
  table {{ width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 11px; }}
  th {{ background: #00823C; color: white; padding: 4px 6px; text-align: left; }}
  td {{ padding: 4px 6px; border-bottom: 1px solid #eee; }}
  .total-row {{ font-size: 15px; font-weight: bold; }}
  .total-row td {{ border-top: 2px solid #00823C; padding-top: 8px; }}
  .footer {{ text-align: center; padding: 10px 0; font-size: 11px; color: #555; border-top: 2px dashed #aaa; }}
  .no-print {{ text-align:center; margin: 20px 0; }}
  .btn {{ background:#00823C; color:white; border:none; padding:10px 30px;
          font-size:14px; border-radius:6px; cursor:pointer; }}
  .btn:hover {{ background:#005F2B; }}
  @media print {{ .no-print {{ display:none; }} body {{ width:100%; }} }}
</style>
</head>
<body>
<div class="header">
  <h1> LibrairieCI</h1>
  <p>Gestion Professionnelle</p>
  <p>Côte d'Ivoire</p>
</div>

<div class="info">
  <p><strong>N° Vente :</strong> {numero}</p>
  <p><strong>Date :</strong> {now}</p>
  <p><strong>Vendeur :</strong> {vendeur}</p>
</div>

<table>
  <thead>
    <tr>
      <th>Article</th>
      <th style="text-align:center">Qté</th>
      <th style="text-align:right">P.U.</th>
      <th style="text-align:right">Total</th>
    </tr>
  </thead>
  <tbody>
    {lignes_html}
    <tr class="total-row">
      <td colspan="3">TOTAL À PAYER</td>
      <td style="text-align:right; color:#00823C">{int(total):,} FCFA</td>
    </tr>
  </tbody>
</table>

<div class="footer">
  <p>Merci pour votre achat !</p>
  <p>LibrairieCI – {datetime.now().strftime("%Y")}</p>
</div>

<div class="no-print">
  <button class="btn" onclick="window.print()"> Imprimer ce reçu</button>
</div>
<script>
  // Ouvrir la boîte d'impression automatiquement
  window.onload = function() {{ setTimeout(function(){{ window.print(); }}, 600); }};
</script>
</body>
</html>""".replace(",", " ")

    # Écrire dans un fichier temporaire
    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.html', delete=False,
        prefix='recu_librairie_', encoding='utf-8'
    )
    tmp.write(html)
    tmp_path = tmp.name
    tmp.close()

    webbrowser.open(f'file:///{os.path.abspath(tmp_path)}')
    return tmp_path
