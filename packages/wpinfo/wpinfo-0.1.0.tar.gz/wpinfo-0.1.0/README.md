# 📰 WPInfo

**WPInfo** is a lightweight Python library that extracts publicly available information from any WordPress website.

It fetches metadata such as site title, theme name, plugin hints, RSS feed, sitemap, WordPress version (if visible), and more — all using clean and simple Python code.

---

## 🚀 Features

- Get site title and meta description
- Detect WordPress version (if disclosed)
- Extract active theme name
- Detect plugin paths
- Find RSS feed, sitemap, and robots.txt URLs
- Clean, simple interface with no dependencies other than `requests` and `beautifulsoup4`

---

## 📦 Installation

You can install from PyPI:

```bash
pip install wpinfo
```

---

## 🧪 Example Usage

```python
from wpinfo import WPInfo

site = WPInfo("https://example.wordpress.com")
info = site.get_info()

for key, value in info.items():
    print(f"{key.capitalize()}: {value}")
```

---

## 🧠 Output Example

```text
Title: Example WordPress Site
Meta_description: This is an example WordPress website.
Wordpress_version: WordPress 6.3.1
Theme: twentytwentythree
Plugins: contact-form-7, jetpack
Rss_feed: https://example.com/feed/
Sitemap: https://example.com/sitemap.xml
Robots_txt: https://example.com/robots.txt
```

---

## 🛠 Requirements

- Python 3.7+
- `requests`
- `beautifulsoup4`

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 📃 License

This project is licensed under the [MIT License](LICENSE).

---

## ✨ Author

Made with ❤️ by **Deadpool2k**  
GitHub: [@Deadpool2000](https://github.com/Deadpool2000)

---

## 📬 Contributions & Feedback

Pull requests, feature ideas, and bug reports are welcome.  
Feel free to open an [issue](https://github.com/Deadpool2000/wpinfo/issues) or submit a PR.
