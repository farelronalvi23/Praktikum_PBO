from abc import ABC, abstractmethod

ADMIN_USERNAME = 'onall'
ADMIN_PASSWORD = '23'


class Fasilitas:
    def __init__(self, nama_fasilitas, deskripsi):
        self.nama_fasilitas = nama_fasilitas
        self.deskripsi = deskripsi

    def __str__(self):
        return f'{self.nama_fasilitas} ({self.deskripsi})'


class KodePromo:
    kode_tersedia = {'SIREVA10': 10, 'LIBURAN20': 20, 'BALIHEMAT15': 15}

    def __init__(self, kode):
        self.kode = kode.strip().upper()

    def valid(self):
        return self.kode in KodePromo.kode_tersedia

    def ambil_diskon_persen(self):
        return KodePromo.kode_tersedia.get(self.kode, 0)


class Kwitansi:
    total_kwitansi = 0

    def __init__(self, id_kwitansi, nama_penyewa, nama_vila, total_bayar):
        self.id_kwitansi = id_kwitansi
        self.nama_penyewa = nama_penyewa
        self.nama_vila = nama_vila
        self.total_bayar = total_bayar
        Kwitansi.total_kwitansi += 1

    def tampilkan(self):
        print(f'  === KWITANSI {self.id_kwitansi} ===')
        print(f'  Penyewa : {self.nama_penyewa}')
        print(f'  Vila    : {self.nama_vila}')
        print(f'  Total   : Rp{self.total_bayar:,.0f}')


wifi = Fasilitas('WiFi', 'Internet cepat')
ac = Fasilitas('AC', 'Pendingin ruangan')
dapur = Fasilitas('Dapur', 'Dapur lengkap')
kolam_renang = Fasilitas('Kolam Renang', 'Kolam renang pribadi')
spa = Fasilitas('Spa', 'Layanan spa in-villa')
bar = Fasilitas('Mini Bar', 'Mini bar pribadi')


class Vila:
    nama_perusahaan = 'SIREVA (Sistem Reservasi Penyewaan Villa)'
    total_vila_terdaftar = 0
    pajak_persen = 10

    def __init__(self, kode_vila, nama_vila, lokasi, harga_per_malam):
        self.kode_vila = kode_vila
        self.nama_vila = nama_vila
        self.lokasi = lokasi
        self._harga_dasar = 0
        self.harga_dasar = harga_per_malam
        self._daftar_fasilitas = []
        self.__id_sistem = f'SYS-{Vila.total_vila_terdaftar + 1:04d}'
        Vila.total_vila_terdaftar += 1
        for f in self.fasilitas_default():
            self.tambah_fasilitas(f)

    @property
    def harga_dasar(self):
        return self._harga_dasar

    @harga_dasar.setter
    def harga_dasar(self, nilai):
        if not isinstance(nilai, (int, float)) or nilai <= 0:
            raise ValueError(f"Harga vila tidak boleh 0/negatif. Input '{nilai}' ditolak.")
        self._harga_dasar = nilai

    def fasilitas_default(self):
        return []

    def tambah_fasilitas(self, fasilitas):
        self._daftar_fasilitas.append(fasilitas)

    def hitung_harga_sewa(self, jumlah_malam):
        return self._harga_dasar * jumlah_malam

    def terapkan_diskon_otomatis(self, jumlah_malam):
        return False

    def tampilkan_info(self):
        print(f'  [{self.kode_vila}] ({type(self).__name__}) {self.nama_vila} - {self.lokasi} | Rp{self._harga_dasar:,.0f}/malam')
        if self._daftar_fasilitas:
            daftar = ', '.join(str(f) for f in self._daftar_fasilitas)
            print(f'    Fasilitas: {daftar}')

    def __str__(self):
        return f'{self.nama_vila} ({type(self).__name__}) - Rp{self._harga_dasar:,.0f}/malam'

    def __eq__(self, other):
        if not isinstance(other, Vila):
            return NotImplemented
        return self.kode_vila == other.kode_vila

    def __lt__(self, other):
        return self._harga_dasar < other._harga_dasar

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


class VilaReguler(Vila):
    def __init__(self, kode_vila, nama_vila, lokasi, harga_per_malam, kapasitas_tamu):
        self.kapasitas_tamu = kapasitas_tamu
        super().__init__(kode_vila, nama_vila, lokasi, harga_per_malam)

    def fasilitas_default(self):
        return [wifi, ac, dapur]

    def terapkan_diskon_otomatis(self, jumlah_malam):
        if jumlah_malam >= 5:
            self._harga_dasar = self._harga_dasar * 0.9
            return True
        return False

    @classmethod
    def dari_dict(cls, data):
        return cls(data['kode_vila'], data['nama_vila'], data['lokasi'], data['harga_per_malam'], data['kapasitas_tamu'])


class VilaPremium(Vila):
    def __init__(self, kode_vila, nama_vila, lokasi, harga_per_malam, fasilitas_eksklusif):
        self.fasilitas_eksklusif = fasilitas_eksklusif
        super().__init__(kode_vila, nama_vila, lokasi, harga_per_malam)

    def fasilitas_default(self):
        return [wifi, ac, kolam_renang, spa, bar]

    def hitung_harga_sewa(self, jumlah_malam):
        harga_dasar_total = super().hitung_harga_sewa(jumlah_malam)
        biaya_layanan = harga_dasar_total * 0.15
        return harga_dasar_total + biaya_layanan

    @classmethod
    def dari_dict(cls, data):
        return cls(data['kode_vila'], data['nama_vila'], data['lokasi'], data['harga_per_malam'], data['fasilitas_eksklusif'])


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
    def dari_dict(cls, data):
        return cls(data['nama'], data['no_hp'], data['nik'], data['username'], data['password'])

    @staticmethod
    def validasi_no_hp(no_hp):
        return isinstance(no_hp, str) and no_hp.startswith('08') and 10 <= len(no_hp) <= 13


class MetodePembayaran(ABC):
    total_pembayaran_diproses = 0

    def __init__(self, nama_metode):
        self.nama_metode = nama_metode
        self._biaya_admin = 0

    @abstractmethod
    def validasi(self, jumlah):
        pass

    @abstractmethod
    def proses(self, jumlah):
        pass

    def jalankan(self, jumlah):
        print(f'\n  --- Memproses Pembayaran via {self.nama_metode} ---')
        if self.validasi(jumlah):
            hasil = self.proses(jumlah)
            MetodePembayaran.total_pembayaran_diproses += 1
            return hasil
        print(f'  Pembayaran via {self.nama_metode} ditolak (validasi gagal).')
        return False


class PembayaranTunai(MetodePembayaran):
    def __init__(self, uang_diterima):
        super().__init__('Tunai')
        self.uang_diterima = uang_diterima

    def validasi(self, jumlah):
        return self.uang_diterima >= jumlah

    def proses(self, jumlah):
        kembalian = self.uang_diterima - jumlah
        print(f'  Pembayaran tunai berhasil. Kembalian: Rp{kembalian:,.0f}')
        return True


class PembayaranTransfer(MetodePembayaran):
    def __init__(self, nomor_rekening_tujuan):
        super().__init__('Transfer Bank')
        self._biaya_admin = 6500
        self.nomor_rekening_tujuan = nomor_rekening_tujuan

    def validasi(self, jumlah):
        return jumlah > 0

    def proses(self, jumlah):
        total = jumlah + self._biaya_admin
        print(f'  Transfer ke rekening {self.nomor_rekening_tujuan} berhasil.')
        print(f'  Total dibayar: Rp{total:,.0f} (termasuk biaya admin Rp{self._biaya_admin:,.0f})')
        return True


class PembayaranEWallet(MetodePembayaran):
    def __init__(self, nomor_ewallet):
        super().__init__('E-Wallet')
        self._biaya_admin = 1500
        self.nomor_ewallet = nomor_ewallet

    def validasi(self, jumlah):
        return jumlah > 0

    def proses(self, jumlah):
        total = jumlah + self._biaya_admin
        print(f'  Pembayaran E-Wallet dari {self.nomor_ewallet} berhasil.')
        print(f'  Total dibayar: Rp{total:,.0f} (termasuk biaya admin Rp{self._biaya_admin:,.0f})')
        return True


class NotifikasiEmail:
    def __init__(self, alamat_email):
        self.alamat_email = alamat_email

    def kirim(self, pesan):
        print(f'  [EMAIL -> {self.alamat_email}] {pesan}')


class NotifikasiSMS:
    def __init__(self, nomor_hp):
        self.nomor_hp = nomor_hp

    def kirim(self, pesan):
        print(f'  [SMS -> {self.nomor_hp}] {pesan}')


def kirim_notifikasi_konfirmasi(daftar_kanal, pesan):
    for kanal in daftar_kanal:
        kanal.kirim(pesan)


class Transaksi:
    total_transaksi = 0
    denda_per_hari_telat = 50000
    status_valid = ('Menunggu Pembayaran', 'Lunas', 'Dibatalkan')

    def __init__(self, id_transaksi, penyewa, vila, jumlah_malam):
        self.id_transaksi = id_transaksi
        self.penyewa = penyewa
        self.vila = vila
        self.jumlah_malam = jumlah_malam
        self._catatan_admin = ''
        self._diskon_persen_aktif = 0
        self.__status_pembayaran = 'Menunggu Pembayaran'
        self._kwitansi = None
        Transaksi.total_transaksi += 1

    @property
    def status_pembayaran(self):
        return self.__status_pembayaran

    @status_pembayaran.setter
    def status_pembayaran(self, status_baru):
        if status_baru not in Transaksi.status_valid:
            raise ValueError(f"Status '{status_baru}' tidak dikenal. Pilihan: {Transaksi.status_valid}")
        self.__status_pembayaran = status_baru

    def terapkan_promo(self, kode_promo):
        if not kode_promo.valid():
            print(f'Kode promo {kode_promo.kode} tidak valid.')
            return 0
        self._diskon_persen_aktif = kode_promo.ambil_diskon_persen()
        print(f'Kode promo {kode_promo.kode} berhasil diterapkan, diskon {self._diskon_persen_aktif}%')
        return self._diskon_persen_aktif

    def hitung_total_bayar(self):
        subtotal = self.vila.hitung_harga_sewa(self.jumlah_malam)
        potongan = subtotal * (self._diskon_persen_aktif / 100)
        setelah_diskon = subtotal - potongan
        pajak = setelah_diskon * (Vila.pajak_persen / 100)
        total = setelah_diskon + pajak
        print(f'\n  --- Rincian Transaksi {self.id_transaksi} ---')
        print(f'  Penyewa   : {self.penyewa.nama}')
        print(f'  Vila      : {self.vila}')
        print(f'  Lama Sewa : {self.jumlah_malam} malam')
        print(f'  Subtotal  : Rp{subtotal:,.0f}')
        if self._diskon_persen_aktif > 0:
            print(f'  Diskon    : -Rp{potongan:,.0f} ({self._diskon_persen_aktif}%)')
        print(f'  Pajak     : Rp{pajak:,.0f} ({Vila.pajak_persen}%)')
        print(f'  Total     : Rp{total:,.0f}')
        print(f'  Status    : {self.status_pembayaran}')
        return total

    def buat_kwitansi(self, total_bayar):
        id_kwitansi = f'KWT-{self.id_transaksi}'
        self._kwitansi = Kwitansi(id_kwitansi, self.penyewa.nama, self.vila.nama_vila, total_bayar)
        return self._kwitansi

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

    def __init__(self, id_ulasan, transaksi, rating, komentar):
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
        if not isinstance(nilai, int) or not (Ulasan.rating_min <= nilai <= Ulasan.rating_max):
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
    VilaReguler.dari_dict({'kode_vila': 'VL01', 'nama_vila': 'Vila Ubud Asri', 'lokasi': 'Ubud, Bali', 'harga_per_malam': 1200000, 'kapasitas_tamu': 4}),
    VilaReguler.dari_dict({'kode_vila': 'VL02', 'nama_vila': 'Vila Kuta Nyaman', 'lokasi': 'Kuta, Bali', 'harga_per_malam': 1500000, 'kapasitas_tamu': 6}),
    VilaReguler.dari_dict({'kode_vila': 'VL03', 'nama_vila': 'Vila Canggu Sederhana', 'lokasi': 'Canggu, Bali', 'harga_per_malam': 1300000, 'kapasitas_tamu': 4}),
    VilaPremium.dari_dict({'kode_vila': 'VL04', 'nama_vila': 'Vila Seminyak Elite', 'lokasi': 'Seminyak, Bali', 'harga_per_malam': 3500000, 'fasilitas_eksklusif': 'Private Chef'}),
    VilaPremium.dari_dict({'kode_vila': 'VL05', 'nama_vila': 'Vila Uluwatu Cliffside', 'lokasi': 'Uluwatu, Bali', 'harga_per_malam': 4000000, 'fasilitas_eksklusif': 'Infinity Pool'}),
    VilaPremium.dari_dict({'kode_vila': 'VL06', 'nama_vila': 'Vila Nusa Dua Luxe', 'lokasi': 'Nusa Dua, Bali', 'harga_per_malam': 3800000, 'fasilitas_eksklusif': 'Butler 24 Jam'}),
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
        if any(p.username == username for p in daftar_penyewa):
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
    kelas_terpilih = VilaReguler if tipe_terpilih == 'Reguler' else VilaPremium
    vila_sesuai_tipe = [v for v in daftar_vila if isinstance(v, kelas_terpilih)]

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


def tanya_promo(transaksi):
    pakai_promo = input('Punya kode promo? (y/n) : ').strip().lower()
    if pakai_promo == 'y':
        kode = input('Masukkan kode promo : ').strip()
        promo = KodePromo(kode)
        transaksi.terapkan_promo(promo)


def pilih_metode_pembayaran():
    print('\n-- Pilih Metode Pembayaran --')
    print('1. Tunai')
    print('2. Transfer Bank')
    print('3. E-Wallet')
    print('4. Belum, tunda pembayaran')
    while True:
        pilihan = input('Pilih metode (1-4) : ').strip()
        if pilihan == '1':
            while True:
                teks = input('Uang yang diberikan : ').strip()
                try:
                    uang = float(teks)
                except ValueError:
                    print('[VALIDASI GAGAL] Masukkan angka.')
                    continue
                return PembayaranTunai(uang)
        elif pilihan == '2':
            rekening = input('Nomor rekening tujuan : ').strip()
            return PembayaranTransfer(rekening)
        elif pilihan == '3':
            nomor_ewallet = input('Nomor E-Wallet : ').strip()
            return PembayaranEWallet(nomor_ewallet)
        elif pilihan == '4':
            return None
        else:
            print('[VALIDASI GAGAL] Pilih 1-4 saja.')


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


def selesaikan_pembayaran(transaksi, total):
    metode = pilih_metode_pembayaran()
    if metode is None:
        print(f"Status transaksi {transaksi.id_transaksi} tetap 'Menunggu Pembayaran'")
        return

    berhasil = metode.jalankan(total)
    if not berhasil:
        print(f"Status transaksi {transaksi.id_transaksi} tetap 'Menunggu Pembayaran' (pembayaran gagal)")
        return

    transaksi.status_pembayaran = 'Lunas'
    print(f'Status transaksi {transaksi.id_transaksi} -> Lunas')
    kwitansi = transaksi.buat_kwitansi(total)
    kwitansi.tampilkan()

    kanal_notifikasi = [
        NotifikasiEmail(f'{transaksi.penyewa.username}@mail.com'),
        NotifikasiSMS(transaksi.penyewa.no_hp),
    ]
    pesan = f'Pembayaran {transaksi.id_transaksi} sebesar Rp{total:,.0f} via {metode.nama_metode} telah berhasil.'
    print('\nMengirim notifikasi konfirmasi (duck typing: Email & SMS, tidak sekerabat):')
    kirim_notifikasi_konfirmasi(kanal_notifikasi, pesan)

    proses_beri_ulasan_otomatis(transaksi)


def proses_sewa_vila(penyewa):
    vila = pilih_vila()
    jumlah_malam = input_jumlah_malam()

    diskon_diberikan = vila.terapkan_diskon_otomatis(jumlah_malam)
    if diskon_diberikan:
        print(f'Selamat! {type(vila).__name__} ini dapat diskon long-stay 10% karena nginap >= 5 malam.')

    id_transaksi = f'TRX{Transaksi.total_transaksi + 1:03d}'
    transaksi = Transaksi.buat_transaksi(id_transaksi, penyewa, vila, jumlah_malam)
    if transaksi is None:
        return

    daftar_transaksi.append(transaksi)
    tanya_promo(transaksi)
    total = transaksi.hitung_total_bayar()
    selesaikan_pembayaran(transaksi, total)


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

    tanya_promo(transaksi_terpilih)
    total = transaksi_terpilih.hitung_total_bayar()
    selesaikan_pembayaran(transaksi_terpilih, total)


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


def admin_urutkan_vila():
    print('\n===== DAFTAR VILA TERURUT (TERMURAH -> TERMAHAL) =====')
    print('(Operator Overloading: sorted() memakai __lt__, ditampilkan lewat __str__)')
    for v in sorted(daftar_vila):
        print(f'  {v}')


def admin_statistik():
    print(f'\nTotal vila terdaftar       : {Vila.total_vila_terdaftar}')
    print(f'Total penyewa terdaftar    : {Penyewa.total_penyewa}')
    print(f'Total transaksi            : {Transaksi.total_transaksi}')
    print(f'Total ulasan               : {Ulasan.total_ulasan}')
    print(f'Total kwitansi dicetak     : {Kwitansi.total_kwitansi}')
    print(f'Total pembayaran diproses  : {MetodePembayaran.total_pembayaran_diproses}')


def demo_konsep_oop():
    print('\n===== DEMO KONSEP OOP (Abstraksi, Polimorfisme, Duck Typing, Operator Overloading) =====')

    print('\n-- 1. Abstraksi: abstract class MetodePembayaran tidak bisa diinstansiasi langsung --')
    try:
        metode = MetodePembayaran('Testing')
    except TypeError as e:
        print(f'Error: {e}')

    print('\n-- 2. Polimorfisme via Pewarisan (satu loop, objek beda subclass Vila) --')
    for v in daftar_vila:
        print(f'  {v.nama_vila} ({type(v).__name__}): Rp{v.hitung_harga_sewa(1):,.0f} / 1 malam')

    print('\n-- 3. Duck Typing (NotifikasiEmail & NotifikasiSMS, tidak berelasi pewarisan) --')
    kanal_demo = [NotifikasiEmail('demo@mail.com'), NotifikasiSMS('081200000000')]
    kirim_notifikasi_konfirmasi(kanal_demo, 'Ini pesan demo duck typing.')

    print('\n-- 4. Operator Overloading pada class Vila (__str__, __eq__, __lt__) --')
    v1, v2 = daftar_vila[0], daftar_vila[3]
    print(f'  str(v1)    : {v1}')
    print(f'  v1 == v2   : {v1 == v2}')
    print(f'  v1 == v1   : {v1 == v1}')
    print(f'  v1 < v2    : {v1 < v2}')
    print('  Urutan vila termurah -> termahal (sorted):')
    for v in sorted(daftar_vila):
        print(f'    {v}')

    print('\n-- 5. Subclass konkret dari abstract class MetodePembayaran --')
    tunai = PembayaranTunai(2_000_000)
    tunai.jalankan(1_500_000)
    transfer = PembayaranTransfer('8800112233')
    transfer.jalankan(1_500_000)

    print('\n===== DEMO SELESAI =====')


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
        print('4. Urutkan & Bandingkan Vila')
        print('5. Statistik Sistem')
        print('6. Logout')
        pilihan = input('Pilih menu (1-6) : ').strip()

        if pilihan == '1':
            lihat_semua_transaksi()
        elif pilihan == '2':
            lihat_semua_ulasan()
        elif pilihan == '3':
            admin_ubah_pajak()
        elif pilihan == '4':
            admin_urutkan_vila()
        elif pilihan == '5':
            admin_statistik()
        elif pilihan == '6':
            print('Logout admin berhasil.')
            break
        else:
            print('[VALIDASI GAGAL] Pilihan menu tidak dikenal, masukkan 1-6.')


def main():
    print('=' * 60)
    print(f'Selamat datang di {Vila.nama_perusahaan}')
    print('=' * 60)

    while True:
        print('\n===== MENU AWAL =====')
        print('1. Registrasi Akun Penyewa')
        print('2. Login')
        print('3. Demo Konsep OOP (Abstraksi, Polimorfisme, dll   )')
        print('4. Keluar')
        pilihan = input('Pilih menu (1-4) : ').strip()

        if pilihan == '1':
            penyewa = registrasi_penyewa()
            menu_penyewa(penyewa)
        elif pilihan == '2':
            login()
        elif pilihan == '3':
            demo_konsep_oop()
        elif pilihan == '4':
            print('\nTerima kasih telah menggunakan SIREVA. Sampai jumpa!')
            break
        else:
            print('[VALIDASI GAGAL] Pilihan menu tidak dikenal, masukkan 1-4.')


if __name__ == '__main__':
    main()