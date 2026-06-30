# Data Permissions

تطبيق Frappe/ERPNext لتقييد الوصول إلى البيانات بناءً على حقول مرجعية تأتي من التهيئات، مثل الفرع، مركز التكلفة، المستودع، الإدارة، المسمى الوظيفي، والشركة.

الفكرة الأساسية: إذا كان هناك حقل Link يأخذ قيمه من DocType تهيئة مثل `Branch`، فالنظام يستطيع تطبيق صلاحية البيانات عليه أينما ظهر في شاشات النظام.

## المفهوم

بدلاً من تقييد أي حقل عشوائي، يعتمد التطبيق على أبعاد بيانات واضحة:

```text
Branch
Cost Center
Warehouse
Department
Designation
Company
```

كل Dimension يحدد:

```text
Source DocType  = مصدر القيم، مثل Branch
Detected Fields = كل الحقول في النظام التي تشير إلى هذا المصدر
```

مثال:

```text
Dimension: Branch
Source DocType: Branch
Detected Fields:
- Employee.branch
- Sales Invoice.branch
- Purchase Invoice.branch
```

بعد ذلك تمنح المستخدم صلاحية على القيم نفسها:

```text
User: ahmed@example.com
Dimension: Branch
Allowed Values:
- Baghdad: View, Add, Edit
- Basra: View only
```

## الشاشات

### Data Permission Dimension

هذه شاشة تعريف أبعاد صلاحيات البيانات. منها تحدد القيم التي تظهر في حقل `Dimension` داخل شاشة الصلاحيات.

أهم الحقول:

```text
Dimension          اسم البعد، مثل Branch
Source DocType     مصدر القيم، مثل Branch
Default Field Name اسم حقل احتياطي، مثل branch
Detected Fields    الشاشات والحقول التي سيتم تطبيق القيد عليها
Enabled            تفعيل أو إخفاء هذا البعد
```

زر `Discover Fields` يبحث تلقائياً عن كل حقول Link التي تأخذ قيمها من `Source DocType`.

### Data Permission

هذه شاشة منح الصلاحيات للمستخدم أو مجموعة المستخدمين.

أهم الحقول:

```text
User / User Group
Dimension
Permission Details
```

عند اختيار Dimension، تظهر كل القيم من Source DocType في الجدول، ثم تحدد:

```text
View
Add
Edit
Delete
```

## هيكل التطبيق

```text
data_access/
├── hooks.py
├── permissions.py
├── install.py
├── modules.txt
├── config/
│   ├── desktop.py
│   └── data_permission_dimensions.py
└── data_permissions/
    └── doctype/
        ├── data_permission/
        ├── data_permission_detail/
        ├── data_permission_dimension/
        └── data_permission_dimension_target/
```

اسم التطبيق البرمجي بقي `data_access` حتى لا ينكسر التثبيت، لكن اسم الـ Module والشاشات أصبح `Data Permissions`.

## التثبيت

```bash
bench get-app https://github.com/arcchatgpt94/data-access-permissions.git
bench --site your-site.local install-app data_access
bench --site your-site.local migrate
bench build --app data_access
bench restart
```

## التحديث

```bash
cd ~/frappe-bench/apps/data_access
git pull
cd ~/frappe-bench
bench --site your-site.local migrate
bench --site your-site.local clear-cache
bench build --app data_access
bench restart
```

## حدود مهمة

الإصدار الحالي يطبق القيود على الحقول الموجودة مباشرة في DocType الرئيسي. دعم الجداول الفرعية مثل `Sales Invoice Item.warehouse` أو `Journal Entry Account.cost_center` يحتاج مرحلة إضافية لأن فلترة القوائم عبر child tables تتطلب شروط SQL مختلفة.
