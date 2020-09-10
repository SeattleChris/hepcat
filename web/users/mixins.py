from django import forms
from django.conf import settings
from django.contrib.admin.utils import flatten
from django.forms.widgets import Input, CheckboxInput, HiddenInput, Textarea
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


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
        }

    def set_alt_data(self, name, field, value):
        """ Modify the form submitted value if it matches a no longer accurate default value. """
        initial = self.get_initial_for_field(field, name)
        data_name = self.add_prefix(name)
        data_val = field.widget.value_from_datadict(self.data, self.files, data_name)
        if not field.has_changed(initial, data_val):
            data = self.data.copy()
            data[data_name] = value
            data._mutable = False
            self.data = data
            self.initial[name] = value  # TODO: Won't work since initial determined earlier.

    def prep_fields(self):
        """ Returns a copy after it modifies self.fields according to overrides, country switch, and maxlength. """
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
                field.widget.attrs.update(overrides[name])
                # for key, value in overrides[name].items():
                #     field.widget.attrs[key] = value  # TODO: Use dict.update instead
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

    def test_field_order(self, data):
        """ Deprecated. Log printing the dict, array, or tuple in the order they are currently stored. """
        from pprint import pprint
        log_lines = [(key, value) for key, value in data.items()] if isinstance(data, dict) else data
        for line in log_lines:
            pprint(line)
        # end test_field_order

    def prep_country_fields(self, remaining_fields):
        """ Used in _make_fieldsets for a row that has the country field (if present) and the country switch. """
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
        """ Updates the dictionaries of each fieldset with 'rows' of field dicts, and a flattend 'field_names' list. """
        all_fields = self.prep_fields()
        fieldsets = list(getattr(self, 'fieldsets', ((None, {'fields': [], 'position': None}), )))
        top_errors = self.non_field_errors().copy()  # Errors that should be displayed above all fields.
        max_position, form_column_count, hidden_fields, remove_idx = 0, 0, [], []
        for index, fieldset in enumerate(fieldsets):
            fieldset_label, opts = fieldset
            if 'fields' not in opts or 'position' not in opts:
                raise ImproperlyConfigured(_("There must be 'fields' and 'position' in each fieldset. "))
            field_rows, fs_column_count = [], 0
            for ea in opts['fields']:
                row = [ea] if isinstance(ea, str) else ea
                existing_fields = {}
                for name in row:
                    if name not in all_fields:
                        continue
                    field = all_fields.pop(name)
                    bf = self[name]
                    bf_errors = self.error_class(bf.errors)
                    if bf.is_hidden:
                        if bf_errors:
                            top_errors.extend(
                                [_('(Hidden field %(name)s) %(error)s') %
                                    {'name': name, 'error': str(e)}
                                    for e in bf_errors])
                        hidden_fields.append(str(bf))
                    else:
                        existing_fields[name] = field
                if existing_fields:  # only adding non-empty rows. May be empty if these fields are not in current form.
                    fs_column_count = max((fs_column_count, len(existing_fields)))
                    field_rows.append(existing_fields)
            if field_rows:
                if self.other_country_switch and 'address' in opts.get('classes', ''):
                    country_fields = self.prep_country_fields(all_fields)
                    opts['fields'].append(('other_country', self.country_field_name, ))
                    fs_column_count = max((fs_column_count, len(country_fields)))
                    field_rows.append(country_fields)
                opts['rows'] = field_rows
                opts['field_names'] = flatten(opts['fields'])
                opts['rows'] = field_rows
                opts['column_count'] = fs_column_count
                if fieldset_label is None:
                    form_column_count = max((fs_column_count, form_column_count))
                max_position += 1
            else:
                remove_idx.append(index)
        for index in reversed(remove_idx):
            fieldsets.pop(index)
        max_position += 1
        field_rows = [{name: value} for name, value in all_fields.items()]
        field_names = list(all_fields.keys())
        fieldsets.append((None, {'rows': field_rows, 'position': max_position + 1, 'field_names': field_names, }))
        lookup = {'end': max_position + 2, None: max_position}
        fieldsets = [(k, v) for k, v in sorted(fieldsets,
                     key=lambda ea: lookup.get(ea[1]['position'], ea[1]['position']))
                     ]
        summary = {'top_errors': top_errors, 'hidden_fields': hidden_fields, 'columns': form_column_count}
        fieldsets.append(('summary', summary, ))
        return fieldsets

    def _html_tag(self, tag, data, attr_string=''):
        """ Wraps 'data' in an HTML element with an open and closed 'tag', applying the 'attr_string' attributes. """
        return '<' + tag + attr_string + '>' + data + '</' + tag + '>'

    def make_row(self, columns_data, error_data, row_tag, html_row_attr=''):
        """ Flattens data lists, wraps them in HTML element of provided tag and attr string. Returns a list. """
        result = []
        if error_data:
            row = self._html_tag(row_tag, ' '.join(error_data))
            result.append(row)
        if columns_data:
            row = self._html_tag(row_tag, ' '.join(columns_data), html_row_attr)
            result.append(row)
        return result

    def make_headless_row(self, html_args, html_el, column_count, col_attr='', row_attr=''):
        """ Creates a row with no column head, spaned across as needed. Used for top errors and imbedding fieldsets. """
        row_tag, col_head_tag, col_tag, single_col_tag, as_type, all_fieldsets = html_args
        if as_type == 'table' and column_count > 0:
            colspan = column_count * 2 if col_head_tag else column_count
            col_attr += f' colspan="{colspan}"' if colspan > 1 else ''
        if single_col_tag:
            html_el = self._html_tag(single_col_tag, html_el, col_attr)
        else:
            row_attr += col_attr
        html_el = self._html_tag(row_tag, html_el, row_attr)
        return html_el

    def column_formats(self, col_head_tag, col_tag, single_col_tag, col_head_data, col_data):
        """ Returns multi-column and single-column string formatters with head and nested tags as needed. """
        col_html, single_col_html = '', ''
        attrs = '%(html_col_attr)s'
        if col_head_tag:
            col_html += self._html_tag(col_head_tag, col_head_data)  # , attrs
            single_col_html += col_html
            # attrs = ''
        col_html += self._html_tag(col_tag, col_data, attrs)
        single_col_html += col_data if not single_col_tag else self._html_tag(single_col_tag, col_data, attrs)
        return col_html, single_col_html

    def determine_label_width(self, opts):
        """ Returns a attr_dict and list of names of fields whose labels should apply these attributes. """
        include_widgets = (Input, Textarea, )  # Base classes for the field.widgets we want.
        exclude_widgets = (CheckboxInput, HiddenInput)  # classes for the field.widgets we do NOT want.
        single_fields = [ea for ea in opts['rows'] if len(ea) == 1]
        visual_group, styled_labels, label_attrs_dict = [], [], {}
        if len(single_fields) > 1:
            for ea in single_fields:
                klass = list(ea.values())[0].widget.__class__
                if issubclass(klass, include_widgets) and not issubclass(klass, exclude_widgets):
                    visual_group.append(ea)
        if len(visual_group) > 1:
            max_label_length = max(len(list(ea.values())[0].label) for ea in visual_group)
            # max_word_length = max(len(w) for ea in visual_group for w in list(ea.values())[0].label.split())
            width = (max_label_length + 1) // 2  # * 0.85 ch
            label_attrs_dict = {'style': "width: {}rem; display: inline-block".format(width)}
            styled_labels = [list(ea.keys())[0] for ea in visual_group]
        return label_attrs_dict, styled_labels

    def form_main_rows(self, html_args, fieldsets, form_col_count):
        """ Returns a list of formatted content of each main form 'row'. Called after preparing fields and row_data. """
        *args, as_type, all_fieldsets = html_args
        output = []
        for fieldset_label, opts in fieldsets:
            row_data = opts['row_data']
            if all_fieldsets or fieldset_label is not None:
                container_attr = f' class="fieldset_{as_type}""'
                container = None if as_type in ('p', 'fieldset') else as_type
                data = '\n'.join(row_data)
                if container:
                    data = self._html_tag(container, data, container_attr) + '\n'
                if fieldset_label:
                    legend = self._html_tag('legend', fieldset_label) + '\n'
                    fieldset_attr = ''
                else:
                    legend = ''
                    fieldset_attr = ' class="noline"'
                fieldset_el = self._html_tag('fieldset', legend + data, fieldset_attr)
                if container:
                    col_attr = ''
                    row_attr = ' class="fieldset_row"'
                    fieldset_el = self.make_headless_row(html_args, fieldset_el, form_col_count, col_attr, row_attr)
                output.append(fieldset_el)
            else:
                output.extend(row_data)
        return output

    def as_test(self):
        """ Prepares and calls different 'as_<variation>' method variations. """
        container = 'table'  # table, ul, p, fieldset, ...

        func = getattr(self, 'as_' + container)
        data = func()
        if container not in ('p', 'fieldset', ):
            data = self._html_tag(container, data)
        return mark_safe(data)

    def _html_output(self, row_tag, col_head_tag, col_tag, single_col_tag, col_head_data, col_data,
                     help_text_br, errors_on_separate_row, as_type=None):
        """ Overriding BaseForm._html_output. Output HTML. Used by as_table(), as_ul(), as_p(), etc. """
        help_tag = 'span'
        all_fieldsets = True if as_type == 'fieldset' else False
        html_args = [row_tag, col_head_tag, col_tag, single_col_tag, as_type, all_fieldsets]
        # ignored_base_widgets = ['ChoiceWidget', 'MultiWidget', 'SelectDateWidget', ]
        # 'ChoiceWidget' is the base for 'RadioSelect', 'Select', and variations.
        col_html, single_col_html = self.column_formats(col_head_tag, col_tag, single_col_tag, col_head_data, col_data)
        fieldsets = self._make_fieldsets()
        assert fieldsets[-1][0] == 'summary', "The final row from _make_fieldsets is reserved for form summary data. "
        summary = fieldsets.pop()[1]
        data_labels = ('top_errors', 'hidden_fields', 'columns')
        assert isinstance(summary, dict) and all(ea in summary for ea in data_labels), "Malformed fieldsets summary. "
        hidden_fields = summary['hidden_fields']
        top_errors = summary['top_errors']
        form_col_count = 1 if all_fieldsets else summary['columns']
        col_double = col_head_tag and as_type == 'table'

        for fieldset_label, opts in fieldsets:
            label_width_attrs_dict, width_labels = '', [] if as_type == 'table' else self.determine_label_width(opts)
            col_count = opts['column_count'] if fieldset_label else form_col_count
            row_data = []
            for row in opts['rows']:
                multi_field_row = False if len(row) == 1 else True
                columns_data, error_data, html_class_attr = [], [], ''
                for name, field in row.items():
                    field_attrs_dict = {}
                    bf = self[name]
                    bf_errors = self.error_class(bf.errors)
                    if errors_on_separate_row and bf_errors:
                        attr = ' colspan="2"' if col_head_tag and as_type == 'table' else ''  # TODO: colspan for single_col_tag
                        tag = col_tag if multi_field_row else single_col_tag
                        err = str(bf_errors) if not tag else self._html_tag(tag, bf_errors, attr)
                        error_data.append(err)
                    if bf.label:
                        attrs = label_width_attrs_dict if name in width_labels else {}
                        label = conditional_escape(bf.label)
                        label = bf.label_tag(label, attrs) or ''
                    else:  # TODO: Check bf.label always exists?
                        raise ImproperlyConfigured(_("Visible Bound Fields must have a non-empty label. "))
                    if field.help_text:
                        help_text = '<br />' if help_text_br else ''
                        help_text += str(field.help_text)
                        id_ = field.widget.attrs.get('id') or bf.auto_id
                        field_html_id = field.widget.id_for_label(id_) if id_ else ''
                        help_id = field_html_id or bf.html_name
                        help_id += '-help'
                        field_attrs_dict.update({'aria-describedby': help_id})
                        help_attr = ' id="{}" class="help-text"'.format(help_id)
                        help_text = self._html_tag(help_tag, help_text, help_attr)
                    else:
                        help_text = ''
                    if field_attrs_dict:
                        field_display = bf.as_widget(attrs=field_attrs_dict)
                        if field.show_hidden_initial:
                            field_display += bf.as_hidden(only_initial=True)
                    else:
                        field_display = bf
                    html_col_attr = html_class_attr
                    # if not multi_field_row:
                    #     html_col_attr += ' colspan="%(col_count)s"'
                    format_kwargs = {
                        'errors': bf_errors,
                        'label': label,
                        'field': field_display,
                        'help_text': help_text,
                        'html_col_attr': html_col_attr,  # html_class_attr,  # if multi_field_row else '',
                        'html_class_attr': html_class_attr,
                        'css_classes': css_classes,
                        'field_name': bf.html_name,
                    }
                    if multi_field_row:
                        columns_data.append(col_html % format_kwargs)
                        html_row_attr = ''
                    else:
                        columns_data.append(single_col_html % format_kwargs)
                        # html_row_attr = html_class_attr
                        html_row_attr = ''
                row_data.extend(self.make_row(columns_data, error_data, row_tag, html_row_attr))
            # end iterating field rows
            opts['row_data'] = row_data
            # opts['column_count'] = max_fs_columns
        # end iterating fieldsets
        output = self.form_main_rows(html_args, fieldsets, form_col_count)
        row_ender = '' if not single_col_tag else '</' + single_col_tag + '>'
        row_ender += '</' + row_tag + '>'
        if top_errors:
            col_attr = ' id="top_errors"'
            row_attr = ''
            data = ' '.join(top_errors)
            error_row = self.make_headless_row(html_args, data, form_col_count, col_attr, row_attr)
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
                    col_attr = ''
                    row_attr = ''
                    last_row = self.make_headless_row(html_args, str_hidden, form_col_count, col_attr, row_attr)
                    output.append(last_row)
            else:  # If there aren't any rows in the output, just append the hidden fields.
                output.append(str_hidden)
        return mark_safe('\n'.join(output))

    def as_table(self):
        "Overwrite BaseForm.as_table. Return this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            row_tag='tr',
            col_head_tag='th',
            col_tag='td',
            single_col_tag='td',
            col_head_data='%(label)s',
            col_data='%(errors)s%(field)s%(help_text)s',
            help_text_br=True,
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
            col_head_data='',
            col_data='%(errors)s%(label)s%(field)s%(help_text)s',
            help_text_br=False,
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
            col_head_data='',
            col_data='%(label)s%(field)s%(help_text)s',
            help_text_br=False,
            errors_on_separate_row=True,
            as_type='p'
        )

    def as_fieldset(self):
        " Return this form rendered as, or in, HTML <fieldset>s. Untitled fieldsets will be borderless. "
        return self._html_output(
            row_tag='p',
            col_head_tag=None,
            col_tag='span',
            single_col_tag='',
            col_head_data='',
            col_data='%(errors)s%(label)s%(field)s%(help_text)s',
            help_text_br=False,
            errors_on_separate_row=False,
            as_type='fieldset',
        )
