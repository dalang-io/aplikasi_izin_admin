import requests
from django.shortcuts import render
import os
from guru_piket import settings
# URL PocketBase untuk koleksi "guestsbook"
POCKETBASE_URL =  f"{settings.POCKETBASE_URL}/api/collections/guestsbook/records"

def izin_guru_view(request):
    # Header untuk autentikasi (gunakan token yang sama seperti di izin_project)
    token = os.getenv('POCKETBASE_TOKEN', 'default_token')
    headers = {
        "authorization": "Bearer RAHASIA"
    }

    try:
        # Ambil semua record dari koleksi "guestsbook"
        response = requests.get(POCKETBASE_URL, headers=headers)
        response.raise_for_status()  # Angkat exception jika ada error HTTP
        izin_murid = response.json().get('items', [])  # Ambil data dari response

        # Siapkan konteks untuk template
        context = {'izin_murid': izin_murid}
        return render(request, 'guru/izin_guru.html', context)

    except requests.exceptions.RequestException as e:
        return render(request, 'guru/izin_guru.html', {'error': f'Error fetching data from PocketBase: {str(e)}', 'izin_murid': []})
