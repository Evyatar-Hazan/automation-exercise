# Automation Framework Exercise

תשתית אוטומציה חזקה וסקיילבילית שנבנתה באמצעות **Python**, **Playwright**, ו-**Pytest**. תוכננה ליציבות, גמישות וקלות תחזוקה תוך שימוש בתבנית העיצוב Page Object Model (POM).

## 🚀 תכונות מרכזיות (Key Features)

*   **טכנולוגיות מודרניות**: Python 3.10+, Playwright, Pytest.
*   **Page Object Model (POM)**: רכיבים מודולריים וניתנים לשימוש חוזר.
*   **Dynamic Browser Matrix**: הרצת בדיקות על מספר דפדפנים (Chrome, Firefox, Edge, WebKit) וגרסאות (latest, specific) ללא שינוי קוד הבדיקה.
*   **Data-Driven Testing**: טעינת נתוני בדיקה מקבצים חיצוניים בפורמט YAML, JSON ו-CSV.
*   **Remote Execution**: תמיכה מלאה ב-Selenium Grid, Moon, או הרצה ב-Docker דרך פרוטוקול CDP.
*   **Parallel Execution**: הרצה מהירה במקביל באמצעות `pytest-xdist`.
*   **Robust Reporting**: אינטגרציה עם **Allure Reports** הכוללת צילומי מסך, לוגים וניתוח כישלונות.
*   **Smart Locators**: אסטרטגיית איתור אלמנטים מתקדמת עם מנגנוני גיבוי (fallback).
*   **Configuration Management**: ניהול קונפיגורציה מרכזי באמצעות קבצי YAML.

## 🏗️ מבנה הפרויקט (Project Structure)

```
automation-exercise/
├── config/                 # קבצי קונפיגורציה (config.yaml, browsers.yaml)
├── core/                   # ליבת התשתית (DriverFactory, BasePage, BaseTest)
├── pages/                  # אובייקטי עמוד (POM)
├── tests/                  # סקריפטים של בדיקות
├── test_data/              # קבצי נתונים לבדיקות (yaml, json, csv)
├── utils/                  # כלי עזר (DataLoader, etc.)
├── reporting/              # שכבת הדיווח
├── reports/                # דוחות ריצה
├── logs/                   # לוגים של הריצה
├── conftest.py             # Pytest fixtures and hooks
├── pytest.ini              # הגדרות Pytest
└── requirements.txt        # תלויות הפרויקט
```

## 📋 דרישות קדם (Prerequisites)

*   **Python 3.10+** מותקן.
*   **Java (JDK 8+)**: נדרש עבור יצירת דוחות Allure.
*   **Allure Commandline**: מותקן ומוגדר ב-System PATH.

## ⚙️ התקנה (Installation)

1.  **שכפול המאגר (Clone)**:
    ```bash
    git clone <repository_url>
    cd automation-exercise
    ```

2.  **יצירה והפעלה של סביבה וירטואלית** (מומלץ):
    ```bash
    python -m venv venv
    source venv/bin/activate  # ב-Windows: venv\Scripts\activate
    ```

3.  **התקנת תלויות (Dependencies)**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **התקנת דפדפני Playwright**:
    ```bash
    playwright install
    ```

## 🏃 הרצת בדיקות (Running Tests)

התשתית תומכת במספר מצבי הרצה המתאימים לפיתוח מקומי, CI/CD וסביבות Grid.

### 1. הרצה מקומית (Local Execution)
הרצת כל הבדיקות על דפדפן ברירת המחדל (מוגדר ב-`config/browsers.yaml`).
```bash
pytest
```

### 2. הרצה במקביל (Parallel Execution)
הרצת בדיקות במקביל לקיצור זמן הריצה (דורש `pytest-xdist`).
```bash
pytest -n auto             # זיהוי אוטומטי של מספר המעבדים
pytest -n 4                # הרצה עם 4 תהליכים (workers)
```

### 3. הרצה על דפדפן ספציפי
הרצת בדיקות על פרופיל דפדפן ספציפי המוגדר ב-`config/browsers.yaml`.
```bash
pytest --browser=chrome_latest
pytest --browser=firefox_latest
pytest --browser=edge_latest
```

### 4. הרצה מרוחקת (Remote / Grid Execution)
הרצת בדיקות על Selenium Grid או Moon מרוחק.
```bash
# שימוש בפרמטרים ב-CLI
pytest --remote --remote-url="http://localhost:4444/wd/hub"

# שימוש ב-Marker בקוד
# @pytest.mark.remote(url="http://grid-box:4444")
```
*הערה: וודא ששרת ה-Grid/Moon פעיל ונגיש.*

### 5. הרצה לפי תגיות (Tagged Execution)
הרצת בדיקות ספציפיות על בסיס Markers (מוגדרים ב-`pytest.ini`).
```bash
pytest -m smoke            # הרצת בדיקות עשן
pytest -m regression       # הרצת רגרסיה מלאה
pytest -m ui               # הרצת בדיקות UI
```

## 📊 דוחות (Reporting)

הפרויקט משתמש ב-**Allure Reports** להצגה ויזואלית עשירה של תוצאות הבדיקה.

1.  **הרצת בדיקות** (התוצאות נשמרות ב-`reports/<timestamp>/allure-results`):
    ```bash
    pytest
    ```

2.  **יצירה וצפייה בדוח**:
    ```bash
    # צפייה ישירה
    allure serve reports/latest/allure-results

    # או יצירת דוח סטטי
    allure generate reports/latest/allure-results -o reports/allure-report --clean
    allure open reports/allure-report
    ```

## 🔧 קונפיגורציה (Configuration)

*   **הגדרות גלובליות**: `config/config.yaml` (Base URL, Timeouts, Retries, Reporting).
*   **פרופילי דפדפן**: `config/browsers.yaml` (הגדרת דפדפנים, גרסאות, רזולוציות, capabilities).

## 🤝 תרומה לפרויקט (Contribution)

1.  בצע Fork למאגר.
2.  צור Feature Branch (`git checkout -b feature/AmazingFeature`).
3.  בצע Commit לשינויים (`git commit -m 'Add some AmazingFeature'`).
4.  בצע Push ל-Branch (`git push origin feature/AmazingFeature`).
5.  פתח Pull Request.

## 📄 רישיון (License)

מופץ תחת רישיון MIT. ראה קובץ `LICENSE` למידע נוסף.

## 📞 יצירת קשר

מנהל הפרויקט - אביתר חזן
