from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests
from guru_piket import settings
from datetime import datetime

# URL PocketBase untuk koleksi "users" dan "guestsbook"
POCKETBASE_URL_USERS = f"{settings.POCKETBASE_URL}/api/collections/_superusers/auth-with-password"
POCKETBASE_URL_RECORDS = f"{settings.POCKETBASE_URL}/api/collections/guestsbook/records"

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            payload = {"identity": username, "password": password}
            response = requests.post(POCKETBASE_URL_USERS, json=payload)
            response.raise_for_status()
            token = response.json().get('token')
            user_data = response.json().get('record')

            request.session['pocketbase_token'] = token
            request.session['pocketbase_user'] = user_data
            print("berhasil login")
            return redirect('izin_guru')

        except requests.exceptions.RequestException as e:
            print("gagal login")
            return render(request, 'guru/guru_login.html', {'error': f'Login gagal: {str(e)}'})

    return render(request, 'guru/guru_login.html')

def izin_guru_view(request):
    token = request.session.get('pocketbase_token')
    if not token:
        return render(request, 'guru/izin_guru.html', {'error': 'Token PocketBase tidak ditemukan', 'izin_murid': []})

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(POCKETBASE_URL_RECORDS, headers=headers)
        response.raise_for_status()
        izin_murid = response.json().get('items', [])
        context = {'izin_murid': izin_murid}
        return render(request, 'guru/izin_guru.html', context)

    except requests.exceptions.RequestException as e:
        return render(request, 'guru/izin_guru.html', {'error': f'Error fetching data from PocketBase: {str(e)}', 'izin_murid': []})

def tindakan_izin_view(request, izin_id):
    token = request.session.get('pocketbase_token')
    if not token:
        return render(request, 'guru/tindakan_guru.html', {'error': 'Token PocketBase tidak ditemukan'})

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{POCKETBASE_URL_RECORDS}/{izin_id}", headers=headers)
        response.raise_for_status()
        izin = response.json()

        if not izin.get('id'):
            return render(request, 'guru/tindakan_guru.html', {'error': f'Data izin dengan ID {izin_id} tidak ditemukan', 'izin': {'id': izin_id}})

        # Jika sudah ada tindakan, redirect ke izin_guru
        if 'tindakan' in izin and izin['tindakan']:
            return redirect('izin_guru')

        context = {'izin': izin}
        return render(request, 'guru/tindakan_guru.html', context)

    except requests.exceptions.RequestException as e:
        return render(request, 'guru/tindakan_guru.html', {'error': f'Error fetching data from PocketBase: {str(e)}'})

def proses_tindakan_view(request, izin_id):
    if request.method == 'POST':
        token = request.session.get('pocketbase_token')
        if not token:
            return render(request, 'guru/tindakan_guru.html', {'error': 'Token PocketBase tidak ditemukan'})

        headers = {"Authorization": f"Bearer {token}"}
        tindakan = request.POST['tindakan']  # Menggunakan 'tindakan' sesuai form
        alasan = request.POST.get('alasan', '').strip()

        if not alasan:
            return render(request, 'guru/tindakan_guru.html', {'error': 'Alasan wajib diisi.', 'izin': {'id': izin_id}})

        try:
            response = requests.get(f"{POCKETBASE_URL_RECORDS}/{izin_id}", headers=headers)
            response.raise_for_status()
            izin = response.json()

            update_data = {
                'tindakan': tindakan,
                'alasan': alasan,
                'tanggal_tindakan': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            izin.update(update_data)

            update_response = requests.patch(f"{POCKETBASE_URL_RECORDS}/{izin_id}", json=izin, headers=headers)
            update_response.raise_for_status()

            return redirect('izin_guru')  # Redirect ke izin_guru setelah simpan

        except requests.exceptions.RequestException as e:
            return render(request, 'guru/tindakan_guru.html', {'error': f'Error processing action: {str(e)}', 'izin': {'id': izin_id}})

    return redirect('izin_guru')

def pocketbase_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        token = request.session.get('pocketbase_token')
        if not token:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper