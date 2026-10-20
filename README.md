# 🌍 PamsBeyond: Intelligent All-in-One Travel & Trip Planning Workspace

[![Streamlit App](https://img.shields.io/badge/Live%20App-Streamlit-ff4b4b?logo=streamlit&logoColor=white)](https://pamsbeyond.streamlit.app)
[![GitHub License](https://img.shields.io/badge/license-see%20repository-lightgrey)](LICENSE)
[![Product Hunt](https://img.shields.io/badge/Product%20Hunt-Support%20PamsBeyond-da552f?logo=producthunt&logoColor=white)](https://www.producthunt.com/)

**PamsBeyond** is an intelligent, all-in-one travel assistance platform engineered to eliminate tedious logistics and border friction. Built with Python and Streamlit, the platform harmonizes AI-guided assistance, algorithmic travel planning tools, trusted service integrations, affiliate travel partners, and access to professional human support in one seamless workspace.

Forget scattered browser tabs. PamsBeyond lets you architect, calculate, track, and export your entire global itinerary from a single interactive interface.

## 🚀 We’re Live on Product Hunt

PamsBeyond is featured on Product Hunt. If the platform helps you plan your next journey, please support us with an upvote and share your feedback:

👉 **[Support PamsBeyond on Product Hunt](https://www.producthunt.com/)**

## ✨ Key Capabilities

| Core Module | Highlighted Features |
| :--- | :--- |
| **🤖 AI & Human Curation** | Combines AI-guided assistance with practical human travel insight and professional support. |
| **🧭 Comprehensive Search** | Explore visa requirements, flight options, hotels, airport transfers, local transport, and destination guidance. |
| **🧮 Multi-City Calculator** | Build multi-city routes, select custom transit options, and estimate food, lodging, transport, and other trip costs. |
| **📊 Financial Guardrails** | Use interactive Plotly budget charts, emergency-buffer tiers, and built-in currency conversion estimates. |
| **💼 Workspace & Utilities** | Track packing progress, save trip notes, export JSON backups, and restore a previous planning session. |
| **📄 Portfolio Engine** | Generate a downloadable PDF travel portfolio containing routes, budgets, checklists, and trip notes. |
| **🔗 Affiliate Travel Partners** | Access helpful partner services for flights, disruption support, hotels, tours, activities, airport transfers, and local rides. |

## 🚀 Streamlit Community Cloud Deployment

1. Upload `app.py` and `requirements.txt` to your repository root.
2. Deploy the repository directly from the **Streamlit Community Cloud Dashboard**.
3. **No External API Keys Required:** The application operates completely self-contained using integrated algorithmic estimation models to prevent external dependency failures or API downtime crashes.

### Local Setup

```bash
git clone https://github.com/Pamsbeyond/Pamsbeyond.git
cd Pamsbeyond
pip install -r requirements.txt
streamlit run app.py
```

## 🛂 Visa Requirements Hub

The app includes a local visa lookup section that reads `passport-index-tidy.csv` from the same folder as `app.py`. To enable the lookup, add a dataset with these columns:

```text
Passport,Destination,Requirement
```

The lookup supports statuses such as `visa free`, `e-visa`, `visa on arrival`, `VOA`, `ETA`, and `visa required`. Always confirm current rules with official embassy or immigration sources before traveling.

## 🛠️ Tech Stack & Architecture

- **Application framework:** [Streamlit](https://streamlit.io)
- **Programming language:** [Python](https://www.python.org)
- **Data analysis and calculations:** [Pandas](https://pandas.pydata.org)
- **Interactive data visualizations:** [Plotly Express](https://plotly.com/python/plotly-express/)
- **PDF document generation:** [ReportLab](https://www.reportlab.com)
- **Data portability:** Structured JSON serialization for plan backup and restore
- **Runtime hardening:** Embedded page lookups tolerate Streamlit-rendered planner fields that live outside the HTML component.
- **Travel integrations:** Affiliate travel services and local assistance links

## 🤝 Human Support

PamsBeyond combines intelligent automation with access to human travel support. Travelers can request guidance for visas, documents, bookings, itinerary decisions, and special travel needs when they want a more personal level of assistance.

## ⚠️ Important Notice

PamsBeyond is a planning and discovery tool. Travel prices, schedules, availability, visa requirements, and entry rules can change. Confirm final details with airlines, hotels, official government sources, and service providers before making decisions or payments.
