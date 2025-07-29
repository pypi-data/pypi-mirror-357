# config.py
# (C) 2020 Masato Kokubo
# since 1.2.0
__author__  = 'Masato Kokubo <masatokokubo@gmail.com>'

import configparser
import os
import sys
from typing import TypeVar
from debugtrace import _print as pr

_VT = TypeVar("_VT", bool, int, str) # Value Type

class Config(object):
    """
    Retains the contents set in debugtrace.ini.

    ---- Japanese ----

    debugtrace.iniで設定されている内容保持します。
    """
    def __init__(self, config_path: str):
        """
        Reads the file in the specified path and retains the settings.
        
        Args:
            config_path (str): Configuration file path

        ---- Japanese ----

        指定のパスのファイルを読み込み設定内容を保持します。

        引数:
            config_path (str): 設定ファイルのパス
        """
        self.config_path = config_path
        self._config_parser = configparser.ConfigParser()
        if os.path.exists(self.config_path):
            self._config_parser.read(self.config_path)
        else:
            self.config_path = '<No config file>'

        self.logger_name               = self._get_value('logger'                   , 'stderr'      )
        self.logging_config_file       = self._get_value('logging_config_file'      , 'logging.conf')
        self.logging_logger_name       = self._get_value('logging_logger_name'      , 'debugtrace'  )
        self.log_datetime_format       = self._get_value('log_datetime_format'      , '%Y-%m-%d %H:%M:%S.%f%z')
        self.enabled                   = self._get_value('enabled'                  , True          )
        self.enter_format              = self._get_value('enter_format'             , 'Enter {0} ({1}:{2}) <- ({3}:{4})')
        self.leave_format              = self._get_value('leave_format'             , 'Leave {0} ({1}:{2}) duration: {3}')
        self.thread_boundary_format    = self._get_value('thread_boundary_format'   , '______________________________ {0} #{1} ______________________________') # since 1.2.0
        self.maximum_indents           = self._get_value('maximum_indents'          , 32   )
        self.indent_string             = self._get_value('indent_string'            , '| ' )
        self.data_indent_string        = self._get_value('data_indent_string'       , '  ' )
        self.limit_string              = self._get_value('limit_string'             , '...')
        self.non_output_string         = self._get_value('non_output_string'        , '...')
        self.circular_reference_string = self._get_value('circular_reference_string', '*** Circular Reference ***')
        self.varname_value_separator   = self._get_value('varname_value_separator'  , ' = '       )
        self.key_value_separator       = self._get_value('key_value_separator'      , ': '        )
        self.print_suffix_format       = self._get_value('print_suffix_format'      , ' ({1}:{2})')
        self.count_format              = self._get_value('count_format'             , 'count:{}'  )
        self.minimum_output_count      = self._get_value('minimum_output_count'     , 128 ) # 128 <- since 1.4.0, 16 <- 5 since 1.2.0
        self.length_format             = self._get_value('length_format'            , 'length:{}' )
        self.minimum_output_length     = self._get_value('minimum_output_length'    , 256 ) # 256 <- since 1.4.0, 16 <- 5 since 1.2.0
        self.data_output_width         = self._get_value('data_output_width'        , 70 )
        self.bytes_count_in_line       = self._get_value('bytes_count_in_line'      , 16 )
        self.collection_limit          = self._get_value('collection_limit'         , 128) # 128 <- 512 since 1.2.0
        self.bytes_limit               = self._get_value('bytes_limit'              , 256) # 256 <- 8192 since 1.2.0
        self.string_limit              = self._get_value('string_limit'             , 256) # 256 <- 8192 since 1.2.0
        self.reflection_limit          = self._get_value('reflection_limit'         , 4  )

    def _get_value(self, key: str, fallback: _VT) -> _VT:
        """
        Gets the value related the key from debugtrace.ini file.

        Args:
            key (str): The key
            fallback (_VT): Value to return when the value related the key is undefined

        Returns:
            _VT: Value related the key

        ---- Japanese ----

        debugtrace.ini ファイルからキーに関連する値を取得します。

        引数:
            key (str): キー
            fallback (_VT): キーに関連する値が未定義の場合に返す値

        戻り値:
            _VT: キーに関連する値
        """
        value = fallback
        try:
            if type(fallback) == bool:
                value = self._config_parser.getboolean('debugtrace', key, fallback=fallback)
            elif type(fallback) == int:
                value = self._config_parser.getint('debugtrace', key, fallback=fallback)
            else:
                value = self._config_parser.get('debugtrace', key, fallback=fallback)
                value = value.replace('\\s', ' ')

        except BaseException as ex:
            pr._print(f"debugtrace: ({self.config_path}) key: {key}, error: {str(ex)}", sys.stderr)

        return value
