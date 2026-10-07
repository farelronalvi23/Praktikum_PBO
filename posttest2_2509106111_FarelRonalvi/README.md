# SIREVA (Sistem Reservasi Penyewaan Villa)

---

## 1. Penjelasan Program

SIREVA merupakan sistem reservasi penyewaan vila yang berlokasi di kawasan Bali, dengan dua peran pengguna yang terpisah, yaitu Penyewa dan Admin.

Alur kerja program adalah sebagai berikut:
1. Penyewa diwajibkan melakukan registrasi akun (nama, nomor HP, NIK, username, password) terlebih dahulu sebelum dapat menyewa vila.
2. Penyewa melakukan login melalui satu pintu masuk yang sama. Sistem akan mendeteksi secara otomatis apakah kredensial yang dimasukkan merupakan milik Admin atau Penyewa, tanpa menu login yang terpisah.
3. Penyewa memilih tipe vila (Reguler atau Premium), kemudian memilih salah satu vila dari daftar sesuai tipe yang dipilih. Seluruh vila yang tersedia berlokasi di Bali dan masing-masing memiliki daftar fasilitas.
4. Penyewa dapat memasukkan kode promo secara opsional sebelum sistem menghitung total biaya (subtotal dikurangi diskon, ditambah pajak).
5. Penyewa dapat melakukan pembayaran secara langsung atau menundanya.
6. Apabila pembayaran ditunda, penyewa dapat melunasinya di kemudian waktu melalui menu "Bayar Transaksi Tertunda". Menu ini hanya akan muncul apabila terdapat transaksi yang berstatus menunggu pembayaran.
7. Setelah status transaksi berubah menjadi Lunas, sistem akan mencetak kwitansi dan menampilkan formulir ulasan secara otomatis (pengisian ulasan bersifat opsional).
8. Admin melakukan login menggunakan kredensial tetap (`onall` / `23`) tanpa perlu melakukan registrasi, dan memiliki menu yang berbeda, yaitu melihat seluruh transaksi, melihat seluruh ulasan, mengubah persentase pajak, serta melihat statistik sistem.

---

## 2. Struktur Class

### Inheritance: `Vila` (superclass) menurunkan `VilaReguler` dan `VilaPremium` (subclass)

`Vila` berperan sebagai superclass yang menyimpan data umum dari suatu vila.
- Atribut kelas: `nama_perusahaan`, `total_vila_terdaftar`, `pajak_persen`
- Atribut instance: `kode_vila`, `nama_vila`, `lokasi` (bersifat public), `_harga_dasar`, `_daftar_fasilitas` (bersifat protected, dapat diakses oleh subclass), `__id_sistem` (bersifat private, hanya digunakan di dalam class `Vila`)
- Instance method: `tambah_fasilitas()`, `hitung_harga_sewa()`, `tampilkan_info()`
- Class method: `ubah_pajak()`
- Static method: `validasi_kode_vila()`

`VilaReguler(Vila)` merupakan subclass yang menambahkan atribut unik `kapasitas_tamu` serta method `beri_diskon_long_stay()`, yang mengakses atribut protected `_harga_dasar` milik superclass secara langsung untuk memberikan diskon sebesar 10% apabila masa menginap mencapai lima malam atau lebih. Konstruktor pada subclass ini memanggil `super().__init__(...)`.

`VilaPremium(Vila)` merupakan subclass yang menambahkan atribut unik `fasilitas_eksklusif`, serta melakukan override terhadap method `hitung_harga_sewa()` milik superclass dengan menambahkan biaya layanan premium sebesar 15% di atas harga dasar. Konstruktor pada subclass ini juga memanggil `super().__init__(...)`.

### `Penyewa`
Merepresentasikan akun penyewa yang terdiri atas data diri dan kredensial login.
- Atribut kelas: `total_penyewa`, `jenis_keanggotaan_default`, `minimal_umur_sewa`
- Atribut instance: `nama`, `no_hp`, `username` (bersifat public), `_jenis_keanggotaan` (bersifat protected), `__nik`, `__password` (bersifat private, diakses melalui `@property`)
- Instance method: `cek_password()`, `tampilkan_profil()`
- Class method: `dari_dict()` (factory method)
- Static method: `validasi_no_hp()`

### `Transaksi`
Menghubungkan objek `Penyewa` dan objek `Vila` dalam satu transaksi penyewaan.
- Atribut kelas: `total_transaksi`, `denda_per_hari_telat`, `status_valid`
- Atribut instance: `id_transaksi`, `penyewa`, `vila`, `jumlah_malam` (bersifat public), `_catatan_admin`, `_diskon_persen_aktif`, `_kwitansi` (bersifat protected), `__status_pembayaran` (bersifat private, diakses melalui `@property`)
- Instance method: `terapkan_promo()`, `hitung_total_bayar()`, `buat_kwitansi()`
- Class method: `buat_transaksi()` (factory method disertai validasi)
- Static method: `validasi_jumlah_malam()`

### `Ulasan`
Menyimpan ulasan yang diberikan penyewa terhadap vila, yang terhubung dengan objek `Transaksi` yang telah berstatus lunas.
- Atribut kelas: `total_ulasan`, `rating_min`, `rating_max`
- Atribut instance: `id_ulasan`, `transaksi`, `komentar` (bersifat public), `__rating` (bersifat private, diakses melalui `@property`)
- Instance method: `tampilkan_ulasan()`
- Class method: `buat_dari_transaksi()` (factory method dengan aturan bisnis bahwa transaksi terkait harus berstatus lunas)
- Static method: `validasi_komentar()`

### `Fasilitas`, `KodePromo`, dan `Kwitansi`
Tiga class pendukung yang masing-masing merepresentasikan satu bentuk relasi UML, sebagaimana dijelaskan pada bagian berikutnya.

---

## 3. Relasi UML yang Diterapkan

### Asosiasi ("menggunakan")
Method `Transaksi.terapkan_promo(kode_promo)` menerima objek `KodePromo` sebagai parameter. Objek tersebut hanya digunakan sesaat untuk mengambil nilai persentase diskon, kemudian dilepaskan kembali. Objek `KodePromo` tidak disimpan sebagai atribut permanen pada `Transaksi`; yang disimpan hanyalah nilai `_diskon_persen_aktif`.

### Agregasi ("memiliki")
Class `Vila` memiliki atribut `_daftar_fasilitas` yang menampung sejumlah objek `Fasilitas`. Objek-objek `Fasilitas` dibuat secara terpisah di luar class `Vila`, yaitu pada proses seeding data, kemudian didaftarkan melalui method `tambah_fasilitas()`. Objek `Fasilitas` tetap dapat berdiri sendiri sekalipun objek `Vila` yang menggunakannya dihapus.

### Komposisi ("terdiri dari")
Method `Transaksi.buat_kwitansi()` membuat objek `Kwitansi` secara langsung di dalam method tersebut. Objek `Kwitansi` tidak memiliki arti di luar konteks transaksi yang membentuknya.

### Inheritance / Pewarisan ("adalah jenis dari")
Class `VilaReguler` dan `VilaPremium` merupakan jenis dari class `Vila`, sebagaimana telah dijelaskan pada bagian sebelumnya. Relasi ini merupakan satu-satunya relasi yang menghubungkan antarkelas, berbeda dengan tiga relasi lainnya yang menghubungkan antarobjek.

---

## 4. Panduan Pengujian

### Cara Menjalankan Program
```bash
python3 sireva_posttest_interaktif.py
```

### Kredensial Admin (bersifat tetap, tanpa registrasi)
- Username: `onall`
- Password: `23`

### Kode Promo yang Tersedia untuk Pengujian
- `SIREVA10` memberikan diskon 10%
- `LIBURAN20` memberikan diskon 20%
- `BALIHEMAT15` memberikan diskon 15%

### Skenario Pengujian yang Disarankan

1. Registrasi dan validasi data
   - Pilih menu `1. Registrasi Akun Penyewa`
   - Cobalah memasukkan NIK kurang dari 16 digit, atau password kurang dari 4 karakter, untuk memastikan sistem menolak input tersebut (`raise ValueError`) dan meminta pengisian ulang
   - Lanjutkan dengan data yang valid hingga akun berhasil dibuat

2. Penyewaan Vila Reguler dengan diskon long-stay
   - Pilih menu `1. Sewa Vila`, kemudian pilih tipe `Reguler`, pilih salah satu vila, dan masukkan jumlah malam sebanyak 5 malam atau lebih
   - Perhatikan pesan diskon long-stay sebesar 10% yang muncul secara otomatis, yang membuktikan bahwa method `beri_diskon_long_stay()` berhasil mengakses atribut protected `_harga_dasar`

3. Penyewaan Vila Premium dan pengecekan override harga
   - Ulangi proses penyewaan, kali ini dengan memilih tipe `Premium`
   - Bandingkan subtotal yang ditampilkan dengan hasil perkalian `harga_per_malam` dan `jumlah_malam`. Subtotal pada vila Premium akan lebih besar karena terdapat tambahan 15% biaya layanan dari method yang telah di-override

4. Pengujian kode promo
   - Pada saat ditanya "Punya kode promo?", jawab `y` kemudian masukkan salah satu kode promo di atas, dan pastikan sistem menampilkan potongan diskon pada rincian transaksi
   - Cobalah pula memasukkan kode promo yang tidak valid untuk memastikan sistem menolaknya tanpa memberikan diskon

5. Pembayaran langsung dan pembayaran yang ditunda
   - Jawab `y` pada saat ditanya status pembayaran untuk menguji status berubah menjadi Lunas, kwitansi tercetak, dan formulir ulasan muncul secara otomatis
   - Pada percobaan lain, jawab `n`, kemudian kembali ke Menu Penyewa dan perhatikan menu "Bayar Transaksi Tertunda" yang muncul secara otomatis. Selesaikan pembayaran melalui menu tersebut

6. Pemeriksaan riwayat transaksi
   - Pilih menu `2. Riwayat Transaksi Saya` untuk melihat seluruh transaksi milik akun yang sedang digunakan

7. Login sebagai Admin
   - Lakukan logout dari akun Penyewa
   - Login menggunakan username `onall` dan password `23`
   - Ujilah seluruh menu Admin, yaitu melihat seluruh transaksi, melihat seluruh ulasan, mengubah pajak sewa, serta melihat statistik sistem (termasuk jumlah kwitansi yang telah tercetak)

8. Pengujian login gabungan
   - Pada Menu Awal, pilih menu `2. Login`, kemudian cobalah memasukkan username atau password yang salah untuk memastikan sistem menolak dan meminta pengisian ulang
   - Lakukan login kembali menggunakan akun Penyewa yang telah terdaftar untuk memastikan proses login berhasil masuk ke Menu Penyewa
