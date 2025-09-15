from django.contrib import admin
from .models import (
    Contest,
    Problem,
    TestCase,
    Student,
    PracticeCategory,
    PracticeSubtopic,
    PracticeQuestion,
    PracticeOption,
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "mobile", "college", "passout_year", "branch")
    search_fields = ("name", "email", "college", "branch")
    list_filter = ("passout_year", "branch")

    # 🚫 Prevent add/delete/change from admin
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ---------- Participant Admin ----------


# ---------- Contest ----------
class ContestAdmin(admin.ModelAdmin):
    list_display = ("name", "start_at", "duration_minutes", "is_active")


admin.site.register(Contest, ContestAdmin)


# ---------- Problem ----------
class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 0


class ProblemAdmin(admin.ModelAdmin):
    list_display = (
        "contest",
        "code",
        "title",
    )
    inlines = [TestCaseInline]


admin.site.register(Problem, ProblemAdmin)
admin.site.register(TestCase)


# ---------- Submission ----------


# ---------- Practice (MCQ) ----------
class PracticeOptionInline(admin.TabularInline):
    model = PracticeOption
    extra = 0


@admin.register(PracticeCategory)
class PracticeCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")
    ordering = ("order", "name")


@admin.register(PracticeSubtopic)
class PracticeSubtopicAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "order")
    list_filter = ("category",)
    ordering = ("category", "order")
    search_fields = ("name",)


@admin.register(PracticeQuestion)
class PracticeQuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "subtopic", "difficulty", "is_active", "created_at")
    list_filter = ("difficulty", "is_active", "subtopic__category")
    search_fields = ("text",)
    inlines = [PracticeOptionInline]
    list_select_related = ("subtopic", "subtopic__category")

    def short_text(self, obj):
        return (obj.text[:60] + "...") if len(obj.text) > 60 else obj.text
    short_text.short_description = "Question"

