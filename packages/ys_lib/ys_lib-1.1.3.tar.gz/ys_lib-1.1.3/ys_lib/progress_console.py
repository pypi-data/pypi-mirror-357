# -*- coding: utf-8 -*-
import collections
import datetime
import functools
import logging
import multiprocessing
import threading
import time
from rich.console import Console
from rich.containers import Lines
from rich.layout import Layout
from rich.live import Live
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import BarColumn, DownloadColumn, Progress, TextColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.text import Text
from typing import Deque, List


# 自定义日志处理器 - 将日志存入缓冲区
class BufferedRichHandler(RichHandler):
    def __init__(self, buffer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buffer: Deque[Text] = buffer
        self.counter = multiprocessing.Value('l', 0)

    def emit(self, record: logging.LogRecord):
        # 将日志记录转化为格式化文本
        match int(record.levelno):
            case logging.DEBUG:
                style = "bright_blue"
            case logging.INFO:
                style = "white"
            case logging.WARNING:
                style = 'bright_yellow'
            case logging.ERROR:
                style = 'bright_red'
            case logging.CRITICAL:
                style = 'white on red'
            case _:
                style = 'white'
        text = Text()
        dt = datetime.datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        text.append(Text(f'{dt}.{int(record.msecs):03d}', style="green"))
        text.append(Text(f' | ', style="white"))
        text.append(Text(f'{record.levelname:<8s}', style=style))
        text.append(Text(f' | ', style="white"))
        text.append(Text(f'{record.module}', style='cyan'))
        text.append(Text(f':', style="white"))
        text.append(Text(f'{record.funcName}', style='cyan'))
        text.append(Text(f':', style="white"))
        text.append(Text(f'{record.lineno}', style='cyan'))
        text.append(Text(f' - ', style="white"))
        text.append(Text(f'{record.msg}\n', style=style))
        # 将格式化消息添加到缓冲区
        self.buffer.appendleft(text)
        with self.counter.get_lock():
            self.counter.value += 1


class ProgressConsole:
    MAX_LOGS: int = 1000

    layout = Layout()
    layout.split(
        Layout(name="progress", size=2, visible=False),
        Layout(name="logs", ratio=1),
    )
    progress: Progress| None = None
    logs: Deque[Text] = collections.deque(maxlen=MAX_LOGS)
    handler = BufferedRichHandler(buffer=logs, rich_tracebacks=True)
    logging.basicConfig(level="NOTSET", handlers=[handler])
    console = Console(record=True)

    @classmethod
    def new_progress(cls, filename: bool = False) -> Progress:
        cs = [
            TextColumn("[yellow]{task.description}", justify="left"),
            "•",
            TextColumn("[bold blue]{task.fields[filename]}", justify="right") if filename else None,
            "•" if filename else None,
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
        ]
        return Progress(*[c for c in cs if c is not None])

    @classmethod
    def set_progress(cls, progress: Progress):
        cls.progress = progress
        cls.layout["progress"].visible = True
        cls.layout["progress"].update(
            Panel(cls.progress, title="进度监控", border_style="blue")
        )

    @classmethod
    def update_log_display(cls):
        """更新日志区域的显示内容"""
        # 添加所有缓冲区中的日志，每行之间用换行符分隔
        height: int = cls.console.height
        lines = []
        for i, line in enumerate(cls.logs.copy()):
            lines.append(line)
            if i == height - 1:
                break
        lines = Lines(lines)
        text = Text().join(lines)
        cls.layout["logs"].update(
            Panel(text, title=f"日志", border_style="green")
        )

    @classmethod
    def live(cls, *partials: functools.partial):
        # 使用Live显示动态界面
        counter: int = 0
        size: int = 0
        with Live(cls.layout, console=cls.console, refresh_per_second=20, screen=True) as live:
            task_threads = []
            for partial in partials:
                task_thread = threading.Thread(target=partial, daemon=True)
                task_thread.start()
                task_threads.append(task_thread)
            for task_thread in task_threads:
                while task_thread.is_alive():
                    # 按需更新日志
                    cls.update_log_display()
                    _counter = cls.handler.counter.value
                    if _counter != counter:
                        cls.update_log_display()
                        counter = _counter
                    # 调整进度条区域高度
                    if cls.progress:
                        _size: int = len(cls.progress.tasks) + 2
                        if _size != size:
                            cls.layout["progress"].size = size = _size
                    live.refresh()
                    time.sleep(0.05)
        cls.console.print(cls.layout)
        cls.console.log("[bold green]\n所有任务已完成！")


logging.getLogger().setLevel(logging.CRITICAL)
logger = logging.getLogger("rich")
logger.setLevel(logging.DEBUG)


if __name__ == '__main__':

    progress = ProgressConsole.new_progress(filename=False)

    def run_tasks(progress: Progress) -> None:
        task1 = progress.add_task(description="[cyan]下载文件", total=100)
        task2 = progress.add_task(description="[green]处理数据", total=150)
        task3 = progress.add_task(description="[green]处理数据1", total=60)
        task3_done = False

        try:
            while not progress.finished:
                progress.update(task1, advance=0.5)
                progress.update(task2, advance=0.8)
                if not task3_done:
                    progress.update(task3, advance=2)
                time.sleep(1)
                # 模拟日志输出
                logger.info("任务进行中... 状态正常")
                logger.warning(time.time())
                if progress.tasks[0].completed > 30:
                    logger.warning("遇到非关键性延迟")
                if progress.tasks[1].completed > 100:
                    logger.error("数据处理阶段出现异常")
                if len(progress.tasks) > 2 and progress.tasks[2].completed >= 60:
                    progress.stop_task(task3)
                    progress.remove_task(task3)
                    task3_done = True
                # logger.debug(time.time())
                # logger.error(time.time())
                # logger.critical(time.time())
        except Exception as e:
            logger.exception(e)

    ProgressConsole.set_progress(progress=progress)
    ProgressConsole.live(functools.partial(run_tasks, progress), functools.partial(run_tasks, progress))
