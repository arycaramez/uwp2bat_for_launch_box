# uwp2bat

> A simple and effective tool that converts UWP apps (including Xbox Game Pass games) into `.bat` files, making them easily launchable from [LaunchBox](https://www.launchbox-app.com/).

---

## 🎯 Purpose

Microsoft restricts traditional launching methods for UWP apps, which makes it difficult to integrate them with game managers like LaunchBox. Even LaunchBox's built-in Xbox/Microsoft Store import tool often fails to detect or launch Game Pass titles correctly.

**`uwp2bat` was created to solve this problem** by generating `.bat` files that launch UWP apps via the shell, allowing seamless integration into LaunchBox like any other game or emulator.

---

## 🛠️ Features

- 🔍 Lists all installed UWP applications (including Xbox Game Pass titles).
- ✅ Allows selecting multiple apps using checkboxes.
- 📝 Enables editing the desired `.bat` filenames before creation.
- 📁 Saves the `.bat` files into a user-defined folder.
- 💾 Remembers the last used folder for convenience.

---

## 🚀 How It Works

The tool uses the following PowerShell command to list all UWP apps:
```powershell
Get-StartApps | ForEach-Object {"$($_.Name)`t$($_.AppID)"}
```

Then it generates `.bat` files using this format:
```bat
explorer.exe shell:AppsFolder\<AppID>
```

This command launches the UWP app using the same mechanism as the Windows Start Menu.

---

## 📋 Requirements

- Python 3.8+
- [wxPython](https://wxpython.org/) (`pip install wxPython`)
- Windows 10 or 11

---

## 📦 Installation

1. Clone this repository

2. Install dependencies:
   ```bash
   pip install wxPython
   ```

3. Run the application:
   ```bash
   python uwp2bat.py
   ```

---

## 📷 Screenshots (optional)

_Add screenshots of the interface here to help users understand the workflow._

---

## ✅ How to Use

1. Launch `uwp2bat.py`.
2. Use the search bar to find UWP apps or games.
3. Check the boxes for the apps you want to convert.
4. Click **"Generate Executables .BAT"**.
5. Choose a destination folder.
6. Optionally rename the `.bat` files in the edit screen.
7. The generated `.bat` files can now be used directly or imported into LaunchBox.

---

## 🎮 Using with LaunchBox

In LaunchBox:
- Go to **Tools → Import → ROM Files**.
- Point to the generated `.bat` files.
- Choose the appropriate platform (e.g., "Xbox Game Pass").
- Complete the import as usual.

---

## 🧪 Tested On

- Windows 11 (22H2)
- LaunchBox 13.10+
- Xbox Game Pass for PC

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributions

Feel free to open an issue or submit a pull request if you want to contribute or improve the project!

---

## 📫 Contact

Developed by **Ary Guilherme Pires Caramez**  
[LinkedIn](https://www.linkedin.com/in/aryguilherme/) • [GitHub](https://github.com/arycaramez)
