from django.contrib.admin.helpers import AdminForm,  Fieldline
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from pprint import pprint


class PersonFormMixIn:

    def _intercept_html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
        # row_start, attr, row_data = normal_row.partition('%(html_class_attr)s>')
        # row_start = row_start.split(' ')
        # start_tag = row_start[0]
        # row_end = '</' + start_tag[1:] + '>'  # expected start_tag: '<tr' or '<li' or '<p'
        # endlen = len(row_end)
        # if row_data[-endlen:] == row_end:
        #     row_data = row_data[:-endlen]
        #     col_data = {'hasclass': '', 'noclass': ''}
        #     if row_data.startswith('<'):
        #         col_start, tag_end, col_data = row_data.partition('>')
        #         col_data['noclass'] = col_data['hasclass'] = col_start + ' ' + attr + col_data
        #     else:
        #         col_data['noclass'] = row_data
        #         col_data['hasclass'] = '<div' + ' ' + attr + row_data + '</div>'
        # else:
        #     row_end = ''
        #     col_data = None

        # # Errors that should be displayed above all fields.
        # top_errors = self.non_field_errors().copy()
        # output, hidden_fields = [], []

        # for row_label, opts in prepared.items():
        #     fields = opts['fields']
        #     for name, field in fields.items():
        pass

    def _html_tag(self, tag, data, attr=''):
        return '<' + tag + attr + '>' + data + '</' + tag + '>'

    def make_row(self, columns_data, error_data, row_tag, html_row_attr=''):
        result = []
        if error_data:
            row = self._html_tag(row_tag, ''.join(error_data))
            result.append(row)
        row = self._html_tag(row_tag, ''.join(columns_data), html_row_attr)
        result.append(row)

    def _html_output(self, row_tag, col_head_tag, col_tag, single_col_tag, class_attr,
                     col_head_data, col_data, error_col, help_text_html, errors_on_separate_row):
        "Overriding BaseForm._html_output. Output HTML. Used by as_table(), as_ul(), as_p()."
        prepared = {
            'names_row': {
                'field_names': ['first_name', 'last_name'],
                'fields': {},
                'html': '',
                'position': 1,
            },
            'address_row': {
                'field_names': ['billing_city', 'billing_country_area', 'billing_postcode'],
                'fields': {},
                'html': '',
                'position': None
            },
        }
        max_columns, max_position = 0, 0
        for row_label, opts in prepared.items():
            fields = {name: self.fields.pop(name) for name in opts['field_names'] if name in self.fields}
            max_columns = len(fields) if len(fields) > max_columns else max_columns
            max_position += opts['position'] if isinstance(opts['position'], int) else 0
            prepared[row_label]['fields'] = fields
        # max_columns = 2 * max(len(data['fields']) for data in prepared.values())
        max_position += 1
        prepared['remaining'] = {'fields': self.fields.copy(), 'position': max_position + 1, }
        prepared = {k: v for k, v in sorted(prepared.items(),
                    key=lambda item: item[1]['position'] if item[1]['position'] else max_position)}
        col_html, single_col_html = '', ''
        if col_head_tag:
            col_html += self._html_tag(col_head_tag, col_head_data, '%(html_col_attr)s')
            single_col_html += col_html
            col_html += self._html_tag(col_tag, col_data)
        else:
            col_html += self._html_tag(col_tag, col_data, '%(html_col_attr)s')
        single_col_html += col_data if not single_col_tag else self._html_tag(single_col_tag, col_data)
        # Errors that should be displayed above all fields.
        top_errors = self.non_field_errors().copy()
        output, hidden_fields = [], []
        for row_label, opts in prepared.items():
            fields = opts['fields']
            multi_field_row = True if row_label != 'remaining' and len(fields) != 1 else True
            columns_data, error_data, html_class_attr = [], [], ''
            for name, field in fields.items():
                bf = self[name]
                bf_errors = self.error_class(bf.errors)
                if bf.is_hidden:
                    if bf_errors:
                        top_errors.extend(
                            [_('(Hidden field %(name)s) %(error)s') % {'name': name, 'error': str(e)}
                             for e in bf_errors])
                    hidden_fields.append(str(bf))
                else:
                    # Create a 'class="..."' attribute if the row or column should have any
                    css_classes = bf.css_classes()
                    html_class_attr = ' class="%s"' % css_classes if css_classes else ''
                    if errors_on_separate_row and bf_errors:
                        error_data.append(error_col % str(bf_errors))
                    if bf.label:
                        label = conditional_escape(bf.label)
                        label = bf.label_tag(label) or ''
                    else:
                        label = ''
                    if field.help_text:
                        help_text = help_text_html % field.help_text
                    else:
                        help_text = ''
                    format_kwargs = {
                        'errors': bf_errors,
                        'label': label,
                        'field': bf,
                        'help_text': help_text,
                        'html_col_attr': html_class_attr if multi_field_row else '',
                        'html_class_attr': html_class_attr,
                        'css_classes': css_classes,
                        'field_name': bf.html_name,
                    }
                    if multi_field_row:
                        columns_data.append(col_html % format_kwargs)
                    else:
                        columns_data.append(single_col_html % format_kwargs)
                        output.extend(self.make_row(columns_data, error_data, row_tag, html_class_attr))
                        columns_data, error_data = [], []
            if multi_field_row:
                output.extend(self.make_row(columns_data, error_data, row_tag))
        row_ender = '' if not single_col_tag else '</' + single_col_tag + '>'
        row_ender += '</' row_tag '>'
        if top_errors:
            error_row = self.make_row(top_errors, None, row_tag)
            output.insert(0, error_row)
        if hidden_fields:  # Insert any hidden fields in the last row.
            str_hidden = ''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and
                # insert the hidden fields.
                if not last_row.endswith(row_ender):
                    # This can happen in the as_p() case (and possibly others
                    # that users write): if there are only top errors, we may
                    # not be able to conscript the last row for our purposes,
                    # so insert a new, empty row.
                    last_row = (normal_row % {
                        'errors': '',
                        'label': '',
                        'field': '',
                        'help_text': '',
                        'html_class_attr': html_class_attr,
                        'css_classes': '',
                        'field_name': '',
                    })
                    output.append(last_row)
                output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
            else:
                # If there aren't any rows in the output, just append the
                # hidden fields.
                output.append(str_hidden)
        return mark_safe('\n'.join(output))

    def as_person_details(self):
        custom_fields = {
            'names_row': ['first_name', 'last_name', ],
            'address_row': ['billing_city', 'billing_country_area', 'billing_postcode', ],
        }
        prepared = {
            'names_row': {
                'field_names': ['first_name', 'last_name'],
                'fields': {},
                'html': '',
                'position': 1,
            },
            'address_row': {
                'field_names': ['billing_city', 'billing_country_area', 'billing_postcode'],
                'fields': {},
                'html': '',
                'position': None
            },
        }
        errors_on_separate_row = False
        help_text_br = False
        for row_label, field_lables in custom_fields.items():
            prepared[row_label]['fields'] = {name: field for name, field in self.fields.items() if name in field_lables}
        max_columns = 2 * max(len(data['fields']) for data in prepared.values())

        row_ender = '</td></tr>'
        help_text_html = '<span class="helptext">%s</span>'
        header_col = '<th%(html_class_attr)s>%(label)s</th>'
        if help_text_br:
            data_col = '%(errors)s%(field)s<br />%(help_text)s'
        else:
            data_col = '%(errors)s%(field)s%(help_text)s'
        data_html = header_col + '<td>' + data_col + '</td>'  # will need the <tr> ... </tr>
        error_column_html = '<td colspan="2">%s</td>'  # will need the <tr> ... </tr>
        error_row_start = '<tr><td colspan="' + str(max_columns)
        error_row = error_row_start + '">%s ' + row_ender
        normal_row = '<tr%(html_class_attr)s><th>%(label)s</th><td colspan="'
        normal_row += str(max_columns - 1) + '">' + data_col + row_ender

        top_errors, hidden_fields, used_field_names = [], [], []
        for prep_label, prep_data in prepared.items():
            error_count, output = 0, []
            error_columns = ['<tr>']
            row_columns = ['<tr>']
            for name, field in prep_data['fields'].items():
                bf = self[name]
                bf_errors = self.error_class(bf.errors)
                if bf.is_hidden:
                    if bf_errors:
                        top_errors.extend(
                            [_('(Hidden field %(name)s) %(error)s') % {'name': name, 'error': str(e)}
                                for e in bf_errors])
                    hidden_fields.append(str(bf))
                else:
                    # Create a 'class="..."' attribute if needed and apply CSS classes.
                    css_classes = bf.css_classes()
                    html_class_attr = ' class="%s"' % css_classes if css_classes else ''
                    if errors_on_separate_row:
                        error_string = str(bf_errors) if bf_errors else ' '
                        error_count += 1 if bf_errors else 0
                        error_columns.append(error_column_html % error_string)
                    if bf.label:
                        label = conditional_escape(bf.label)
                        label = bf.label_tag(label) or ''
                    else:
                        label = ''
                    help_text = help_text_html % field.help_text if field.help_text else ''
                row_columns.append(data_html % {
                    'errors': bf_errors,
                    'label': label,
                    'field': bf,
                    'help_text': help_text,
                    'html_class_attr': html_class_attr,
                    'css_classes': css_classes,
                    'field_name': bf.html_name,
                })
            row_columns.append('</tr>')
            if error_count:
                error_columns.append('</tr>')
                output.append(''.join(error_columns))
            output.append(''.join(row_columns))
            prepared[prep_label]['html'] = "\n".join(output)
            used_field_names.extend(prep_data['field_names'])
        if top_errors or hidden_fields:
            new_errors = str(top_errors) + ''.join(hidden_fields)
        else:
            new_errors = ''
        has_initial_top_errors = self.non_field_errors() or \
            any(self[name].is_hidden and self.error_class(self[name].errors) for name in self.fields)

        self.fields = {name: field for name, field in self.fields.items() if name not in used_field_names}
        html_output = self._html_output(
            normal_row=normal_row,
            error_row=error_row,
            row_ender=row_ender,
            help_text_html=help_text_html,
            errors_on_separate_row=errors_on_separate_row,
        )
        line_ender = "%s\n" % row_ender
        rows = html_output.split(line_ender)  # TODO: Consider using .splitlines([keepends])
        for prep_label, prep_data in prepared.items():
            self.fields.update(prep_data['fields'])

        if new_errors:
            if has_initial_top_errors:
                initial_errors = rows[0][len(error_row_start):-len(line_ender)]
                rows[0] = error_row % ''.join((initial_errors, new_errors) + '\n')
            else:
                rows.insert(0, error_row % new_errors + '\n')
        first_field_row = 1 if new_errors or has_initial_top_errors else 0
        for row_label, row_data in prepared.items():
            if not row_data['fields']:
                continue
            if isinstance(row_data['position'], int):
                position = row_data['position'] + first_field_row - 1
                rows.insert(position, row_data['html'] + '\n')
            else:
                rows.append(row_data['html'] + '\n')

        print("=========================== PersonFormMixIn.as_person_details =======================")
        print(f"New errors: {new_errors} |  ")
        pprint(prepared)
        print("-------------------------------------------------------------------------------------")
        pprint(rows)
        print("-------------------------------------------------------------------------------------")
        pprint(self.fields)
        return mark_safe(' '.join(rows))

    def as_table(self):
        "Return this form rendered as HTML <tr>s -- excluding the <table></table>."
        # single = single_field_row_start + single_field_row_col_start + col_data + col_end + row_end
        # row_fields = ('first', 'second', )
        # html_cols = ''.join((col_start + col_data + col_end) % ea for ea in row_fields)
        # multi = row_start + html_cols + row_end
        return self._html_output(
            row_tag='tr',
            col_head_tag='th',
            col_tag='td',
            single_col_tag='td',
            class_attr='%(html_class_attr)s',
            col_head_data='%(label)s',
            col_data='%(errors)s%(field)s%(help_text)s',
            error_col='<td colspan="2">%s</td>',
            help_text_html='<br><span class="helptext">%s</span>',
            errors_on_separate_row=False,
        )

    def as_ul(self):
        "Return this form rendered as HTML <li>s -- excluding the <ul></ul>."

        return self._html_output(
            row_tag='li',
            col_head_tag=None,
            col_tag='span',
            single_col_tag='',
            class_attr='%(html_class_attr)s',
            col_head_data='',
            col_data='%(errors)s%(label)s %(field)s%(help_text)s',
            error_col='%s',
            help_text_html='<span class="helptext">%s</span>',
            errors_on_separate_row=False,
        )

    def as_p(self):
        "Return this form rendered as HTML <p>s."
        return self._html_output(
            row_tag='p',
            col_head_tag=None,
            col_tag='span',
            single_col_tag='',
            class_attr='%(html_class_attr)s',
            col_head_data='',
            col_data='%(label)s %(field)s%(help_text)s',
            error_col='%s',
            help_text_html='<span class="helptext">%s</span>',
            errors_on_separate_row=True,
        )

# class FormLineMixIn:
#     """ Allows Django forms to define fields or fieldsets similarly to admin.ModelAdmin setup. """
#     model = None
#     USERNAME_FLAG = ''
#     fields = None
#     fieldsets = (
#         (None, {
#             'fields': [('first_name', 'last_name'), model.get_email_field_name(), USERNAME_FLAG, model.USERNAME_FIELD],
#         }),
#         ('address', {
#             'fields': [('billing_city', 'billing_country_area', 'billing_postcode', )],
#             'position': None,
#         }),
#     )
#     # self, form, fieldsets, prepopulated_fields, readonly_fields=None, model_admin=None

#     def _get_fieldsets(self):
#         fields = getattr(self, 'fields', None)
#         if hasattr(self, 'fieldsets'):
#             if fields is not None:
#                 raise ImproperlyConfigured(_("Only one of 'fields' and 'fieldsets' should be defined, not both. "))
#             return self.fieldsets
#         if fields is None:
#             raise ImproperlyConfigured(_("Either 'fields' or 'fieldsets' must be defined. "))
#         return ((None, {'fields': list(fields)}))

#     def _get_fields(self):
#         fieldsets = self._get_fieldsets()
#         field_groups = []
#         for label, opts in fieldsets.items():
#             if 'fields' not in opts:
#                 raise ImproperlyConfigured(_("There is a missing 'fields' key in the fieldsets definition. "))
#             field_groups.extend(opts['fields'])
#         fields, fieldlines = [], []
#         for ea in field_groups:
#             if isinstance(ea, tuple):
#                 fields.extend(ea)
#                 fieldlines.append(ea)
#             elif isinstance(ea, str):
#                 fields.append(ea)
#                 fieldlines.append((ea, ))
#         self._fieldlines = fieldlines
#         return fields

#     def __iter__(self):
#         for field in self.fields:
#             yield FormFieldline(self.form, field, self.readonly_fields, model_admin=self.model_admin)
#     # end class FormLineMixIn


# class FormFieldline(Fieldline):

#     pass

#     # end class FormFieldLine
