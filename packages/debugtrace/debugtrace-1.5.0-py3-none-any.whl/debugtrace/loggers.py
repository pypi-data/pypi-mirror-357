# loggers.py
# (C) 2020 Masato Kokubo
# since 1.2.0
__author__  = 'Masato Kokubo <masatokokubo@gmail.com>'

from abc import abstractmethod
import datetime
import tzlocal
import logging
from logging import config as logging_config
import os
import sys
from debugtrace import config
from debugtrace import _print as pr

class LoggerBase(object):
    """
    Abstract base class for logger classes.

    ---- Japanese ----

    ロガー クラスの抽象基本クラス。
    """
    __slots__ = ['_config']

    def __init__(self, config: config.Config):
        """
        Initializes this object.

        Args:
            config: the Config object

        ---- Japanese ----

        このオブジェクトを初期化します。

        引数:
            config: Configオブジェクト
        """
        self._config = config

    @abstractmethod
    def print(self, message: str) -> None:
        """
        Outputs the message.

        Args:
            message (str): The message to output

        ---- Japanese ----

        メッセージを出力します。

        引数:
            message (str): 出力するメッセージ
        """
        pass

    def get_log_date_str(self) -> str:
        now = datetime.datetime.now(tzlocal.get_localzone())
        log_date_str = now.strftime(self._config.log_datetime_format)
        return log_date_str

class Std(LoggerBase):
    """
    Abstract base class for StdOut and StdErr classes.

    ---- Japanese ----

    StdOutおよびStdErrクラスの抽象基本クラス。
    """
    __slots__ = LoggerBase.__slots__ + ['_iostream']

    def __init__(self, config: config.Config, iostream):
        """
        Initializes this object.

        Args:
            iostream: Output destination

        ---- Japanese ----

        このオブジェクトを初期化します。

        引数:
            iostream: 出力先
        """
        super().__init__(config)
        self._iostream = iostream
    
    def print(self, message: str) -> None:
        """
        Outputs the message.

        Args:
            message (str): The message to output

        ---- Japanese ----

        メッセージを出力します。

        引数:
            message (str): 出力するメッセージ
        """
        pr._print(super().get_log_date_str() + ' ' + message, self._iostream)

class StdOut(Std):
    """
    A logger class that outputs to sys.stdout.

    ---- Japanese ----

    sys.stdout に出力するロガー クラス。
    """
    def __init__(self, config: config.Config):
        """
        Initializes this object.

        ---- Japanese ----

        このオブジェクトを初期化します。
        """
        super().__init__(config, sys.stdout)

    def __str__(self):
        """
        Returns a string representation of this object.

        Returns:
            str: A string representation of this object

        ---- Japanese ----

        このオブジェクトの文字列表現を返します。

        戻り値 :
            str: このオブジェクトの文字列表現
        """
        return 'sys.stdout'

class StdErr(Std):
    """
    A logger class that outputs to sys.stderr.

    ---- Japanese ----

    sys.stderr に出力するロガー クラス。
    """
    def __init__(self, config: config.Config):
        """
        Initializes this object.

        ---- Japanese ----

        このオブジェクトを初期化します。
        """
        super().__init__(config, sys.stderr)

    def __str__(self):
        """
        Returns a string representation of this object.

        Returns:
            str: A string representation of this object

        ---- Japanese ----

        このオブジェクトの文字列表現を返します。

        戻り値 :
            str: このオブジェクトの文字列表現
        """
        return 'sys.stderr'

class PythonLogging(LoggerBase):
    """
    A logger class that outputs using the logging package.

    ---- Japanese ----

    logging パッケージを使用して出力するロガー クラス。
    """
    __slots__ = LoggerBase.__slots__ + ['_config_file', '_logger', '_logging_logger_name']

    def __init__(self, config: config.Config):
        super().__init__(config)
        self._config_file = config.logging_config_file
        if os.path.exists(config.logging_config_file):
            logging_config.fileConfig(config.logging_config_file)
        else:
            pr._print(f"debugtrace: ({config.config_path}) logging_config_file = '{config.logging_config_file} (Not found)", sys.stderr)

        self._logger = logging.getLogger(config.logging_logger_name)
        self._logging_logger_name = config.logging_logger_name

    def print(self, message: str) -> None:
        """
        Outputs the message.

        Args:
            message (str): The message to output

        ---- Japanese ----

        メッセージを出力します。

        引数:
            message (str): 出力するメッセージ

        """
        self._logger.debug(message)

    def __str__(self):
        """
        Returns a string representation of this object.

        Returns:
            str: A string representation of this object

        ---- Japanese ----

        このオブジェクトの文字列表現を返します。

        戻り値 :
            str: このオブジェクトの文字列表現

        """
        return f"logging.Logger: config file: '{self._config_file}', logger name: '{self._logging_logger_name}"

class File(LoggerBase):
    """
    A logger class that outputs to a file.

    ---- Japanese ----

    ファイルに出力するロガークラス。
    """
    __slots__ = LoggerBase.__slots__ + ['_append', '_log_path']

    def __init__(self, config: config.Config):
        super().__init__(config)
        self._append = False
        self._log_path = ''
        
        log_path = config.logger_name[5:].strip()
        if log_path.startswith('+'):
            self._append = True
            log_path = log_path[1:].strip()
        if len(log_path) <= 0:
            pr._print(f"debugtrace: ('{config.config_path}') logger = {config.logger_name}: There is no file name.", sys.stderr)

        dir_path = os.path.dirname(log_path)
        if os.path.exists(dir_path):
            self._log_path = log_path
        else:
            pr._print(f"debugtrace: The directory '{dir_path}' cannot be found.", sys.stderr)

        if not self._append:
            with open(self._log_path, 'w') as f:
                pass

    def print(self, message: str) -> None:
        if self._log_path == '': return

        with open(self._log_path, 'a', 1, 'utf-8', 'replace', '\n') as f:
            pr._print(super().get_log_date_str() + ' ' + message, file=f)

    def __str__(self):
        """
        Returns a string representation of this object.

        Returns:
            str: A string representation of this object

        ---- Japanese ----

        このオブジェクトの文字列表現を返します。

        戻り値 :
            str: このオブジェクトの文字列表現

        """
        return f"File: '{self._log_path}', append: {self._append}"
