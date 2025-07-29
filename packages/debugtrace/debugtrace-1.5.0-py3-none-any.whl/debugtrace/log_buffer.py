# log_buffer.py
# (C) 2020 Masato Kokubo
from __future__ import annotations

__author__  = 'Masato Kokubo <masatokokubo@gmail.com>'

class LogBuffer(object):
    """
    Buffers logs.
    
    ---- Japanese ----

    ログをバッファリングします。
    """
    __slots__ = [
        '_data_output_width',
        '_nest_level',
        '_append_nest_level',
        '_lines',
        '_last_line',
    ]

    def __init__(self, data_output_width: int) -> None:
        """
        Initializes this object.
        
        Args:
            data_output_width (int): Maximum data output width

        ---- Japanese ----

        このオブジェクトを初期化します。

        引数:
            data_output_width (int): 最大データ出力幅
        """
        self._data_output_width = data_output_width
        self._nest_level = 0
        self._append_nest_level = 0

        # tuples of data indentation level and log string
        self._lines: list[tuple[int, str]] = []

        # buffer for a line of logs
        self._last_line = ''

    def line_feed(self) -> None:
        """
        Breaks the current line.

        ---- Japanese ----

        現在の行を改行します。
        """
        self._lines.append((self._nest_level + self._append_nest_level, self._last_line.rstrip()))
        self._append_nest_level = 0
        self._last_line = ""

    def up_nest(self) -> None:
        """
        Ups the data nesting level.

        ---- Japanese ----

        データのネスト レベルを上げます。
        """
        self._nest_level += 1

    def down_nest(self) -> None:
        """
        Downs the data nesting level.

        ---- Japanese ----

        データのネスト レベルを下げます。
        """
        self._nest_level -= 1

    def append(self, value: object, nest_level:int = 0, no_break: bool = False) -> LogBuffer:
        """
        Appends a string representation of the value.

        Args:
            value (object): The value to append
            nest_level (int, optional): The nesting level of the value. Defaults to 0
            no_break (bool, optional): If True, does not break even if the maximum width is exceeded.
                Defaults to False

        Returns:
            LogBuffer: This object

        ---- Japanese ----

        値の文字列表現を追加します。
        
        引数:
            value (object): 追加する値
            nest_level (int, optional): 値のネストレベル。 デフォルトは0
            no_break (bool, optional): true の場合、最大幅を超えてもブレークしない。デフォルトはFalse

        戻り値:
            LogBuffer: このオブジェクト
        """
        if value is not None:
            string = str(value)
            if not no_break and self.length > 0 and self.length + len(string) > self._data_output_width:
                self.line_feed()
            self._append_nest_level = nest_level
            self._last_line += string
        return self

    def no_break_append(self, value: object) -> LogBuffer:
        """
        Appends a string representation of the value.
        Does not break even if the maximum width is exceeded.

        Args:
            value (object): The value to append

        Returns:
            LogBuffer: This object

        ---- Japanese ----

        値の文字列表現を追加します。最大幅を超えても改行しません。

        引数:
            value (オブジェクト): 追加する値

        戻り値:
            LogBuffer: このオブジェクト
        """
        return self.append(value, 0, True)

    def append_buffer(self, separator: str, buff: LogBuffer) -> LogBuffer:
        """
        Appends lines of another LogBuffer.

        Args:
            separator (str): Separator string to append. Do not append if empty.
            buff (LogBuffer): Another LogBuffer

        Returns:
            LogBuffer: This object

        ---- Japanese ----

        別のLogBufferの行を追加します。

        引数:
            separator (str): 追加するセパレーター文字列。空文字列なら追加しない
            buff (LogBuffer): 別のLogBuffer

        戻り値:
            LogBuffer: このオブジェクト
        """
        if separator != '':
            self.append(separator, 0, True)
        index = 0
        for line in buff.lines:
            if index > 0:
                self.line_feed()
            self.append(line[1], line[0], index == 0 and separator != '')
            index += 1
        return self

    @property
    def length(self) -> int:
        """
        The length of the last line.

        ---- Japanese ----

        最後の行の長さ。
        """
        return len(self._last_line)

    @property
    def is_multi_lines(self) -> bool:
        """
        True if multiple line, false otherwise.

        ---- Japanese ----

        複数行の場合はTrue、それ以外の場合はFalse。
        """
        return len(self._lines) > 1 or len(self._lines) == 1 and self.length > 0

    @property
    def lines(self) -> list:
        """
        A list of tuple of data indentation level and log string.

        ---- Japanese ----

        データのインデント レベルとログ文字列のタプルのリスト。
        """
        lines = self._lines.copy()
        if self.length > 0:
            lines.append((self._nest_level, self._last_line))
        return lines
