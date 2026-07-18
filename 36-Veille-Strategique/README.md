# Strategic Watch MVP (Veille Stratégique)

> Automated and structured strategic intelligence system for the MIDGARD ecosystem.

This repository hosts the Minimum Viable Product (MVP) for the Strategic Watch system. It provides a structured methodology, automated file-system surveillance, and a canonical ground-truth knowledge base optimized for Alexandria and Avalon integration.

## 🚀 Quick Start

Ensure you have the required dependencies (`entr`) installed to use the automated watch script.

```bash
# Install dependencies (Ubuntu/Debian)
sudo apt install entr

# Clone the repository
git clone https://github.com/lordmahonheim-bot/MVP-GITHUB.git
cd MVP-GITHUB/36-Veille-Strategique

# Start the file-system watcher
./watch.sh
```

## 📚 Usage & Examples

The system relies on a rigorous structure to maintain canonical truth. It is divided into reference methodologies and data storage directories.

### Directories

- **`Highlights-Outputs/`**: Surface alerts, session summaries, and rapid technological watch data.
- **`Strategic-Outputs/`**: In-depth analytical reports (SWOT, decision support, exhaustive fact-checking).

### File Monitoring

The `watch.sh` script monitors all Markdown files within the directory. When a change is detected, it triggers the synchronization and indexing protocol. By default, it logs the detection, but it can be customized to trigger `rsync` or GitHub commits automatically.

## 🏛️ Architecture & Design Decisions

> [!NOTE]
> This MVP is designed to act as the primary "Ground Truth" for Alexandria and Avalon.

- **Canonical Structure**: Uses a central `INDEX.md` Map of Content (MOC) to link rules and databases.
- **Inverted Pyramid**: Information is structured for immediate legibility by autonomous agents.
- **Automated Observation**: Uses `entr` for highly efficient, lightweight file monitoring instead of polling.
- **Standardized Outputs**: Governed by the `Charte_Veille_Strategique.md` (Strategic Watch Charter) and `La grille de rédaction d'un rapport analytique.md`.

## 🤝 Contribution & Governance

> [!IMPORTANT]
> All strategic data must adhere to the 10 articles of the Strategic Watch Charter.

To contribute to this watch system:
1. Ensure your output aligns with the analytical grid standard.
2. Store rapid insights in `Highlights-Outputs/` and deep research in `Strategic-Outputs/`.
3. Submit changes via PR. The automated watcher will flag modifications for indexing.

For further enhancement proposals, refer to the `Proposition_Amelioration.md` document.
