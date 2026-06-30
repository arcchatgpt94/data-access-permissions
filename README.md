# Data Access Permissions

تطبيق Frappe/ERPNext لإضافة قيود وصول على مستوى الصفوف بناءً على قيم مثل الفرع، مركز التكلفة، الحساب، أو المستودع.

## ما الذي تغيّر في هذه النسخة

- تنظيف بنية المشروع وحذف مخلفات التوليد.
- إصلاح `modules.txt` ليطابق بنية تطبيقات Frappe.
- تسجيل `permission_query_conditions` و `doc_events` مباشرة من `hooks.py`.
- إصلاح فحص دور `System Manager`.
- جعل الصلاحيات آمنة افتراضياً: وجود سجل صلاحية بلا قيم مسموحة يعني المنع، لا السماح.
- تطبيق صلاحيات العرض والإضافة والتعديل والحذف بدلاً من استخدام العرض فقط.
- استخدام escaping لقيم SQL داخل شروط القراءة.
- إصلاح النصوص المشوهة واستبدالها برسائل واضحة قابلة للترجمة.

## هيكل التطبيق

الهيكل مرتب كالتالي حتى يطابق توقعات Frappe:

```text
data_access_app_improved/
├── setup.py
├── MANIFEST.in
├── README.md
└── data_access/
    ├── hooks.py
    ├── permissions.py
    ├── modules.txt
    ├── config/
    │   ├── desktop.py
    │   └── data_access_types.py
    └── data_access/
        └── doctype/
            ├── data_access_permission/
            └── data_access_permission_detail/
```

في هذا الهيكل:

- `data_access/hooks.py` هو ملف hooks الخاص بالتطبيق.
- `data_access/permissions.py` يحتوي محرك الصلاحيات.
- `data_access/data_access/doctype` يحتوي DocTypes الخاصة بـ module اسمه `Data Access`.

## طريقة التثبيت

انسخ مجلد التطبيق كاملاً إلى مجلد `apps` داخل bench، وليس مجلد `data_access` وحده:

```bash
cd /path/to/frappe-bench
cp -r /path/to/data_access_app_improved apps/data_access
bench --site your-site.local install-app data_access
bench --site your-site.local migrate
bench build --app data_access
bench restart
```

## طريقة الاستخدام

1. افتح DocType باسم `Data Access Permission`.
2. اختر مستخدماً أو مجموعة مستخدمين، وليس الاثنين معاً.
3. اختر نوع القيد مثل `Branch` أو `Cost Center`.
4. اضغط `Tools > Load Values`.
5. فعّل الصلاحيات المطلوبة لكل قيمة: `View`, `Add`, `Edit`, `Delete`.

إذا لم يكن للمستخدم أي سجل صلاحيات مفعّل لنوع معين، فلن يتم تقييده بهذا النوع. إذا كان لديه سجل مفعّل لكن لا توجد أي قيمة مسموحة، فسيتم منعه من الوصول لذلك النوع.

## أنواع القيود

تُدار الأنواع من:

```text
data_access/config/data_access_types.py
```

مثال لإضافة نوع جديد:

```python
{
    "name": "Territory",
    "label": "المناطق",
    "label_en": "Territory",
    "doctype": "Territory",
    "field_name": "territory",
    "allow_blank": False,
    "apply_to": ["Sales Invoice", "Sales Order", "Lead"],
}
```

## حدود مهمة قبل الإنتاج

هذا التطبيق يقيّد الحقول الموجودة مباشرة في DocType الرئيسي فقط. كثير من مستندات ERPNext تضع الحسابات، المستودعات، ومراكز التكلفة داخل child tables، وهذه تحتاج دعماً إضافياً باستعلامات مخصصة أو منطق تحقق على الجداول الفرعية.

يُنصح باختباره على بيئة تجريبية مع مستخدمين حقيقيين وسيناريوهات قراءة/إضافة/تعديل/حذف قبل تثبيته على بيئة إنتاج.
