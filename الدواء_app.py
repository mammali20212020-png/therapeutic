import flet as ft
import datetime
import json
import os

# --- المنطق البرمجي المطور (Core Logic) ---
class MedicationManager:
    def __init__(self):
        self.filename = "medications.json"
        self.medications = self.load_data()

    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for med in data:
                    med['البداية'] = datetime.date.fromisoformat(med['البداية'])
                    med['النهاية'] = datetime.date.fromisoformat(med['النهاية'])
                return data
            except:
                return []
        return []

    def save_data(self):
        data_to_save = []
        for med in self.medications:
            med_copy = med.copy()
            med_copy['البداية'] = med_copy['البداية'].isoformat()
            med_copy['النهاية'] = med_copy['النهاية'].isoformat()
            data_to_save.append(med_copy)
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

    def add_medicine(self, name, dose_times, duration_days, price):
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=int(duration_days))
        medicine = {
            "الاسم": name,
            "المواعيد": dose_times,
            "البداية": start_date,
            "النهاية": end_date,
            "المدة": int(duration_days),
            "السعر": float(price)
        }
        self.medications.append(medicine)
        self.save_data()

    def delete_medicine(self, med):
        self.medications.remove(med)
        self.save_data()

    def get_total_cost(self):
        return sum(med['السعر'] for med in self.medications)

# --- واجهة المستخدم المطورة (UI) ---
def main(page: ft.Page):
    page.title = "صحتك أفضل"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.rtl = True
    page.window_width = 450
    page.window_height = 800
    page.scroll = "auto"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE, font_family="Arial")

    manager = MedicationManager()

    # عناصر الإدخال
    name_field = ft.TextField(label="اسم الدواء", border_radius=10)
    times_field = ft.TextField(label="المواعيد (مثلاً: 08:00, 20:00)", border_radius=10)
    duration_field = ft.TextField(label="المدة باليوم", keyboard_type=ft.KeyboardType.NUMBER, border_radius=10)
    price_field = ft.TextField(label="السعر الإجمالي", keyboard_type=ft.KeyboardType.NUMBER, border_radius=10)
    list_container = ft.Column(spacing=10)
    total_cost_text = ft.Text("إجمالي التكلفة: 0 جنيه مصري", size=18, weight="bold", color=ft.Colors.BLUE_GREY)

    def update_list():
        list_container.controls.clear()
        today = datetime.date.today()
        for med in manager.medications:
            remaining = (med['النهاية'] - today).days
            progress = max(0, remaining) / med['المدة'] if med['المدة'] > 0 else 0
            status_color = ft.Colors.GREEN if remaining > 0 else ft.Colors.RED_400
            card = ft.Card(
                elevation=2,
                content=ft.Container(
                    padding=15,
                    content=ft.Column([
                        ft.Row([
                            ft.Row([ft.Text("💊", size=20, color=ft.Colors.BLUE), ft.Text(med['الاسم'], size=18, weight="bold")]),
                            ft.TextButton("حذف", on_click=lambda e, m=med: delete_action(m), style=ft.ButtonStyle(color=ft.Colors.RED))
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(f"⏰ المواعيد: {', '.join(med['المواعيد'])}", size=14),
                        ft.Row([
                            ft.Text(f"⏳ المتبقي: {max(0, remaining)} يوم", color=status_color, weight="bold"),
                            ft.Text(f"💰 {med['السعر']} جنيه مصري", weight="w600")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.ProgressBar(value=progress, color=status_color, bgcolor=ft.Colors.GREY_200),
                    ])
                )
            )
            list_container.controls.append(card)
        total_cost_text.value = f"إجمالي تكلفة الأدوية: {manager.get_total_cost():.2f} جنيه مصري"
        page.update()

    def delete_action(med):
        manager.delete_medicine(med)
        update_list()
        page.snack_bar = ft.SnackBar(ft.Text("تم حذف الدواء"))
        page.update()

    def refresh_from_file(e):
        manager.medications = manager.load_data()
        update_list()
        page.snack_bar = ft.SnackBar(ft.Text("تم التحديث من الملف بنجاح"))
        page.update()

    def save_now(e):
        manager.save_data()
        page.snack_bar = ft.SnackBar(ft.Text("تم حفظ البيانات يدوياً"))
        page.update()

    def add_click(e):
        try:
            if not name_field.value or not duration_field.value:
                raise ValueError("يرجى ملء الحقول الأساسية")
            manager.add_medicine(
                name_field.value,
                [t.strip() for t in times_field.value.split(",")] if times_field.value else ["غير محدد"],
                int(duration_field.value),
                float(price_field.value) if price_field.value else 0
            )
            # تفريغ الحقول
            for f in [name_field, times_field, duration_field, price_field]:
                f.value = ""
            add_section.expanded = False
            update_list()
            page.snack_bar = ft.SnackBar(ft.Text("تمت الإضافة بنجاح ✅"))
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"خطأ: تأكد من صحة البيانات"))
            page.update()

    # قسم الإضافة بتصميم أنيق
    add_section = ft.ExpansionTile(
        title=ft.Text("إضافة دواء جديد", weight="bold"),
        leading=ft.Text("+", size=20, color=ft.Colors.BLUE),
        controls=[
            ft.Container(
                padding=20,
                content=ft.Column([
                    name_field,
                    times_field,
                    ft.Row([duration_field, price_field], spacing=10),
                    ft.ElevatedButton("حفظ الدواء", on_click=add_click, width=400, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))
                ], spacing=15)
            )
        ]
    )

    page.add(
        ft.Container(
            padding=10,
            content=ft.Column([
                ft.Column([
                ft.Text("⚠️ التنبيه: هذا التطبيق للتذكير فقط وليس بديلاً عن استشارة الطبيب أو الصيدلي. التأكد من الجرعة مهم.", size=12, color=ft.Colors.RED_700),
                ft.Text("للاستعلام: 01030924083", size=12, color=ft.Colors.BLUE_800),
                ft.Row([
                    ft.Text("🏥", size=40),
                    ft.Text("صحتك أفضل", size=28, weight="bold"),
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], spacing=5),
                add_section,
                ft.Container(
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=10,
                    content=ft.Column([
                        ft.Text("أمثلة على الأدوية والجرعات (للاستشارة فقط)", weight="bold"),
                        ft.Row([ft.Text("دواء"), ft.Text("جرعة مقترحة"), ft.Text("سعر"), ft.Text("بديل")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("باراسيتامول"), ft.Text("500mg كل 8 ساعات"), ft.Text("20 جنيه"), ft.Text("إيبوبروفين")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("أموكسيسيلين"), ft.Text("500mg كل 12 ساعة"), ft.Text("60 جنيه"), ft.Text("أزيثروميسين")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("سيبروفلوكساسين"), ft.Text("500mg يومياً"), ft.Text("80 جنيه"), ft.Text("ليفوفلوكساسين")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("ديكلوفيناك"), ft.Text("50mg كل 12 ساعة"), ft.Text("30 جنيه"), ft.Text("نابروكسين")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=4)
                ),
                ft.Divider(height=20, thickness=1),
                ft.Row([
                    ft.Text("الأدوية الحالية", size=20, weight="bold"),
                    ft.Row([
                        ft.TextButton("تحديث من الملف", on_click=refresh_from_file),
                        ft.TextButton("حفظ الآن", on_click=save_now)
                    ], spacing=10),
                    total_cost_text
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                list_container
            ], spacing=20)
        )
    )

    update_list()

ft.app(main)