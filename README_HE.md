# Automation Framework Exercise

תשתית אוטומציה חזקה וסקיילבילית שנבנתה באמצעות **Python**, **Playwright**, ו-**Pytest**. תוכננה ליציבות, גמישות וקלות תחזוקה תוך שימוש בתבנית העיצוב Page Object Model (POM).

> [!NOTE]
> **סטטוס דרישות**: ✅ **100% בוצע**. פרויקט זה עומד בכל הדרישות שהוגדרו, כולל שימוש ב-Playwright, Python, דוחות Allure, תמיכה ב-Selenium Grid/Moon, תכנון OOP/POM, בדיקות מונחות נתונים (Data-Driven), והרצה מקבילית.

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
├── config/                 # קבצי קונפיגורציה
│   ├── config.yaml         # הגדרות ראשיות (Base URL, timeouts)
│   ├── browsers.yaml       # הגדרת מטריצת דפדפנים
│   └── reporting.yaml      # הגדרות דיווח
├── core/                   # ליבת התשתית
│   ├── driver_factory.py   # יצירת דפדפן וחיבור מרוחק
│   ├── base_page.py        # מחלקת עמוד בסיסית (POM)
│   └── locator_strategy.py # לוגיקת איתור חכמה (Fallback)
├── pages/                  # אובייקטי עמוד (POM)
├── tests/                  # סקריפטים של בדיקות
├── test_data/              # קבצי נתונים לבדיקות
│   ├── login.yaml          # דוגמאות YAML
│   ├── users.csv           # דוגמאות CSV
│   └── search.json         # דוגמאות JSON
├── utils/                  # כלי עזר (DataLoader, etc.)
├── reporting/              # שכבת הדיווח (Abstraction Layer)
├── reports/                # דוחות ריצה (עם חותמת זמן)
├── logs/                   # לוגים של הריצה
├── conftest.py             # Pytest fixtures and hooks
├── pytest.ini              # הגדרות Pytest
└── requirements.txt        # תלויות הפרויקט
```

## 🌐 מטריצת דפדפנים וארכיטקטורה (Browser Matrix)

התשתית משתמשת ב-**מטריצת דפדפנים דינמית** המוגדרת בקובץ `config/browsers.yaml`. הבדיקות מתוזמנות אוטומטית (בזמן ה-Collection) לרוץ על כל הדפדפנים המוגדרים.

### ארכיטקטורה
```
YAML Matrix (browsers.yaml) → pytest_generate_tests() → Test Parametrization → Isolated Drivers
```

### קונפיגורציה (`config/browsers.yaml`)
```yaml
matrix:
  - name: chrome_latest
    browserName: chromium
    browserVersion: latest
    headless: false

  - name: firefox_latest
    browserName: firefox
    browserVersion: latest
```

## ☁️ הרצה מרוחקת (Remote Execution - Grid / Moon)

הרץ בדיקות באופן שקוף על דפדפנים מקומיים או על Grid מרוחק (Selenium Grid 4, Moon, BrowserStack וכו').

### ארכיטקטורה
ה-`DriverFactory` ממפה אוטומטית את פרופילי הדפדפן ל-W3C Capabilities ומתחבר דרך CDP או WebDriver API.

### אופן השימוש
**שיטה 1: פרמטרים ב-CLI**
```bash
pytest --remote --remote-url="http://localhost:4444/wd/hub"
```

**שיטה 2: קונפיגורציה**
הגדר `remote: true` בפרופילים הרצויים בקובץ `config/browsers.yaml`.

### הקמת Docker (דוגמה)
הרצת Moon (Selenium Grid קל משקל):
```bash
docker run -d -p 4444:4444 aerokube/moon:latest
```

## 💾 בדיקות מונחות נתונים (Data-Driven Testing)

הפרדת לוגיקת הבדיקה מהנתונים. תמיכה ב-**YAML**, **JSON**, ו-**CSV**.

### דוגמת שימוש
```python
from utils.data_loader import load_test_data

@pytest.mark.parametrize("data", load_test_data("test_data/login.yaml"))
def test_login(driver, data):
    page.login(data["username"], data["password"])
    assert page.is_logged_in()
```

### פורמטים נתמכים
*   **YAML**: מומלץ לנתונים מובנים ומורכבים.
*   **JSON**: מתאים למבני נתונים היררכיים.
*   **CSV**: מצוין לטבלאות נתונים שטוחות וגדולות (שורת הכותרת הופכת למפתחות).

## 🎯 איתור אלמנטים חכם (Smart Locators)

התשתית משתמשת במנגנון גיבוי (fallback) חזק לזיהוי אלמנטים. ניתן להגדיר מספר לוקייטורים לכל אלמנט; אם הראשון נכשל, התשתית מנסה אוטומטית את הבא בתור.

### אופן השימוש
```python
# In Page Object
SEARCH_INPUT = [
    {'type': 'id', 'value': 'search_query_top'},          # 1. נסה לפי ID
    {'type': 'css', 'value': '#search_query_top'},        # 2. נסה לפי CSS
    {'type': 'xpath', 'value': '//input[@name="search"]'} # 3. נסה לפי XPath
]

# In Test/Page Method
self.type(self.SEARCH_INPUT, "Laptop", "Search Field")
```
*   **Fallback אוטומטי**: מנסה את הלוקייטורים באופן סדרתי.
*   **לוגים**: מתעד איזה לוקייטור הצליח ואיזה נכשל.
*   **כישלון**: מצלם מסך (Screenshot) אם כל הלוקייטורים נכשלו.

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
    playwright install
    ```

## 🏃 הרצת בדיקות (Running Tests)

### 1. הרצה מקומית (ברירת מחדל)
הרצת כל הבדיקות על דפדפן ברירת המחדל.
```bash
pytest
```

### 2. הרצה במקביל
הרצת בדיקות במקביל לקיצור זמן הריצה.
```bash
pytest -n auto             # זיהוי אוטומטי של מספר המעבדים
pytest -n 4                # הרצה עם 4 תהליכים (workers)
```

### 3. הרצה על דפדפן ספציפי
הרצת בדיקות על פרופיל דפדפן ספציפי מהמטריצה.
```bash
pytest --browser=chrome_latest
pytest --browser=firefox_latest
```

### 4. הרצה מרוחקת (Remote)
```bash
pytest --remote --remote-url="http://localhost:4444/wd/hub"
```

## 📊 דוחות (Reporting)

הפרויקט משתמש ב-**Allure Reports**.

1.  **הרצת בדיקות** (התוצאות נשמרות ב-`reports/<timestamp>/allure-results`).
2.  **יצירה וצפייה בדוח**:
    ```bash
    # צפייה ישירה
    allure serve reports/latest/allure-results
    ```

### דיווח מתקדם (Advanced Reporting)
ניתן להוסיף לוגים וצילומי מסך מותאמים אישית באמצעות ה-`ReportingManager`:
```python
from reporting.manager import ReportingManager
ReportingManager.reporter().log_step("Custom step info")
ReportingManager.reporter().attach_screenshot("Evidence", "/path/to/img.png")
```

## ❓ פתרון תקלות (Troubleshooting)

| תקלה | פתרון |
|-------|----------|
| **הבדיקות לא רצות על כל הדפדפנים** | וודא שקובץ `browsers.yaml` מכיל סקציית `matrix` תקינה. |
| **כישלון בהתחברות ל-Grid** | בדוק אם ה-Container של Docker רץ (`docker ps`) ופורט 4444 פתוח. |
| **שגיאה בטעינת נתונים (Data Loader)** | וודא שהקובץ קיים בתיקיית `test_data/` ושהתחביר שלו תקין (YAML/JSON). |
| **פקודת Allure לא נמצאה** | התקן את כלי ה-Commandline של Allure והוסף אותו ל-PATH. |

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
