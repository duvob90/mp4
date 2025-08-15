import os
import csv
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

API_KEY = os.environ.get('MERCADOPUBLICO_API_KEY')
if not API_KEY:
    raise SystemExit('MERCADOPUBLICO_API_KEY environment variable is not set')

URL = f"https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?ticket={API_KEY}"
DETAIL_URL = "https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion={}"


def fetch_details(code: str) -> tuple[str, str]:
    """Fetch estado and descripcion from the public details page."""
    try:
        resp = requests.get(DETAIL_URL.format(code), timeout=60)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        estado = soup.find("span", id="lblFicha1Estado")
        descripcion = soup.find("span", id="lblFicha1Descripcion")
        return (
            estado.text.strip() if estado else "",
            " ".join(descripcion.text.split()) if descripcion else "",
        )
    except Exception:
        return "", ""

def main():
    response = requests.get(URL, timeout=60)
    response.raise_for_status()
    data = response.json()
    items = data.get('Listado', [])
    fields = ['CodigoExterno', 'Nombre', 'CodigoEstado', 'FechaCierre', 'Estado', 'Descripcion']
    codes = [item.get('CodigoExterno') for item in items]
    details = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        for code, result in zip(codes, executor.map(fetch_details, codes)):
            details[code] = result
    with open('licitaciones.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for item in items:
            code = item.get('CodigoExterno', '')
            estado, descripcion = details.get(code, ('', ''))
            row = {
                'CodigoExterno': code,
                'Nombre': item.get('Nombre', ''),
                'CodigoEstado': item.get('CodigoEstado', ''),
                'FechaCierre': item.get('FechaCierre', ''),
                'Estado': estado,
                'Descripcion': descripcion,
            }
            writer.writerow(row)

if __name__ == '__main__':
    main()
