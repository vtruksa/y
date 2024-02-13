from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def get_profile_avatar(profile, x, round):
    tag = "<img width:" + str(x) + "px src='"
    if profile.avatar:
        tag += str(profile.avatar.url) + "'"
    else:
        tag += "media/avatars/default.png"

    tag += ">"
    return tag

@register.filter(is_safe=True)
# render a form with bootstrap 5
def render_bs5(form):
    html = ""
    for f in form:
        try:
            input_type = f.field.widget.input_type
        except:
            input_type = 'tag'
        group = 'form-group'
        cl = 'form-control'        
        checked = ''

        if input_type == 'checkbox': 
            group = 'form-check'
            cl = 'form-check-input'
            if f.value(): checked = 'checked'

        html += '<div class='+group+'><label>'+str(f.label)+'</label>'
        if input_type is not 'tag':
            html += '<input type="' + input_type + '" name="'+ f.name +'" class="'+ cl +'" '+ checked +'>'
        else:
            html += '<textarea rows=4 name="'+f.name+'" class="'+cl+'"></textarea>'
        html += '<br><small class="form-text text-muted">'+f.help_text+'</small>'
        html+= '</div>'

    return mark_safe(html)