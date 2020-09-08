from django import forms
from django.conf import settings
# from django.contrib.admin.helpers import AdminForm,  Fieldline
from django.contrib.admin.utils import flatten
from django.forms.widgets import Input, CheckboxInput, HiddenInput, Textarea
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from pprint import pprint


class PersonFormMixIn:
    other_country_switch = True
    country_field_name = 'billing_country_code'
    alt_country_text = {
        # 'billing_country_code':  {
        #     'label': _(""),
        #     'help_text': _("")},
        'billing_country_area': {
            'label': _("Territory, or Province"),
            'help_text': '',
            'initial': ''},
        'billing_postcode':  {
            'label': _("Postal Code"),
            'help_text': ''}, }
    fieldsets = (
        (None, {
            'fields': [('first_name', 'last_name', )],
            'position': 1,
        }),
        (_('username'), {
            'fields': ['username'],
            'position': None
        }),
        (_('address'), {
            'classes': ('collapse', 'address', ),
            'fields': [
                'billing_address_1',
                'billing_address_2',
                ('billing_city', 'billing_country_area', 'billing_postcode', )
                ],
            'position': 'end'
        }), )
    formfield_attrs_overrides = {
        '_default_': {'size': 15, },
        'email': {'maxlength': 191, 'size': 20, },
        'billing_country_area': {'maxlength': 2, 'size': 2, },
        'billing_postcode': {'maxlength': 5, 'size': 5, },
        # 'first_name': {'size': 12, },
        # 'username': {'size': 25, },
        # # 'last_name': {'size': 18, },
        # 'password': {'size': 10, },
        # 'password1': {'size': 10, },
        # 'password2': {'size': 10, },
        # 'billing_address_1': {'size': 20, },
        # 'billing_address_2': {'size': 20, },
        }

    def set_alt_data(self, name, field, value):
        initial = self.get_initial_for_field(field, name)
        data_name = self.add_prefix(name)
        data_val = field.widget.value_from_datadict(self.data, self.files, data_name)
        if not field.has_changed(initial, data_val):
            data = self.data.copy()
            data[data_name] = value
            data._mutable = False
            self.data = data
            self.initial[name] = value  # TODO: Won't work since initial determined earlier.
    # end def set_alt_data

    def prep_fields(self):
        alt_country = False
        if self.other_country_switch:
            alt_country = self.data.get('other_country', False)
            if not alt_country:
                self.fields.pop(self.country_field_name, None)
        fields = self.fields
        overrides = getattr(self, 'formfield_attrs_overrides', {})
        DEFAULT = overrides.get('_default_', {})

        for name, field in fields.items():
            if name in overrides:
                for key, value in overrides[name].items():
                    field.widget.attrs[key] = value  # TODO: Use dict.update instead
            if not overrides.get(name, {}).get('no_size_override', False):
                # TODO: Correct size attributes for all form controls: textarea, others?
                default = DEFAULT.get('size', None)  # Cannot use float("inf") as an int.
                display_size = field.widget.attrs.get('size', None)
                input_size = field.widget.attrs.get('maxlength', None)
                value = ''
                if input_size:
                    possible_size = [int(ea) for ea in (display_size or default, input_size) if ea]
                    # field.widget.attrs['size'] = str(int(min(float(display_size), float(input_size))))
                    value = str(min(possible_size))
                    field.widget.attrs['size'] = value
            if alt_country and name in self.alt_country_text:
                for prop, value in self.alt_country_text[name].items():
                    if prop == 'initial' or prop == 'default':
                        self.set_alt_data(name, field, value)
                    setattr(field, prop, value)
        return fields.copy()

    def make_country_row(self, remaining_fields):
        field_name = self.country_field_name
        field = remaining_fields.pop(field_name, None)
        result = {field_name: field} if field else {}
        other_country_field = remaining_fields.pop('other_country', None)
        if not other_country_field:
            country_name = settings.DEFAULT_COUNTRY
            label = "Not a {} address. ".format(country_name)
            other_country_field = forms.BooleanField(label=_(label), required=False, )
            self.fields['other_country'] = other_country_field
        result.update({'other_country': other_country_field})
        return result

    def _make_fieldsets(self):
        all_fields = self.prep_fields()
        fieldsets = list(getattr(self, 'fieldsets', ((None, {'fields': [], 'position': None}), )))
        print("=============== PersonFormMixIn._make_fieldsets =====================")
        max_position, prepared, new_opts = 0, {}, {}
        for index, fieldset in enumerate(fieldsets):
            fieldset_label, opts = fieldset
            if 'fields' not in opts or 'position' not in opts:
                raise ImproperlyConfigured(_("There must be 'fields' and 'position' in each fieldset. "))
            field_rows = []
            for ea in opts['fields']:
                row = [ea] if isinstance(ea, str) else ea
                temp = {name: all_fields.pop(name) for name in row if name in all_fields}
                if temp:
                    field_rows.append(temp)
            if field_rows:
                fieldset_label = fieldset_label or 'fieldset_' + str(index)
                prepared[fieldset_label] = {'position': opts['position']}
                prepared[fieldset_label]['rows'] = field_rows
                opts['rows'] = field_rows
                opts['field_names'] = flatten(opts['fields'])
                prepared[fieldset_label]['field_names'] = flatten(opts['fields'])
                prepared[fieldset_label]['classes'] = opts.get('classes', [])
                max_position += 1  # opts['position'] if isinstance(opts['position'], int) else 0
                if self.other_country_switch and 'address' in opts.get('classes', ''):
                    country_fields = self.make_country_row(all_fields)
                    new_opts = {'position': opts['position'], 'classes': '', }
                    new_opts['fields'] = [('other_country', self.country_field_name, )]
                    new_opts['field_names'] = flatten(new_opts['fields'])
                    new_opts['rows'] = [country_fields]
                    prepared['other_country'] = {'position': opts['position'], 'rows': [country_fields]}
                    max_position += 1
        if new_opts:
            fieldsets.append(('other_country', new_opts))
        max_position += 1
        field_rows = [{name: value} for name, value in all_fields.items()]
        prepared['remaining'] = {'rows': field_rows, 'position': max_position + 1, }
        fieldsets.append(('remaining', {'rows': field_rows, 'position': max_position + 1, }))
        lookup = {'end': max_position + 2, None: max_position}
        # TODO: Refactor prepared to match fieldset format, but still sort.
        prepared = {k: v for k, v in sorted(prepared.items(),
                    key=lambda ea: lookup.get(ea[1]['position'], ea[1]['position']))
                    }
        pprint(prepared)
        print("-------------------------------------------------------------------------------------")
        fieldsets = [(k, v) for k, v in sorted(fieldsets,
                     key=lambda ea: lookup.get(ea[1]['position'], ea[1]['position']))
                     ]
        pprint(fieldsets)
        print("-------------------------------------------------------------------------------------")
        setup = [(k, v) for k, v in sorted(prepared.items(),
                 key=lambda ea: lookup.get(ea[1]['position'], ea[1]['position']))
                 ]
        pprint(setup)
        return prepared

    def _html_tag(self, tag, data, attr=''):
        return '<' + tag + attr + '>' + data + '</' + tag + '>'

    def make_row(self, columns_data, error_data, row_tag, html_row_attr=''):
        result = []
        if error_data:
            row = self._html_tag(row_tag, ' '.join(error_data))
            result.append(row)
        if columns_data:
            row = self._html_tag(row_tag, ' '.join(columns_data), html_row_attr)
            result.append(row)
        return result

    def column_formats(self, col_head_tag, col_tag, single_col_tag, col_head_data, col_data):
        col_html, single_col_html = '', ''
        if col_head_tag:
            col_html += self._html_tag(col_head_tag, col_head_data, '%(html_col_attr)s')
            single_col_html += col_html
            col_html += self._html_tag(col_tag, col_data)
        else:
            col_html += self._html_tag(col_tag, col_data, '%(html_col_attr)s')
        single_col_html += col_data if not single_col_tag else self._html_tag(single_col_tag, col_data)
        return col_html, single_col_html

    def as_test(self):
        """ Prepares and calls different 'as_<variation>' method variations. """
        data = self.as_p()
        container = 'p'  # table, ul, ''
        if container != 'p':
            data = self._html_tag(container, data)
        return mark_safe(data)

    def _html_output(self, row_tag, col_head_tag, col_tag, single_col_tag, class_attr, col_head_data, col_data,
                     error_col, help_text_html, errors_on_separate_row, as_type=None):
        "Overriding BaseForm._html_output. Output HTML. Used by as_table(), as_ul(), as_p()."
        include_widgets = (Input, Textarea, )  # Base classes for the field.widgets we want.
        exclude_widgets = (CheckboxInput, HiddenInput)  # classes for the field.widgets we do NOT want.
        # ignored_base_widgets = ['ChoiceWidget', 'MultiWidget', 'SelectDateWidget', ]
        # 'ChoiceWidget' is the base for 'RadioSelect', 'Select', and variations.
        col_html, single_col_html = self.column_formats(col_head_tag, col_tag, single_col_tag, col_head_data, col_data)
        prepared = self._make_fieldsets()
        top_errors = self.non_field_errors().copy()  # Errors that should be displayed above all fields.
        # print("========================== PersonFormMixIn._html_output ================================")
        output, hidden_fields, max_columns = [], [], 0
        for fieldset_label, opts in prepared.items():
            single_fields = [ea for ea in opts['rows'] if len(ea) == 1]
            visual_group, styled_labels, label_attrs = [], [], ''
            if len(single_fields) > 1:
                for ea in single_fields:
                    klass = list(ea.values())[0].widget.__class__
                    if issubclass(klass, include_widgets) and not issubclass(klass, exclude_widgets):
                        visual_group.append(ea)
            if len(visual_group) > 1:
                max_label_length = max(len(list(ea.values())[0].label) for ea in visual_group)
                # max_word_length = max(len(w) for ea in visual_group for w in list(ea.values())[0].label.split())
                width = (max_label_length + 1) // 2  # * 0.85 ch
                label_attrs = {'style': "width: {}rem; display: inline-block".format(width)}
                styled_labels = [list(ea.keys())[0] for ea in visual_group]
            row_data = []
            for row in opts['rows']:
                col_count = len(row)
                multi_field_row = False if col_count == 1 else True
                max_columns = col_count if col_count > max_columns else max_columns
                columns_data, error_data, html_class_attr = [], [], ''
                for name, field in row.items():
                    bf = self[name]
                    bf_errors = self.error_class(bf.errors)
                    if bf.is_hidden:
                        if bf_errors:
                            top_errors.extend(
                                [_('(Hidden field %(name)s) %(error)s') %
                                 {'name': name, 'error': str(e)}
                                 for e in bf_errors])
                        hidden_fields.append(str(bf))
                        continue
                    # Create a 'class="..."' attribute if the row or column should have any
                    css_classes = bf.css_classes()
                    if multi_field_row:
                        css_classes = ' '.join(['nowrap', css_classes])
                    html_class_attr = ' class="%s"' % css_classes if css_classes else ''
                    if errors_on_separate_row and bf_errors:
                        error_data.append(error_col % str(bf_errors))
                    has_label_style = name in styled_labels and label_attrs
                    # print(f"{name} has style: {has_label_style} ")
                    if bf.label or has_label_style:
                        attrs = label_attrs if has_label_style else ''
                        label = conditional_escape(bf.label)
                        label = bf.label_tag(label, attrs) or ''
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
                        html_row_attr = ''
                    else:
                        columns_data.append(single_col_html % format_kwargs)
                        html_row_attr = html_class_attr
                row_data.extend(self.make_row(columns_data, error_data, row_tag, html_row_attr))
            # end iterating field rows
            if fieldset_label is not None:
                container_attr = f' class="fieldset_{as_type}""'
                container = None if as_type in ('p', 'fieldset') else as_type
                data = '\n'.join(row_data)
                if container:
                    data = self._html_tag(container, data, container_attr) + '\n'
                legend = self._html_tag('legend', fieldset_label) + '\n'
                fieldset_attr = ''
                fieldset_el = self._html_tag('fieldset', legend + data, fieldset_attr)
                if container:
                    attr = ''
                    if as_type == 'table' and max_columns > 1:
                        colspan = max_columns * 2 if col_head_tag else max_columns
                        attr += f' colspan="{colspan}"'
                    fieldset_col = self._html_tag(single_col_tag or col_tag, fieldset_el, attr)
                    row_attr = ' class="fieldset_row"'
                    fieldset_el = self._html_tag(row_tag, fieldset_col, row_attr)
                output.append(fieldset_el)
            else:
                output.extend(row_data)
        # end iterating fieldsets
        row_ender = '' if not single_col_tag else '</' + single_col_tag + '>'
        row_ender += '</' + row_tag + '>'
        if top_errors:
            attr = ''
            if col_head_tag and as_type == 'table' and max_columns > 0:  # as_type == 'table' or single_col_tag == 'td'
                attr = ' colspan=' + str(max_columns * 2)
            attr += ' id="top_errors"'
            column_kwargs = {
                'field': ' '.join(top_errors),
                'html_col_attr': attr,
                'errors': '',
                'label': '',
                'help_text': '',
                'html_class_attr': '',
                'css_classes': '',
                'field_name': '',
                }
            column = [single_col_html % column_kwargs]  # attr is only applied if there is a col_head_tag
            error_row = self.make_row(column, None, row_tag)[0]
            output.insert(0, error_row)
        if hidden_fields:  # Insert any hidden fields in the last row.
            str_hidden = ''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and insert the hidden fields.
                if last_row.endswith(row_ender):
                    output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
                else:
                    # This can happen in the as_p() case (and possibly other custom display methods).
                    # If there are only top errors, we may not be able to conscript the last row for
                    # our purposes, so insert a new empty row.
                    format_kwargs = {
                        'errors': '',
                        'label': '',
                        'field': str_hidden,
                        'help_text': '',
                        'html_col_attr': '',
                        'html_class_attr': '',
                        'css_classes': '',
                        'field_name': '',
                    }
                    column = [single_col_html % format_kwargs]
                    last_row = self.make_row(column, None, row_tag)[0]
                    output.append(last_row)
            else:  # If there aren't any rows in the output, just append the hidden fields.
                output.append(str_hidden)
        # print("------------------------ End PersonFormMixIn._html_output ------------------------------")
        return mark_safe('\n'.join(output))

    def as_table(self):
        "Overwrite BaseForm.as_table. Return this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            row_tag='tr',
            col_head_tag='th',
            col_tag='td',
            single_col_tag='td',
            class_attr='%(html_class_attr)s',
            col_head_data='%(label)s',
            col_data='%(errors)s%(field)s%(help_text)s',
            error_col='<td colspan="2">%s</td>',
            help_text_html='<br /><span class="helptext">%s</span>',
            errors_on_separate_row=False,
            as_type='table',
        )

    def as_ul(self):
        "Overwrite BaseForm.as_ul. Return this form rendered as HTML <li>s -- excluding the <ul></ul>."
        return self._html_output(
            row_tag='li',
            col_head_tag=None,
            col_tag='span',
            single_col_tag='',
            class_attr='%(html_class_attr)s',
            col_head_data='',
            col_data='%(errors)s%(label)s%(field)s%(help_text)s',
            error_col='%s',
            help_text_html='<span class="helptext">%s</span>',
            errors_on_separate_row=False,
            as_type='ul',
        )

    def as_p(self):
        "Overwrite BaseForm.as_p. Return this form rendered as HTML <p>s."
        return self._html_output(
            row_tag='p',
            col_head_tag=None,
            col_tag='span',
            single_col_tag='',
            class_attr='%(html_class_attr)s',
            col_head_data='',
            col_data='%(label)s%(field)s%(help_text)s',
            error_col='%s',
            help_text_html='<span class="helptext">%s</span>',
            errors_on_separate_row=True,
            as_type='p'
        )
