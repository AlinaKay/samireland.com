from django import forms
from django.forms.extras.widgets import SelectDateWidget
from blog.models import BlogPost

EMPTY_FIELD_ERROR = "You cannot submit a blog post with no %s"


class DateInput(forms.DateInput):
    input_type = 'date'



class PlainTextarea(forms.Textarea):

    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(PlainTextarea, self).build_attrs(extra_attrs, **kwargs)
        if "cols" in attrs: del attrs["cols"]
        if "rows" in attrs: del attrs["rows"]
        return attrs



class BlogPostForm(forms.models.ModelForm):


    class Meta:
        model = BlogPost
        fields = ("title", "date", "body", "visible")
        widgets = {
         "title": forms.fields.TextInput,
         "date": DateInput,
         "body": PlainTextarea
        }
        error_messages = {
         "title": {"required": EMPTY_FIELD_ERROR % "title"},
         "date": {"required": EMPTY_FIELD_ERROR % "date"},
         "body": {"required": EMPTY_FIELD_ERROR % "body"}
        }