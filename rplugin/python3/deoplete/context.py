# ============================================================================
# FILE: context.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import re

from os.path import exists


class Context(object):

    def __init__(self, vim):
        self._vim = vim
        self._prev_filetype = self._vim.eval('&l:filetype')
        self._cached = self._init_cached()
        self._cached_filetype = self._init_cached_filetype(
            self._prev_filetype)

    def get(self, event):
        text = self._vim.call('deoplete#util#get_input', event)
        [filetype, filetypes, same_filetypes] = self._vim.call(
            'deoplete#util#get_context_filetype', text, event)

        window = self._vim.current.window
        m = re.search(r'\w$', text)
        word_len = len(m.group(0)) if m else 0
        width = window.width - window.cursor[1] + word_len
        max_width = (width * 2 / 3)

        context = {
            'changedtick': self._vim.current.buffer.vars.get(
                'changedtick', 0),
            'event': event,
            'filetype': filetype,
            'filetypes': filetypes,
            'input': text,
            'max_abbr_width': max_width,
            'max_kind_width': max_width,
            'max_menu_width': max_width,
            'next_input': self._vim.call(
                'deoplete#util#get_next_input', event),
            'position': self._vim.call('getpos', '.'),
            'same_filetypes': same_filetypes,
        }
        context.update(self._cached)

        if filetype != self._prev_filetype:
            self._prev_filetype = filetype
            self._cached_filetype = self._init_cached_filetype(filetype)

        context.update(self._cached_filetype)

        return context

    def _init_cached_filetype(self, filetype):
        return {
            'keyword_pattern': self._vim.call(
                'deoplete#util#get_keyword_pattern', filetype),
            'sources': self._vim.call(
                'deoplete#custom#_get_filetype_option',
                'sources', filetype, []),
        }

    def _init_cached(self):
        bufnr = self._vim.call('expand', '<abuf>')
        if not bufnr:
            bufnr = self._vim.current.buffer.number
        if not bufnr:
            bufnr = -1
            bufname = ''
        else:
            bufname = self._vim.buffers[int(bufnr)].name
        buftype = self._vim.current.buffer.options['buftype']
        bufpath = self._vim.call('fnamemodify', bufname, ':p')
        if not exists(bufpath) or 'nofile' in buftype:
            bufpath = ''

        return {
            'bufnr': bufnr,
            'bufname': bufname,
            'bufpath': bufpath,
            'camelcase': self._vim.call(
                'deoplete#custom#_get_option', 'camel_case'),
            'complete_str': '',
            'custom': self._vim.call('deoplete#custom#_get'),
            'cwd': self._vim.call('getcwd'),
            'encoding': self._vim.options['encoding'],
            'ignorecase': self._vim.call(
                'deoplete#custom#_get_option', 'ignore_case'),
            'is_windows': self._vim.call('has', 'win32'),
            'smartcase': self._vim.call(
                'deoplete#custom#_get_option', 'smart_case'),
            'vars': {x: y for x, y in self._vim.eval('g:').items()
                     if x.startswith('deoplete#') and
                     not x.startswith('deoplete#_')},
        }
