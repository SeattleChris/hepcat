import re
import json
from django.core.management import BaseCommand
from django.urls import resolvers


class Command(BaseCommand):

    all_columns = ['source', 'name', 'pattern', 'lookup_str', 'args']
    rejected_data = [{'source': 'admin', 'name': 'view_on_site'}, ]
    initial_sort = ['source', 'name']
    initial_sub_cols = ['source', 'name', 'lookup_str']
    initial_sub_rules = [('^django.contrib', 'cb '), ('^django_registration', 'd_reg '), ('^django', '')]
    EMPTY_VALUE = "************* NO URLS FOUND *************"
    MIN_WIDTH = 4
    title = None
    col_widths = None

    def add_arguments(self, parser):
        """Both positional and named arguments are defined. Help documentation generated from this content.  """
        # Positional arguments
        parser.add_argument('sources', nargs='*', type=str, default=[], metavar='source',
                            help='Only show url info from the namespace or module source(s) listed. Default: show all.')
        # Optional Named Arguments: Rows (modules) and Columns (info about the url setting).
        parser.add_argument('--ignore', nargs='*', default=[], help='List of sources to ignore.', metavar='source')
        parser.add_argument('--only', nargs='*', help='Only show the following columns. ', metavar='col')
        parser.add_argument('--not', nargs='*', default=[], help='Do NOT show the following columns.', metavar='col')
        parser.add_argument('--sort', nargs='*', default=self.initial_sort,  metavar='col',
                            help='Sort by, in order of priority, column(s) value. Default: source name. ',)
        # Optional Named Arguments: String substitutions for tighter view and readability.
        parser.add_argument('--long', '-l', action='store_true', help='Show full text: remove default substitutions.', )
        parser.add_argument('--sub-cols', nargs='*', action='store', default=self.initial_sub_cols,
                            help='Columns to apply the default substitutions. ', metavar='col', )
        parser.add_argument('--add', '-a', nargs=2, default=[], action='append', metavar=('regex', 'value', ),
                            help='Add a substitution rule: regex, value.', )
        parser.add_argument('--cols', '-c', nargs='*', metavar='col',
                            help='Columns to apply added substitutions. If none given, defaults to sub-cols. ', )
        # Optional Named Argument: Flag for returning results when called within code instead of command line.
        parser.add_argument('--data', '-d', action='store_true', help='Return results usable in application code.', )

    def get_col_names(self, kwargs):
        col_names = kwargs['only'] or self.all_columns
        return [ea for ea in col_names if ea not in kwargs['not']]

    def get_sub_rules(self, kwargs):
        sc = kwargs.get('sub_cols', [])
        if kwargs['long']:
            sub_rules = []
        else:
            sub_rules = [(*rule, sc) for rule in self.initial_sub_rules]
        add_rules = [(*rule, kwargs['cols'] or sc) for rule in kwargs['add']]
        sub_rules.extend(add_rules)
        return sub_rules

    def collect_urls(self, urls=None, source=None, prefix=None):
        """Called recursively for URLResolver until base case URLPattern. Ultimately returning a list of data dicts. """
        if urls is None:
            urls = resolvers.get_resolver()
        prefix = prefix or []
        if isinstance(urls, resolvers.URLResolver):
            name = urls.urlconf_name
            if isinstance(name, (list, tuple)):
                name = ''
            elif not isinstance(name, str):
                name = name.__name__
            source = urls.namespace or name.split('.')[0] or source
            res = []
            for x in urls.url_patterns:
                res += self.collect_urls(x, source=source, prefix=prefix + [str(urls.pattern)])
            return res
        elif isinstance(urls, resolvers.URLPattern):
            pattern = prefix + [str(urls.pattern)]
            pattern = ''.join([ea for ea in pattern if ea])[1:]
            data = [source, urls.name, pattern, urls.lookup_str, dict(urls.default_args)]
            return [dict(zip(self.all_columns, data))]
        else:
            raise ValueError(repr(urls))

    def data_to_string(self, data):
        """Takes a list of url data, with each row as a list of columns, and formats for a table looking layout. """
        if not data:
            return self.EMPTY_VALUE
        if len(self.title) == 1:
            result = [' | '.join(ea) for ea in data]
        else:
            widths = [self.col_widths.get(key, self.MIN_WIDTH) for key in self.title]
            bar = ['*' * width for width in widths]
            data = [self.title[:], bar] + data
            result = [' | '.join(('{:%d}' % widths[i]).format(v) for i, v in enumerate(ea)) for ea in data]
        return '\n'.join(result)

    def get_url_data(self, sources=None, ignore=None, cols=None, sort=None, sub_rules=None):
        """Collects all urls, then filters down to the desired data. Sets title & col_widths, Returns a 2d data list."""
        all_urls = self.collect_urls()
        if not all_urls:
            return []
        if sort:
            all_urls = sorted(all_urls, key=lambda x: [str(x[key] or '') for key in sort])
        title = {key: key for key in all_urls[0].keys()}
        all_urls.append(title)
        if sources:
            sources.append('source')
        remove_idx, col_widths = [], {}
        for i, u in enumerate(all_urls):
            for col in ['name', 'args']:
                val = u[col]
                u[col] = '' if val is None else str(val)
            # Prep removal, and don't compute length, for ignored sources or known rejected_data combo(s)
            is_rejected = any(all(u[k] == v for k, v in condition.items()) for condition in self.rejected_data)
            if u['source'] in ignore or is_rejected or (sources and u['source'] not in sources):
                remove_idx.append(i)
                continue
            if sub_rules:
                for regex, new_str, sub_cols in sub_rules:
                    for col in sub_cols:
                        u[col] = re.sub(regex, new_str, u[col])
            for k, v in list(u.items()):  # could skip last column length since there is no ending border.
                u[k] = v = v or ''
                col_widths[k] = max(len(v), col_widths.get(k, 0))
        for idx in reversed(remove_idx):
            all_urls.pop(idx)
        if len(all_urls) == 1:
            return []
        result = [[v for k, v in u.items() if k in cols] for u in all_urls]
        self.title = result.pop()
        self.col_widths = col_widths
        return result

    def handle(self, *args, **kwargs):
        """Main interface, called to determine response. """
        col_names = self.get_col_names(kwargs)
        sub_rules = self.get_sub_rules(kwargs)
        result = self.get_url_data(kwargs['sources'], kwargs['ignore'], col_names, kwargs['sort'], sub_rules)
        if kwargs['data']:
            return json.dumps(result)
        else:
            result = self.data_to_string(result)
            self.stdout.write(result)
            return 0
