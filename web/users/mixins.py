from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from pprint import pprint


class PersonFormMixIn:
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
