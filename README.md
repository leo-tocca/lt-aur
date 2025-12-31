# lt-aur - Custom Arch Linux ARM Repository

Repository Arch Linux personalizzato per architettura **aarch64** (ARM64), ottimizzato per Raspberry Pi 4B e EndeavourOS ARM.

## Pacchetti disponibili

Questo repository contiene ~50 pacchetti compilati dall'AUR, tra cui:

- **Desktop apps**: albert, hypnotix, webapp-manager
- **System utilities**: debtap, etherwake, neofetch, powerjoular
- **Themes & icons**: mint-l-theme, mint-l-icons, mint-backgrounds-*
- **Development tools**: openfortigui-git, python packages
- **Hardware support**: aic8800-dkms (WiFi), epsonscan2

[Lista completa pacchetti](packages-list.yaml)

## Installazione

### 1. Importa chiave GPG

```bash
curl -O https://github.com/leo-tocca/lt-aur/raw/main/public-key.asc
sudo pacman-key --add public-key.asc
sudo pacman-key --lsign-key F6C74B48
```

### 2. Aggiungi repository

Edita `/etc/pacman.conf` e aggiungi:

```ini
[lt-aur]
SigLevel = Required TrustedOnly
Server = https://github.com/leo-tocca/lt-aur/releases/latest/download
```

### 3. Aggiorna e installa

```bash
sudo pacman -Sy
sudo pacman -S <nome-pacchetto>
```

## Esempi

```bash
# Installa Albert launcher
sudo pacman -S albert

# Installa tema Mint
sudo pacman -S mint-l-theme mint-l-icons

# Installa utilities
sudo pacman -S neofetch debtap etherwake

# Installa backgrounds
sudo pacman -S mint-backgrounds-wilma
```

## Cerca pacchetti

```bash
pacman -Ss lt-aur/
```

## Architettura supportata

- **aarch64** (ARM 64-bit)

Testato su:
- Raspberry Pi 4B
- EndeavourOS ARM

## Build & Updates

I pacchetti vengono:
- Compilati automaticamente su GitHub Actions con QEMU
- Aggiornati giornalmente dall'AUR
- Firmati con chiave GPG per sicurezza
- Rilasciati tramite GitHub Releases

## Sicurezza

Tutti i pacchetti sono:
- ✅ Firmati con GPG (F6C74B48)
- ✅ Source visibili su GitHub
- ✅ Build automatizzati e riproducibili
- ✅ Verificabili tramite `pacman -Qkk <pacchetto>`

## Contribuire

Richieste per nuovi pacchetti: [apri un issue](https://github.com/leo-tocca/lt-aur/issues)

## Supporto

- Issues: [GitHub Issues](https://github.com/leo-tocca/lt-aur/issues)
- AUR: I PKGBUILD originali sono su [aur.archlinux.org](https://aur.archlinux.org)

## License

I singoli pacchetti mantengono le loro licenze originali.
Build scripts: MIT License

---

**Maintainer**: Leonardo Toccafondi  
**GPG Key**: F6C74B48  
**Fingerprint**: `A170924D350FF4B2E8BFAA162F135E62F6C74B48`
