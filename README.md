# SIREVA (Sistem Reservasi Penyewaan Villa)

---

## 1. Penjelasan Program

SIREVA adalah sistem reservasi penyewaan vila di kawasan Bali yang memisahkan dua peran pengguna: Penyewa dan Admin.

Alur singkat:
1. Penyewa registrasi akun (nama, no HP, NIK, username, password) sebelum bisa menyewa vila.
2. Penyewa login — sistem otomatis mendeteksi apakah kredensial yang dimasukkan milik Admin atau Penyewa, tanpa menu login terpisah.
3. Penyewa memilih tipe vila (Reguler / Premium), lalu memilih vila dari daftar sesuai tipe tersebut (semua berlokasi di Bali).
4. Sistem menghitung total biaya (subtotal + pajak), lalu penyewa bisa langsung bayar atau menunda pembayaran.
5. Jika belum bayar, penyewa bisa melunasinya nanti lewat menu "Bayar Transaksi Tertunda" (menu ini hanya muncul kalau memang ada transaksi yang menunggu pembayaran).
6. Begitu status transaksi menjadi Lunas, form ulasan langsung muncul otomatis (boleh dilewati).
7. Admin login pakai kredensial tetap (`onall` / `23`) tanpa perlu registrasi, dan punya menu berbeda: lihat semua transaksi, lihat semua ulasan, ubah persentase pajak, serta lihat statistik sistem.

---

## 2. Struktur Class

Program terdiri dari 4 class yang saling berinteraksi (tanpa inheritance/pewarisan):

### `Vila`
Merepresentasikan data vila yang disewakan.
- Atribut kelas: `nama_perusahaan`, `total_vila_terdaftar`, `pajak_persen`
- Atribut instance: `kode_vila`, `nama_vila`, `lokasi` (public), `_catatan_internal` (protected), `__harga_per_malam`, `__tipe_vila` (private, lewat `@property`)
- Instance method: `tampilkan_info()`
- Class method: `dari_dict()` (factory), `ubah_pajak()`
- Static method: `validasi_kode_vila()`

### `Penyewa`
Merepresentasikan akun penyewa (data diri + kredensial login).
- Atribut kelas: `total_penyewa`, `jenis_keanggotaan_default`, `minimal_umur_sewa`
- Atribut instance: `nama`, `no_hp`, `username` (public), `_jenis_keanggotaan` (protected), `__nik`, `__password` (private, lewat `@property`)
- Instance method: `cek_password()`, `tampilkan_profil()`
- Class method: `dari_dict()` (factory)
- Static method: `validasi_no_hp()`

### `Transaksi`
Menghubungkan objek `Penyewa` dan `Vila` dalam satu transaksi sewa.
- Atribut kelas: `total_transaksi`, `denda_per_hari_telat`, `status_valid`
- Atribut instance: `id_transaksi`, `penyewa`, `vila`, `jumlah_malam` (public), `_catatan_admin` (protected), `__status_pembayaran` (private, lewat `@property`)
- Instance method: `hitung_total_bayar()`
- Class method: `buat_transaksi()` (factory + validasi)
- Static method: `validasi_jumlah_malam()`

### `Ulasan`
Menyimpan ulasan penyewa terhadap vila, terhubung ke objek `Transaksi` yang sudah lunas.
- Atribut kelas: `total_ulasan`, `rating_min`, `rating_max`
- Atribut instance: `id_ulasan`, `transaksi`, `komentar` (public), `__rating` (private, lewat `@property`)
- Instance method: `tampilkan_ulasan()`
- Class method: `buat_dari_transaksi()` (factory dengan aturan bisnis: transaksi harus Lunas)
- Static method: `validasi_komentar()`

---

## 3. Panduan Pengujian

### Cara Menjalankan
```bash
python3 sireva_posttest_interaktif.py
```

### Kredensial Admin (tetap, tanpa registrasi)
- Username: `onall`
- Password: `23`

### Skenario Pengujian yang Disarankan

1. Registrasi & validasi data
   - Pilih `1. Registrasi Akun Penyewa`
   - Coba masukkan NIK kurang dari 16 digit / password kurang dari 4 karakter → sistem harus menolak (`raise ValueError`) dan minta input ulang
   - Lanjutkan dengan data valid sampai akun berhasil dibuat

2. Sewa vila (pembayaran langsung)
   - Pilih `1. Sewa Vila` → pilih tipe (Reguler/Premium) → pilih salah satu vila → isi jumlah malam
   - Coba isi jumlah malam dengan angka negatif/huruf → sistem harus menolak
   - Saat ditanya "Apakah sudah bayar sekarang?", jawab `y` → status berubah jadi Lunas → form ulasan otomatis muncul

3. Sewa vila (pembayaran ditunda)
   - Ulangi sewa vila, tapi jawab `n` saat ditanya pembayaran
   - Kembali ke Menu Penyewa → perhatikan menu "Bayar Transaksi Tertunda" kini muncul otomatis
   - Pilih menu tersebut, masukkan ID transaksi, konfirmasi bayar → status berubah jadi Lunas → ulasan otomatis muncul lagi

4. Cek riwayat transaksi
   - Pilih `2. Riwayat Transaksi Saya` untuk melihat semua transaksi milik akun yang sedang login

5. Login sebagai Admin
   - Logout dari akun Penyewa
   - Login dengan username `onall` dan password `23`
   - Coba semua menu admin: lihat semua transaksi, lihat semua ulasan, ubah pajak sewa, dan lihat statistik sistem

6. Uji login gabungan
   - Dari Menu Awal, pilih `2. Login`, lalu coba masukkan username/password yang salah → sistem menolak dan meminta input ulang
   - Coba login dengan akun Penyewa yang sudah didaftarkan → berhasil masuk ke Menu Penyewa
