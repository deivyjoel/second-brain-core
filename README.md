# 🧠 SecondBrain - Personal Knowledge Manager

**SecondBrain** is a desktop application designed to capture notes, organize thoughts, and manage personal knowledge in a structured way, eliminating mental and digital clutter.

---

## ✨ Features

- **📝 Markdown Support:** Take notes with integrated basic Markdown formatting.
- **⏱️ Time Tracking:** Each note includes a linked timer to track how much time you spend on each idea or task.
- **📂 Topic-Based Organization:** A hierarchical management system where **Topics** act as containers (folders) for notes and images.
- **🖼️ Media Management:** Integrated image import and export directly into your workflow.
- **📊 Smart Analytics:** View basic statistics for both individual notes and entire topics.


---

## 📸 Interface Preview

### 1. Markdown Editor & Rendering
The main interface allows for plain text note editing with immediate **Preview Mode** visualization. The left panel manages data persistence through a hierarchical topic structure.
![Markdown Editor](https://github.com/deivyjoel/second-brain-core/blob/cb8b788728884f6c5cc96b45250729877812851b/preview_markdown.JPG)

### 2. Media Management
Dedicated module for organizing visual resources. It supports dynamic previewing with **zoom** controls and exposes file metadata such as capture date and original format.
![Image Viewer](https://github.com/deivyjoel/second-brain-core/blob/cb8b788728884f6c5cc96b45250729877812851b/preview_image.JPG)

### 3. Note Analytics
Calculation engine for individual productivity metrics. It tracks precise data on active editing time, word count, work sessions, and the **lexical diversity** of the content.
![Note Analytics](https://github.com/deivyjoel/second-brain-core/blob/cb8b788728884f6c5cc96b45250729877812851b/preview_analytics_note.JPG)

### 4. Topic-Level Aggregated Metrics
Unlike individual analysis, this component consolidates information from all elements within a category. It evaluates the **total effort** per knowledge area, accounting for accumulated time and entity density (notes and images).
![Topic Analytics](https://github.com/deivyjoel/second-brain-core/blob/cb8b788728884f6c5cc96b45250729877812851b/preview_analyticas_themes.JPG)

---

## 🛠️ Tech Stack

The project was built following **clean architecture** principles and separation of concerns:

* **Language:** Python
* **GUI:** Tkinter
* **Database:** SQLAlchemy + SQLite
* **Data Validation:** Pydantic
* **Image Processing:** Pillow (PIL)

---

## 🚀 Installation & Running

1. **Clone the repository:**
   git clone https://github.com/deivyjoel/second-brain-core.git

2. **Run the application:**
   python -m main

---

## 💡 Motivation

This project was born out of a personal need: **to organize the chaos**. My desktop and my ideas were scattered, and I needed a tool to centralize my thoughts in one place.

Beyond solving a real productivity problem, **SecondBrain** is a conscious exercise in software engineering, where I applied best practices in architecture, component decoupling, and maintainable code.

---

Developed with ❤️ by [Deivy Joel](https://github.com/deivyjoel)
