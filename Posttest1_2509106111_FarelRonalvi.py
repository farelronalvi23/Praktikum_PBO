ADMIN_USERNAME = 'onall'
ADMIN_PASSWORD = '23'

class Vila:
    nama_perusahaan = 'SIREVA (Sistem Reservasi Penyewaan Villa)'
    total_vila_terdaftar = 0
    pajak_persen = 10

    def __init__(self, kode_vila, nama_vila, lokasi, harga_per_malam, tipe_vila):
        self.kode_vila = kode_vila
        self.nama_vila = nama_vila
        self.lokasi = lokasi
        self._catatan_internal = 'Belum ada catatan'
        self.__harga_per_malam = 0
        self.harga_per_malam = harga_per_malam
        self.__tipe_vila = None
        self.tipe_vila = tipe_vila
        Vila.total_vila_terdaftar += 1

    @property
    def harga_per_malam(self):
        return self.__harga_per_malam

    @harga_per_malam.setter
    def harga_per_malam(self, nilai):
        if not isinstance(nilai, (int, float)) or nilai <= 0:
            raise ValueError(f"Harga vila tidak boleh 0/negatif. Input '{nilai}' ditolak.")
        self.__harga_per_malam = nilai

    @property
    def tipe_vila(self):
        return self.__tipe_vila

    @tipe_vila.setter
    def tipe_vila(self, nilai):
        if nilai not in ('Reguler', 'Premium'):
            raise ValueError(f"Tipe vila harus 'Reguler' atau 'Premium'. Input '{nilai}' ditolak.")
        self.__tipe_vila = nilai

    def tampilkan_info(self):
        print(f'  [{self.kode_vila}] ({self.tipe_vila}) {self.nama_vila} - {self.lokasi} | Rp{self.__harga_per_malam:,.0f}/malam')

    @classmethod
    def dari_dict(cls, data: dict):
        return cls(data['kode_vila'], data['nama_vila'], data['lokasi'], data['harga_per_malam'], data['tipe_vila'])

    @classmethod
    def ubah_pajak(cls, persen_baru):
        if persen_baru < 0:
            print('[VALIDASI GAGAL] Pajak tidak boleh negatif.')
            return
        cls.pajak_persen = persen_baru
        print(f'Pajak sewa vila sekarang menjadi {cls.pajak_persen}%')

    @staticmethod
    def validasi_kode_vila(kode_vila):
        return isinstance(kode_vila, str) and kode_vila.upper().startswith('VL')

class Penyewa:
    total_penyewa = 0
    jenis_keanggotaan_default = 'Reguler'
    minimal_umur_sewa = 18

    def __init__(self, nama, no_hp, nik, username, password):
        self.nama = nama
        self.no_hp = no_hp
        self.username = username
        self._jenis_keanggotaan = Penyewa.jenis_keanggotaan_default
        self.__nik = None
        self.nik = nik
        self.__password = None
        self.password = password
        Penyewa.total_penyewa += 1

    @property
    def nik(self):
        if self.__nik:
            return self.__nik[:4] + '*' * 12
        return None

    @nik.setter
    def nik(self, nilai):
        if not isinstance(nilai, str) or not nilai.isdigit() or len(nilai) != 16:
            raise ValueError(f"NIK harus 16 digit angka. Input '{nilai}' ditolak.")
        self.__nik = nilai

    @property
    def password(self):
        return '*' * len(self.__password) if self.__password else None

    @password.setter
    def password(self, nilai):
        if not isinstance(nilai, str) or len(nilai) < 4:
            raise ValueError('Password minimal 4 karakter.')
        self.__password = nilai

    def cek_password(self, input_password):
        return self.__password == input_password

    def tampilkan_profil(self):
        print(f'  Penyewa: {self.nama} | Username: {self.username} | HP: {self.no_hp} | NIK: {self.nik}')

    @classmethod
    def dari_dict(cls, data: dict):
        return cls(data['nama'], data['no_hp'], data['nik'], data['username'], data['password'])

    @staticmethod
    def validasi_no_hp(no_hp):
        return isinstance(no_hp, str) and no_hp.startswith('08') and (10 <= len(no_hp) <= 13)

class Transaksi:
    total_transaksi = 0
    denda_per_hari_telat = 50000
    status_valid = ('Menunggu Pembayaran', 'Lunas', 'Dibatalkan')

    def __init__(self, id_transaksi, penyewa: 'Penyewa', vila: 'Vila', jumlah_malam):
        self.id_transaksi = id_transaksi
        self.penyewa = penyewa
        self.vila = vila
        self.jumlah_malam = jumlah_malam
        self._catatan_admin = ''
        self.__status_pembayaran = 'Menunggu Pembayaran'
        Transaksi.total_transaksi += 1

    @property
    def status_pembayaran(self):
        return self.__status_pembayaran

    @status_pembayaran.setter
    def status_pembayaran(self, status_baru):
        if status_baru not in Transaksi.status_valid:
            raise ValueError(f"Status '{status_baru}' tidak dikenal. Pilihan: {Transaksi.status_valid}")
        self.__status_pembayaran = status_baru

    def hitung_total_bayar(self):
        subtotal = self.vila.harga_per_malam * self.jumlah_malam
        pajak = subtotal * (Vila.pajak_persen / 100)
        total = subtotal + pajak
        print(f'\n  --- Rincian Transaksi {self.id_transaksi} ---')
        print(f'  Penyewa   : {self.penyewa.nama}')
        print(f'  Vila      : {self.vila.nama_vila} ({self.jumlah_malam} malam)')
        print(f'  Subtotal  : Rp{subtotal:,.0f}')
        print(f'  Pajak     : Rp{pajak:,.0f} ({Vila.pajak_persen}%)')
        print(f'  Total     : Rp{total:,.0f}')
        print(f'  Status    : {self.status_pembayaran}')
        return total

    @classmethod
    def buat_transaksi(cls, id_transaksi, penyewa, vila, jumlah_malam):
        if not cls.validasi_jumlah_malam(jumlah_malam):
            print(f"[GAGAL] Jumlah malam '{jumlah_malam}' tidak valid.")
            return None
        return cls(id_transaksi, penyewa, vila, jumlah_malam)

    @staticmethod
    def validasi_jumlah_malam(jumlah_malam):
        return isinstance(jumlah_malam, int) and jumlah_malam >= 1

class Ulasan:
    total_ulasan = 0
    rating_min = 1
    rating_max = 5

    def __init__(self, id_ulasan, transaksi: 'Transaksi', rating, komentar):
        self.id_ulasan = id_ulasan
        self.transaksi = transaksi
        self.__rating = 0
        self.rating = rating
        self.komentar = komentar
        Ulasan.total_ulasan += 1

    @property
    def rating(self):
        return self.__rating

    @rating.setter
    def rating(self, nilai):
        if not isinstance(nilai, int) or not Ulasan.rating_min <= nilai <= Ulasan.rating_max:
            raise ValueError(f'Rating harus bilangan bulat antara {Ulasan.rating_min}-{Ulasan.rating_max}.')
        self.__rating = nilai

    def tampilkan_ulasan(self):
        bintang = '*' * self.rating
        print(f'  [{self.id_ulasan}] {self.transaksi.penyewa.nama} untuk {self.transaksi.vila.nama_vila}')
        print(f'  Rating  : {bintang} ({self.rating}/5)')
        print(f'  Komentar: {self.komentar}')

    @classmethod
    def buat_dari_transaksi(cls, id_ulasan, transaksi, rating, komentar):
        if transaksi.status_pembayaran != 'Lunas':
            print(f'[GAGAL] Transaksi {transaksi.id_transaksi} belum Lunas, ulasan tidak bisa dibuat.')
            return None
        return cls(id_ulasan, transaksi, rating, komentar)

    @staticmethod
    def validasi_komentar(komentar):
        return isinstance(komentar, str) and len(komentar.strip()) >= 5
daftar_vila = [
    Vila.dari_dict({'kode_vila': 'VL01', 'nama_vila': 'Vila Ubud Asri', 'lokasi': 'Ubud, Bali', 'harga_per_malam': 1200000, 'tipe_vila': 'Reguler'}),
    Vila.dari_dict({'kode_vila': 'VL02', 'nama_vila': 'Vila Kuta Nyaman', 'lokasi': 'Kuta, Bali', 'harga_per_malam': 1500000, 'tipe_vila': 'Reguler'}),
    Vila.dari_dict({'kode_vila': 'VL03', 'nama_vila': 'Vila Canggu Sederhana', 'lokasi': 'Canggu, Bali', 'harga_per_malam': 1300000, 'tipe_vila': 'Reguler'}),
    Vila.dari_dict({'kode_vila': 'VL04', 'nama_vila': 'Vila Seminyak Elite', 'lokasi': 'Seminyak, Bali', 'harga_per_malam': 3500000, 'tipe_vila': 'Premium'}),
    Vila.dari_dict({'kode_vila': 'VL05', 'nama_vila': 'Vila Uluwatu Cliffside', 'lokasi': 'Uluwatu, Bali', 'harga_per_malam': 4000000, 'tipe_vila': 'Premium'}),
    Vila.dari_dict({'kode_vila': 'VL06', 'nama_vila': 'Vila Nusa Dua Luxe', 'lokasi': 'Nusa Dua, Bali', 'harga_per_malam': 3800000, 'tipe_vila': 'Premium'}),
]
daftar_penyewa = []
daftar_transaksi = []
daftar_ulasan = []

def registrasi_penyewa():
    print('\n===== DAFTAR AKUN PENYEWA BARU =====')
    while True:
        nama = input('Nama lengkap : ').strip()
        if nama == '':
            print('[VALIDASI GAGAL] Nama tidak boleh kosong.')
            continue
        no_hp = input('No HP (08xxxxxxxxxx) : ').strip()
        if not Penyewa.validasi_no_hp(no_hp):
            print("[VALIDASI GAGAL] Format No HP salah (harus diawali '08', 10-13 digit).")
            continue
        nik = input('NIK (16 digit) : ').strip()
        username = input('Buat username : ').strip()
        if username == '':
            print('[VALIDASI GAGAL] Username tidak boleh kosong.')
            continue
        if any((p.username == username for p in daftar_penyewa)):
            print(f"[VALIDASI GAGAL] Username '{username}' sudah dipakai, pilih yang lain.")
            continue
        password = input('Buat password (min. 4 karakter) : ').strip()
        try:
            penyewa_baru = Penyewa(nama, no_hp, nik, username, password)
        except ValueError as e:
            print(f'[VALIDASI GAGAL] {e}')
            continue
        daftar_penyewa.append(penyewa_baru)
        print(f'\nAkun berhasil dibuat! Selamat datang, {penyewa_baru.nama}.')
        return penyewa_baru

def login():
    print('\n===== LOGIN =====')
    while True:
        username = input('Username (atau ketik 0 untuk kembali) : ').strip()
        if username == '0':
            return
        password = input('Password : ').strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            print('\nLogin admin berhasil.')
            menu_admin()
            return
        akun = next((p for p in daftar_penyewa if p.username == username), None)
        if akun is not None and akun.cek_password(password):
            print(f'\nLogin berhasil. Selamat datang kembali, {akun.nama}!')
            menu_penyewa(akun)
            return
        print('[GAGAL] Username atau password salah. Coba lagi.')

def pilih_tipe_vila():
    print('\n-- Pilih Tipe Vila --')
    print('1. Reguler')
    print('2. Premium')
    while True:
        pilihan = input('Pilih tipe (1-2) : ').strip()
        if pilihan == '1':
            return 'Reguler'
        elif pilihan == '2':
            return 'Premium'
        else:
            print('[VALIDASI GAGAL] Pilih 1 atau 2 saja.')

def pilih_vila():
    tipe_terpilih = pilih_tipe_vila()
    vila_sesuai_tipe = [v for v in daftar_vila if v.tipe_vila == tipe_terpilih]

    print(f'\n-- Daftar Vila {tipe_terpilih} Tersedia (Bali) --')
    for v in vila_sesuai_tipe:
        v.tampilkan_info()

    while True:
        kode = input('Masukkan kode vila yang dipilih (mis. VL01) : ').strip().upper()
        if not Vila.validasi_kode_vila(kode):
            print("[VALIDASI GAGAL] Format kode vila salah (harus diawali 'VL').")
            continue
        vila_terpilih = next((v for v in vila_sesuai_tipe if v.kode_vila == kode), None)
        if vila_terpilih is None:
            print(f'[VALIDASI GAGAL] Kode vila tidak ditemukan dalam daftar tipe {tipe_terpilih}.')
            continue
        return vila_terpilih

def input_jumlah_malam():
    while True:
        teks = input('Jumlah malam menginap : ').strip()
        if not teks.isdigit() or not Transaksi.validasi_jumlah_malam(int(teks)):
            print('[VALIDASI GAGAL] Jumlah malam harus bilangan bulat >= 1.')
            continue
        return int(teks)

def proses_beri_ulasan_otomatis(transaksi):
    print('\nPembayaran berhasil! Yuk beri ulasan untuk vila ini (ketik 0 pada rating untuk lewati).')
    while True:
        teks_rating = input('Rating (1-5, atau 0 untuk lewati) : ').strip()
        if not teks_rating.isdigit():
            print('[VALIDASI GAGAL] Rating harus angka.')
            continue
        rating = int(teks_rating)
        if rating == 0:
            print('Ulasan dilewati.')
            return
        komentar = input('Komentar : ').strip()
        if not Ulasan.validasi_komentar(komentar):
            print('[VALIDASI GAGAL] Komentar minimal 5 karakter, tidak boleh kosong.')
            continue
        try:
            id_ulasan = f'ULS{Ulasan.total_ulasan + 1:03d}'
            ulasan = Ulasan.buat_dari_transaksi(id_ulasan, transaksi, rating, komentar)
        except ValueError as e:
            print(f'[VALIDASI GAGAL] {e}')
            continue
        if ulasan is None:
            return
        daftar_ulasan.append(ulasan)
        print('\nUlasan berhasil disimpan! Terima kasih.')
        ulasan.tampilkan_ulasan()
        return

def proses_sewa_vila(penyewa):
    vila = pilih_vila()
    jumlah_malam = input_jumlah_malam()
    id_transaksi = f'TRX{Transaksi.total_transaksi + 1:03d}'
    transaksi = Transaksi.buat_transaksi(id_transaksi, penyewa, vila, jumlah_malam)
    if transaksi is None:
        return
    daftar_transaksi.append(transaksi)
    transaksi.hitung_total_bayar()
    while True:
        bayar = input('\nApakah sudah bayar sekarang? (y/n) : ').strip().lower()
        if bayar == 'y':
            transaksi.status_pembayaran = 'Lunas'
            print(f'Status transaksi {transaksi.id_transaksi} -> Lunas')
            proses_beri_ulasan_otomatis(transaksi)
            break
        elif bayar == 'n':
            print(f"Status transaksi {transaksi.id_transaksi} tetap 'Menunggu Pembayaran'")
            break
        else:
            print("[VALIDASI GAGAL] Jawab 'y' atau 'n' saja.")

def lihat_riwayat_saya(penyewa):
    transaksi_saya = [t for t in daftar_transaksi if t.penyewa is penyewa]
    if not transaksi_saya:
        print('\nKamu belum punya transaksi.')
        return
    print(f'\n===== RIWAYAT TRANSAKSI {penyewa.nama.upper()} =====')
    for t in transaksi_saya:
        t.vila.tampilkan_info()
        print(f'  ID Transaksi : {t.id_transaksi} | {t.jumlah_malam} malam | Status: {t.status_pembayaran}')
        print('  ' + '-' * 40)

def bayar_transaksi_tertunda(penyewa):
    transaksi_tertunda = [t for t in daftar_transaksi if t.penyewa is penyewa and t.status_pembayaran == 'Menunggu Pembayaran']
    if not transaksi_tertunda:
        print('\nTidak ada transaksi yang menunggu pembayaran.')
        return

    print('\n===== TRANSAKSI MENUNGGU PEMBAYARAN =====')
    for t in transaksi_tertunda:
        print(f'  {t.id_transaksi} - {t.vila.nama_vila} ({t.jumlah_malam} malam)')

    while True:
        id_pilih = input('Masukkan ID transaksi yang mau dibayar (atau 0 untuk batal) : ').strip().upper()
        if id_pilih == '0':
            return
        transaksi_terpilih = next((t for t in transaksi_tertunda if t.id_transaksi == id_pilih), None)
        if transaksi_terpilih is None:
            print('[VALIDASI GAGAL] ID transaksi tidak ditemukan / bukan milikmu.')
            continue
        break

    transaksi_terpilih.hitung_total_bayar()
    while True:
        konfirmasi = input('\nKonfirmasi pembayaran sekarang? (y/n) : ').strip().lower()
        if konfirmasi == 'y':
            transaksi_terpilih.status_pembayaran = 'Lunas'
            print(f'Status transaksi {transaksi_terpilih.id_transaksi} -> Lunas')
            proses_beri_ulasan_otomatis(transaksi_terpilih)
            return
        elif konfirmasi == 'n':
            print('Pembayaran dibatalkan, status tetap Menunggu Pembayaran.')
            return
        else:
            print("[VALIDASI GAGAL] Jawab 'y' atau 'n' saja.")

def lihat_semua_transaksi():
    if not daftar_transaksi:
        print('\nBelum ada transaksi tercatat.')
        return
    print('\n===== SEMUA TRANSAKSI (ADMIN) =====')
    for t in daftar_transaksi:
        t.penyewa.tampilkan_profil()
        t.vila.tampilkan_info()
        print(f'  ID Transaksi : {t.id_transaksi} | {t.jumlah_malam} malam | Status: {t.status_pembayaran}')
        print('  ' + '-' * 40)

def lihat_semua_ulasan():
    if not daftar_ulasan:
        print('\nBelum ada ulasan yang masuk.')
        return
    print('\n===== SEMUA ULASAN (ADMIN) =====')
    for u in daftar_ulasan:
        u.tampilkan_ulasan()
        print('  ' + '-' * 40)

def admin_ubah_pajak():
    while True:
        teks = input('\nMasukkan persentase pajak baru : ').strip()
        try:
            persen = float(teks)
        except ValueError:
            print('[VALIDASI GAGAL] Masukkan angka.')
            continue
        Vila.ubah_pajak(persen)
        break

def admin_statistik():
    print(f'\nTotal vila terdaftar   : {Vila.total_vila_terdaftar}')
    print(f'Total penyewa terdaftar: {Penyewa.total_penyewa}')
    print(f'Total transaksi        : {Transaksi.total_transaksi}')
    print(f'Total ulasan           : {Ulasan.total_ulasan}')

def menu_penyewa(penyewa):
    while True:
        ada_tertunda = any(t.penyewa is penyewa and t.status_pembayaran == 'Menunggu Pembayaran' for t in daftar_transaksi)

        print(f'\n===== MENU PENYEWA ({penyewa.nama}) =====')
        print('1. Sewa Vila')
        print('2. Riwayat Transaksi Saya')
        opsi_bayar = None
        nomor_berikutnya = 3
        if ada_tertunda:
            opsi_bayar = nomor_berikutnya
            print(f'{opsi_bayar}. Bayar Transaksi Tertunda')
            nomor_berikutnya += 1
        opsi_logout = nomor_berikutnya
        print(f'{opsi_logout}. Logout')

        pilihan = input(f'Pilih menu (1-{opsi_logout}) : ').strip()
        if pilihan == '1':
            proses_sewa_vila(penyewa)
        elif pilihan == '2':
            lihat_riwayat_saya(penyewa)
        elif ada_tertunda and pilihan == str(opsi_bayar):
            bayar_transaksi_tertunda(penyewa)
        elif pilihan == str(opsi_logout):
            print('Logout berhasil.')
            break
        else:
            print(f'[VALIDASI GAGAL] Pilihan menu tidak dikenal, masukkan 1-{opsi_logout}.')

def menu_admin():
    while True:
        print('\n===== MENU ADMIN =====')
        print('1. Lihat Semua Transaksi')
        print('2. Lihat Semua Ulasan')
        print('3. Ubah Pajak Sewa')
        print('4. Statistik Sistem')
        print('5. Logout')
        pilihan = input('Pilih menu (1-5) : ').strip()
        if pilihan == '1':
            lihat_semua_transaksi()
        elif pilihan == '2':
            lihat_semua_ulasan()
        elif pilihan == '3':
            admin_ubah_pajak()
        elif pilihan == '4':
            admin_statistik()
        elif pilihan == '5':
            print('Logout admin berhasil.')
            break
        else:
            print('[VALIDASI GAGAL] Pilihan menu tidak dikenal, masukkan 1-5.')

def main():
    print('=' * 60)
    print(f'Selamat datang di {Vila.nama_perusahaan}')
    print('=' * 60)
    while True:
        print('\n===== MENU AWAL =====')
        print('1. Registrasi Akun Penyewa')
        print('2. Login')
        print('3. Keluar')
        pilihan = input('Pilih menu (1-3) : ').strip()
        if pilihan == '1':
            penyewa = registrasi_penyewa()
            menu_penyewa(penyewa)
        elif pilihan == '2':
            login()
        elif pilihan == '3':
            print('\nTerima kasih telah menggunakan SIREVA. Sampai jumpa!')
            break
        else:
            print('[VALIDASI GAGAL] Pilihan menu tidak dikenal, masukkan 1-3.')
if __name__ == '__main__':
    main()