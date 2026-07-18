# Fedora Software Updater - Help Guide

Welcome to the **Fedora Software Updater** help guide. This application provides a modern, fast, and unified graphical interface to update both system packages and flatpak applications on your Fedora 44 (KDE Plasma Desktop Edition) machine.

---

## 🚀 Getting Started

### How to Launch
1. **Application Launcher (Start Menu)**: Click the Application Launcher icon on your taskbar, type **System Software Updater**, and click the launcher.
2. **Terminal Launcher**: Open a terminal and run the following command:
   ```bash
   python3 /home/pp/.gemini/antigravity/scratch/fedora-software-updater/updater.py
   ```

---

## 🛠️ Main Features

* **Unified Updates**: Aggregates and applies both Fedora system upgrades (`dnf5`) and applications (`flatpak`) in one go.
* **Modern Slate Design**: Features an elegant dark-theme look matching modern desktop environments, built entirely using Python's native Tkinter.
* **Vector Graphics Status**: Resolution-independent custom drawn shields (Success checkmark and Warning indicators) to communicate application status.
* **Real-time Log Terminal**: A live monospace terminal displaying stdout streams of compilation, download, and installation transactions.
* **Dual-Phase Progress Bar**: An intelligent progress estimator that monitors download phases, installation operations, and Flatpak completion status.
* **One-Click Privilege Elevation**: Seamless integration with Polkit (`pkexec`) to prompt for root authorization when installing updates.

---

## 📖 Step-by-Step Usage

### 1. Checking for Updates
Upon opening, the application will automatically start scanning. An active circular loading animation will spin. Under the hood, it queries `dnf5 check-update` and `flatpak remote-ls --updates`.

### 2. Viewing Available Updates
If updates are found:
- The screen will transition to show the total count of packages.
- A list detailing the **Package Name**, **Version**, and **Source** (e.g. `updates`, `fedora`, or `Flathub`) will be populated.
- Scroll through the list using your mouse scroll-wheel or scrollbar.

### 3. Installing Updates
- Click the blue **Install Updates** button.
- You will be prompted with a standard graphical dialog asking for your sudo/root password (this is handled securely by `pkexec` and your system's Polkit authentication agent).
- Enter your password to proceed.

### 4. Monitoring Progress
- The progress bar will fill as downloads and installation tasks complete.
- The log console at the bottom displays real-time lines printed by DNF5 and Flatpak.
- Status notifications like `Processing: 12 of 30 tasks done...` will update dynamically.

### 5. Finalizing Upgrades
- Once finished, a dialog will ask if you want to **Restart** the system (useful if core packages like the Linux Kernel or Systemd were updated).
- You can select **Yes** to reboot or **No** to return to the updater.

---

## ❓ Troubleshooting & FAQs

### Q1: The launcher prompts for root authorization, is this safe?
**Yes.** Standard system packages can only be updated by a root user. The application invokes `pkexec` which safely delegates password checking to the system's PolicyKit daemon. The python script itself does not store or see your password.

### Q2: What happens if I cancel the password prompt?
The application catches the cancellation (Exit code 127) and displays a red warning shield indicating that root permissions are required. You can simply click **Try Again** to prompt the auth dialog again.

### Q3: How do I view detailed error logs?
If an upgrade transaction fails, a red warning screen is shown, and the text box inside the error screen will show the specific error message or exit code returned by DNF5/Flatpak.

### Q4: The app menu shortcut icon is missing or broken.
Make sure the icon is located at `/home/pp/.local/share/icons/fedora-software-updater.png` and that the desktop entry file `/home/pp/.local/share/applications/fedora-software-updater.desktop` points to it.
To fix menu cache, you can run:
```bash
update-desktop-database ~/.local/share/applications
```
