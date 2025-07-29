# state.py
# (C) 2020 Masato Kokubo
__author__  = 'Masato Kokubo <masatokokubo@gmail.com>'

from collections import deque
import datetime

class State(object):
    """
    Holds the trace state for a thread.

    @since: 1.2.0

    ---- Japanese ----

    スレッドのトレース状態を保持します。
    """
    __slots__ = [
        '_thread_id',
        '_nest_level',
        '_previous_nest_level',
        '_previous_line_count',
        '_times',
    ]

    def __init__(self, thread_id: int):
        self._thread_id = thread_id
        self._times = deque()
        self.reset()

    @property
    def thread_id(self) -> int:
        """
        The thread id.

        ---- Japanese ----

        スレッド ID
        """
        return self._thread_id

    @property
    def nest_level(self) -> int:
        """
        The nesting level.

        ---- Japanese ----

        ネストレベル
        """
        return self._nest_level

    @property
    def previous_nest_level(self) -> int:
        """
        The previous nesting level.

        ---- Japanese ----

        以前のネスティング レベル
        """
        return self._previous_nest_level

    @property
    def previous_line_count(self) -> int:
        """
        The previous line count.

        ---- Japanese ----

        以前の行数
        """
        return self._previous_line_count

    @previous_line_count.setter
    def previous_line_count(self, value: int):
        """
        Set the previous line count.

        Args:
            value (int): The value to set

        ---- Japanese ----

        前の行数を指定します。
        
        Args:
            value (int): 設定する値
        """
        self._previous_line_count = value

    def reset(self):
        """
        Reset.

        ---- Japanese ----

        リセットします。
        """
        self._nest_level = 0
        self._previous_nest_level = 0
        self._previous_line_count = 0
        self._times.clear()

    def __str__(self) -> str:
        """
        Returns a string representation of this object.

        Returns:
            str: A string representation of this object.

        ---- Japanese ----

        このオブジェクトの文字列表現を返します。

        戻り値 :
            str: このオブジェクトの文字列表現
        """
        return '(State){'
        + f"thread_id: {self._thread_id}"
        + f", nest_level: {self._nest_level}"
        + f", previous_nest_level: {self._previous_nest_level}"
        + f", previous_line_count: {self._previous_line_count}"
        + f", times: ' {self._times}"
        + '}'

    def up_nest(self):
        """
        Ups the nesting level.

        ---- Japanese ----

        ネスティング レベルを上げます。
        """
        self._previous_nest_level = self._nest_level
        if (self._nest_level >= 0):
            self._times.append(datetime.datetime.now(datetime.timezone.utc))
        self._nest_level += 1

    def down_nest(self) -> datetime.datetime:
        """
        Downs the nesting level.

        Returns:
            datetime.datetime: The time when the corresponding upNest method was invoked

        ---- Japanese ----

        ネスティング レベルを下げます。

        戻り値:
            datetime.datetime: 対応する upNest メソッドが呼び出された時刻
        """
        self._previous_nest_level = self._nest_level
        self._nest_level -= 1
        return self._times.pop() if len(self._times) > 0 else datetime.datetime.now(datetime.timezone.utc)
