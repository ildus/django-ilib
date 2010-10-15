# coding: utf-8

from django.core.urlresolvers import reverse

''' Для upload_to в моделях, генерирует файл с уникальных именем.
    Недостаток - все ложится в одну папку '''
def make_upload_path(instance, filename):
    import datetime
    import os
    
    now = datetime.datetime.now()
    ext = os.path.splitext(filename)[1]
    fn = "f%s%s%s%s%s%s"%(now.year, now.month, now.day, now.hour, now.minute, now.second)
    return "uploads/%s%s"%(fn, ext)

''' Решение недостатка первой функции '''
def tree_upload_path(folder):
    def make_upload_path(instance, filename):
        import datetime
        import os
        
        now = datetime.datetime.now()
        ext = os.path.splitext(filename)[1]
        fn = "f%s%s%s%s%s%s"%(now.year, now.month, now.day, now.hour, now.minute, now.second)
        return "uploads/%s/%s%s"%(folder, fn, ext)
    
    return make_upload_path

def is_generic_filename(filename):
    import re
    fname_re = re.compile(r'^f[0-9]+\.', re.I)
    
    matches = fname_re.findall(filename)
    return len(matches) > 0

''' Функция для админки, возвращающая название в виде ссылки на страницу изменения '''
def _change_link():
    def change_link(self):
        change_link.allow_tags = True
        
        info = self._meta.app_label, self._meta.module_name            
        link = reverse('admin:%s_%s_change' % info, args = [self.id])
        
        return '<a href="%s"> %s </a>'%(link, unicode(self))

    return change_link

#возвращает список разбитый на страницы
def paginate(queryset, page, count):
    from django.core.paginator import Paginator, InvalidPage, EmptyPage
    
    paginator = Paginator(queryset, count)
    
    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages)

    ON_EACH_SIDE = 3
    ON_ENDS = 2
    DOT = '.'

    if paginator.num_pages <=  10:
        page_range = range(paginator.num_pages)
    else:
        page_range = []
        if page > (ON_EACH_SIDE  + ON_ENDS):
            page_range.extend(range(0, ON_EACH_SIDE  - 1))
            page_range.append(DOT)
            if page < paginator.num_pages:
                page_range.extend(range(page - ON_EACH_SIDE, page+1))
            else:
                page_range.extend(range(page - ON_EACH_SIDE, page))
        else:
            page_range.extend(range(0, page  + 1))
        
        if page < (paginator.num_pages -  ON_EACH_SIDE - ON_ENDS - 1):
            page_range.extend(range(page + 1, page +  ON_EACH_SIDE + 1))
            page_range.append(DOT)
            page_range.extend(range(paginator.num_pages  - ON_ENDS,  paginator.num_pages))
        else:
            page_range.extend(range(page + 1, paginator.num_pages))
                
    return objects, paginator, page_range
    