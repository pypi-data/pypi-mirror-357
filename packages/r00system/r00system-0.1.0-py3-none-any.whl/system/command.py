import os
import shlex
import subprocess
import time
from typing import Union, List, Dict, Optional

from logger import log
from .helpers.constants import *
from .helpers.exceptions import *
from .helpers.utils import determine_shell_and_command, CMDResult
from .pltform import is_windows

def stream(
        command: Union[str, List[str]],
        ignore_errors: bool = False,
        encoding: str = DEFAULT_ENCODING,
        shell: Optional[bool] = None,
) -> subprocess.Popen | None:
    """
    Выполняет команду в stream режиме.
    :param command: Команда для выполнения
    :param ignore_errors: Игнорировать ошибки выполнения команды.
    :param encoding: Кодировка для декодирования stdout и stderr.
    :param shell: Принудительно установить shell=True или shell=False.
    :return:
    """

    final_command, use_shell = determine_shell_and_command(command, force_shell=shell)
    command_repr = final_command if isinstance(final_command, str) else ' '.join(
        shlex.quote(str(arg)) for arg in final_command)

    log.trace(f"Запускаем команду {command_repr} в stream режиме")

    try:
        process = subprocess.Popen(
            final_command,
            shell=use_shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding=encoding,
            errors='replace',
        )
        return process
    except Exception as e:
        if ignore_errors:
            return None
        raise CommandError(f"🔥 Ошибка при выполнении команды в stream режиме: {shell=}, {command_repr!r}.\nError: {e}") from e


def run(
        command: Union[str, List[str]],
        *,  # Делаем остальные аргументы только именованными
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        ignore_errors: bool = False,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        retry_delay: float = 0.5,  # Задержка между попытками в секундах
        encoding: str = DEFAULT_ENCODING,
        shell: Optional[bool] = None,
        disable_log: bool = False,
        capture_output: bool = True,
        verbose: bool=False
) -> CMDResult | subprocess.CompletedProcess:
    """
    Выполняет команду оболочки и возвращает ее результат.

    Блокирует выполнение до завершения команды или истечения таймаута.
    Автоматически определяет необходимость `shell=True`.
    Поддерживает повторные попытки при неудаче.

    Args:
        command: Команда для выполнения (строка или список аргументов).
        cwd: Рабочая директория для выполнения команды. По умолчанию - текущая.
        env: Словарь переменных окружения для добавления/переопределения.
        ignore_errors: Если True, возвращает CMDResult даже при ошибке выполнения.
                       Если False (по умолчанию), вызывает CommandError при ошибке.
        timeout: Максимальное время выполнения команды в секундах.
        retries: Количество повторных попыток выполнения в случае неудачи (код возврата != 0).
                 Значение 1 означает одну попытку без повторов.
        retry_delay: Задержка между повторными попытками в секундах.
        encoding: Кодировка для декодирования stdout и stderr.
        shell: Принудительно установить shell=True или shell=False.
               None (по умолчанию) включает автоматическое определение.
        disable_log: Если True, отключает логирование выполнения команды.
        capture_output: Сделай False если нужен интерактивный вызов, например открытие файла micro filepath.
        verbose: Если True, включает подробный вывод выполнения команды.

    Returns:
        Объект CMDResult, содержащий детали выполнения команды.

    """
    if not isinstance(command, (str, list)):
        raise TypeError("Аргумент 'command' должен быть строкой или списком строк.")

    if retries < 1:
        retries = 1

    final_command, use_shell = determine_shell_and_command(command, force_shell=shell)
    command_repr = final_command if isinstance(final_command, str) else ' '.join(
        shlex.quote(str(arg)) for arg in final_command)



    process_env = None
    if env:
        process_env = os.environ.copy()
        process_env.update(env)

    for attempt in range(retries):
        attempt_num = attempt + 1
        if attempt > 0:
            if not disable_log:
                log.trace(f"🔁 Повторный запуск комманды [{attempt_num}/{retries}]: {command_repr} ...")
            time.sleep(retry_delay)

        if verbose:
            log.trace(f"Выполняем команду через subprocess.run...")
            log.trace(f"Это команда выполняется: {final_command=}")
            log.trace(f"Это команда для логов:   {command_repr=}")
            log.trace(f"shell={use_shell}")
            log.trace(f"{encoding=}")
            log.trace(f"{timeout=}")
            log.trace(f"{process_env=}")
            log.trace(f"{cwd=}")

        try:
            t0 = time.time()
            process = subprocess.run(
                final_command,
                shell=use_shell,
                capture_output=capture_output,
                check=False,
                encoding=encoding,
                errors='backslashreplace',
                timeout=timeout,
                env=process_env,
                cwd=cwd,
            )
            elapsed = time.time() - t0

            if verbose:
                log.trace(f"subprocess.run завершено.")
                log.trace(f"  returncode: {process.returncode}")
                log.trace(f"  stdout: {process.stdout}")
                log.trace(f"  stderr: {process.stderr}")
                log.trace(f"  время выполнения: {elapsed:.3f} сек.")

            cmdresult = CMDResult(
                command=final_command,  # Сохраняем команду, которая реально выполнялась
                stdout=process.stdout if process.stdout else None,
                stderr=process.stderr if process.stderr else None,
                return_code=process.returncode,
                duration=elapsed,
                process=process
            )

            if verbose or not disable_log:
                if cmdresult.success:
                    log.trace(f"⚙️ {command_repr}, elapsed={elapsed:.2f}, output={cmdresult.output}")
                else:
                    log.trace(
                        f"🔥️ {command_repr}, elapsed={elapsed:.2f}, output={cmdresult.output}, status_code={cmdresult.return_code}")
            return cmdresult

        except Exception as e:
            if ignore_errors:
                return CMDResult(command=command_repr, stdout=None, stderr=str(e), return_code=-1, duration=-1)
            raise CommandError(f"🔥 Ошибка при выполнении команды: {shell=}, {command_repr!r}.\nError: {e}") from e
    raise CommandError(f"🔥 Ошибка при выполнении команды: {command_repr}")


def run_background(
        command: Union[str, List[str]],
        *,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        shell: Optional[bool] = None,
        disable_log: bool = False
) -> subprocess.Popen:
    """
    Запускает команду в фоновом режиме, не дожидаясь ее завершения.

    Использует `subprocess.Popen` для запуска процесса.
    Стандартные потоки вывода (stdout, stderr) процесса перенаправляются в /dev/null (или NUL),
    чтобы избежать блокировки буферов.

    Args:
        command: Команда для выполнения (строка или список).
        cwd: Рабочая директория.
        env: Переменные окружения.
        shell: Принудительно shell=True/False или None для авто-определения.
        disable_log: Если True, отключает логирование выполнения команды.

    Returns:
        Объект `subprocess.Popen`, представляющий запущенный процесс.
        С этим объектом можно взаимодействовать (например, `process.wait()`, `process.terminate()`).

    Raises:
        CommandError: Если не удалось запустить процесс (например, из-за ошибки Popen).
        CommandNotFoundError: Если исполняемый файл команды не найден.
        PermissionDeniedError: Если возникли проблемы с правами доступа при запуске.
        TypeError: Если `command` не является строкой или списком.
    """
    if not isinstance(command, (str, list)):
        raise TypeError("Аргумент 'command' должен быть строкой или списком строк.")

    final_command, use_shell = determine_shell_and_command(command, force_shell=shell)
    command_repr = final_command if isinstance(final_command, str) else ' '.join(
        shlex.quote(str(arg)) for arg in final_command)

    if not disable_log:
        log.trace(f"⚙️ в фоне: {command_repr} (shell={use_shell})")

    process_env = None
    if env:
        process_env = os.environ.copy()
        process_env.update(env)

    try:
        # Определяем, куда перенаправлять вывод
        devnull = open(os.devnull, 'w')

        process = subprocess.Popen(
            final_command,
            shell=use_shell,
            stdout=devnull,
            stderr=devnull,
            encoding=DEFAULT_ENCODING,  # Кодировка важна для Popen, даже если вывод перенаправлен
            errors='backslashreplace',
            env=process_env,
            cwd=cwd,
            close_fds=True if not is_windows() else False  # Закрывать файловые дескрипторы (кроме 0,1,2) на Unix
        )
        return process

    except Exception as e:
        if not disable_log:
            log.error(f"🔥 Не удалось запустить фоновый процесс: {command_repr}", exc_info=True)
        raise CommandError(f"🔥 Не удалось запустить фоновый процесс: {final_command} -> {e}") from e


def kill_process(name_pattern: str) -> CMDResult:
    """
    Завершает процессы, соответствующие шаблону имени, в Windows или Linux.

    Args:
        name_pattern: Имя или шаблон имени процесса для завершения.
                      В Linux используется как шаблон регулярного выражения для `pkill -f`.

    """
    result = run(f'pkill -f "{name_pattern}"', ignore_errors=True, retries=1, disable_log=True)
    log.trace(f"Killed procces '{name_pattern}'")
    return result


def exists_process(name_pattern: str, kill: bool = False, ) -> bool:
    """
    Проверяет, запущен ли процесс, соответствующий шаблону имени, и опционально завершает его

    Args:
        name_pattern: Имя или шаблон имени процесса.
                     В Linux используется с `pgrep -f` (поиск по всей командной строке).
        kill: Если True, попытаться завершить найденные процессы (`kill -9`/`taskkill /F`).
                     принадлежащих другим пользователям (например, root).

    Returns:
        True, если процесс запущен
        False, если процесс не найден или убит
    """
    cmd_check_list = ["pgrep", "-f", name_pattern]
    result_check = run(cmd_check_list, ignore_errors=True, retries=1, disable_log=True)
    if result_check.success:
        if result_check.stdout:
            process_found = True
            pids_to_kill = result_check.stdout.splitlines()  # Получаем список PID
            log.trace(f"Found proccess: {', '.join(pids_to_kill)}")
        else:
            return False
    else:
        return False

    if process_found:
        if kill and pids_to_kill:
            result_kill = kill_process(name_pattern)
            if not result_kill.success:
                log.warning(
                    f"🔥 kill -9 для PID(ов) {', '.join(pids_to_kill)} завершилась code={result_kill.return_code}. Возможно, процесс уже завершен. Stderr: {result_kill.stderr or 'N/A'}")
                return True
            else:
                return False
        else:
            return True
