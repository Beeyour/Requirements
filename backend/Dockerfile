# 1. اختيار نسخة بايثون
FROM python:3.11-slim

# 2. تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# 3. نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. نسخ بقية ملفات المشروع
COPY . .

# 5. الأمر الذي يشغل التطبيق
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]