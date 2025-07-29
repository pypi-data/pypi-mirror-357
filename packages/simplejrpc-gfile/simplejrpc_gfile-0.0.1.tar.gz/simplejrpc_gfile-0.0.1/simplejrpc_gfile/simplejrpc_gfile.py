import os
import sys
import re
import json
import subprocess
from os import PathLike
from abc import ABCMeta, abstractmethod
from collections import deque
from contextlib import suppress
from typing_extensions import (
    TypeAlias,
    Literal,
    Callable,
    Optional,
    Iterable,
    Any,
    IO,
    Dict,
    Self,
)

__all__ = [
    "Content",
    "FileContent",
    "FileOperator",
    "SimpleFileOperator",
    "PermissionFilerOperator",
    "JsonFileOperator",
    "FilePermission",
    "BigFileOperator",
    "get_env_user_home",
    "get_env_user",
    "make_path",
]

OpenTextModeUpdating: TypeAlias = Literal[
    "r+",
    "+r",
    "rt+",
    "r+t",
    "+rt",
    "tr+",
    "t+r",
    "+tr",
    "w+",
    "+w",
    "wt+",
    "w+t",
    "+wt",
    "tw+",
    "t+w",
    "+tw",
    "a+",
    "+a",
    "at+",
    "a+t",
    "+at",
    "ta+",
    "t+a",
    "+ta",
    "x+",
    "+x",
    "xt+",
    "x+t",
    "+xt",
    "tx+",
    "t+x",
    "+tx",
]
OpenTextModeWriting: TypeAlias = Literal[
    "w", "wt", "tw", "a", "at", "ta", "x", "xt", "tx"
]
OpenTextModeReading: TypeAlias = Literal[
    "r", "rt", "tr", "U", "rU", "Ur", "rtU", "rUt", "Urt", "trU", "tUr", "Utr"
]
OpenTextMode: TypeAlias = (
    OpenTextModeUpdating | OpenTextModeWriting | OpenTextModeReading
)
StrOrBytesPath: TypeAlias = str | bytes | PathLike[str] | PathLike[bytes]  # stable
FileDescriptorOrPath: TypeAlias = int | StrOrBytesPath


class Content:
    """ """

    def __init__(self, content: Any):
        self._content = content

    @property
    def content(self):
        """ """
        return self._content

    def is_digit(self) -> bool:
        """ """
        if isinstance(self._content, str):
            return self._content.isdigit()
        else:
            return False

    def to_int(self) -> int:
        """ """
        if self.is_digit():
            return int(self._content)
        else:
            return 0

    def to_bool(self) -> bool:
        """ """
        return bool(self._content)

    def to_dict(self, default={}) -> Dict[str, Any]:
        """ """
        try:
            return json.loads(self._content)
        except Exception:
            return dict(default)

    def to_json(self, default="{}") -> str:
        """ """
        try:
            return json.dumps(self._content)
        except Exception:
            return default

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, Content):
            return NotImplemented
        return self._content == obj._content

    def __len__(self) -> int:
        return len(self._content)


class FileContent:
    """ """

    def __init__(self, filename: FileDescriptorOrPath, content: Any):
        """ """
        self._filename = filename
        self.content_obj = Content(content)

    @property
    def filename(self):
        """ """
        return self._filename

    @property
    def content(self):
        """ """
        return self.content_obj._content

    def to_dict(self):
        """ """
        return self.content_obj.to_dict()


class FileOperator(metaclass=ABCMeta):
    """ """

    def __init__(
        self,
        filename: FileDescriptorOrPath,
        auto_create: bool = False,
        auto_create_type: Optional[Any] = "",
    ):
        """ """
        self._filename = filename
        self._auto_create = auto_create
        self._auto_create_type = auto_create_type

    def exists(self) -> bool:
        """ """
        return os.path.exists(self._filename)

    def exists_folder(self) -> bool:
        """ """
        if isinstance(self._filename, int):
            # File descriptors do not have a directory
            return False
        return os.path.exists(os.path.dirname(self._filename))

    def _create_empty_folder(self):
        """ """
        os.makedirs(os.path.dirname(self._filename), exist_ok=True)

    def _create_empty_file(self):
        """ """
        if not self._auto_create:
            return
        if self.exists():
            return
        self._create_empty_folder()
        with open(self._filename, "w", encoding="utf-8") as f:
            f.write(self._auto_create_type)
            return

    def open(self, handler: Callable[[IO[Any]], Any], *args, **kwargs) -> str:
        """ """
        self._create_empty_file()
        kwargs["encoding"] = kwargs.get("encoding", "utf-8")
        with open(self._filename, *args, **kwargs) as f:
            return handler(f)

    def iter_open(
        self, handler: Callable[[IO[Any]], Iterable[str]], *args, **kwargs
    ) -> Iterable[str]:
        """ """
        self._create_empty_file()
        kwargs["encoding"] = kwargs.get("encoding", "utf-8")
        with open(self._filename, *args, **kwargs) as f:
            yield from handler(f)

    @abstractmethod
    def read(self, mode: OpenTextMode = "r", **kwargs) -> Any: ...

    @abstractmethod
    def write(self, content: str, mode: OpenTextMode = "w", **kwargs) -> Any: ...

    def file_access(self, mode) -> bool:
        """ """
        return os.access(self._filename, mode)


class SimpleFileOperator(FileOperator):
    """ """

    def _extract_handler(self, kwargs) -> bool:
        """ """
        return not kwargs.get("handler")

    def read(self, mode: OpenTextMode = "r", **kwargs) -> str:
        """ """
        if self._extract_handler(kwargs):
            return super().open(lambda x: x.read(), mode=mode, **kwargs)
        else:
            handler = kwargs.pop("handler")
            return super().open(handler, mode=mode, **kwargs)

    def write(self, content: str, mode: OpenTextMode = "w", **kwargs) -> Any:
        """ """
        if self._extract_handler(kwargs):
            return super().open(lambda x: x.write(content), mode=mode, **kwargs)
        handler = kwargs.pop("handler")
        return super().open(handler, mode=mode, **kwargs)


class FilePermission:
    """ """

    def replace_perm(
        self, filename: FileDescriptorOrPath, file_mode: int = 0, user=""
    ) -> bool:
        """ """
        if not file_mode:  # Handling special situations
            file_mode = 0
        if isinstance(file_mode, str) and file_mode.isdigit():
            """ """
            file_mode = int(file_mode)
        try:
            if file_mode > 0:
                os.chmod(filename, file_mode)
            if user:
                os.chown(filename, user, user)
        except Exception as e:
            return False
        return True


class PermissionFilerOperator(FilePermission, SimpleFileOperator):
    """ """

    def write(
        self, content: str, mode: OpenTextMode = "w", file_mode=0, user="", **kwargs
    ) -> Any:
        """ """
        super().write(content=content, mode=mode, **kwargs)
        return self.replace_perm(self._filename, file_mode=file_mode, user=user)


class JsonFileOperator(PermissionFilerOperator):
    """ """

    def __init__(
        self,
        filename,
        auto_create=False,
        auto_create_type="{}",
        json_encoder=json.dump,
        json_decoder=json.load,
    ):
        super().__init__(filename, auto_create, auto_create_type)
        self.json_encoder = json_encoder
        self.json_decoder = json_decoder

    def write(
        self, content: str, mode: OpenTextMode = "w", file_mode=0, user="", **kwargs
    ) -> Any:
        """ """
        if isinstance(content, str):
            """ """
            return super().write(
                content=content, mode=mode, file_mode=file_mode, user=user, **kwargs
            )
        else:
            kwargs["handler"] = lambda x, content=content: self.json_encoder(content, x)
            return super().write(
                content=content, mode=mode, file_mode=file_mode, user=user, **kwargs
            )

    def read(self, mode: OpenTextMode = "r", **kwargs) -> Any:
        """ """
        kwargs["handler"] = lambda x: self.json_decoder(x)
        return super().read(mode=mode, **kwargs)


def _get_num_lines_result(result, pyVersion):
    """ """
    try:
        try:
            result = json.dumps(result)
            return json.loads(result).strip()
        except Exception:
            if pyVersion == 2:
                result = result.decode("utf8", errors="ignore")
            else:
                result = result.encode("utf-8", errors="ignore").decode(
                    "utf-8", errors="ignore"
                )
        return result.strip()
    except Exception:
        return ""


class BigFileOperator(SimpleFileOperator):
    """ """

    def write(self, content, mode="w", **kwargs):
        return super().write(content, mode, **kwargs)

    def read(self, num, mode="rb", p=1, **kwargs):
        """
        从文件末尾按行读取指定范围的内容

        参数:
            path: 文件路径
            num: 要读取的行数
            p: 页码，默认为1
        返回:
            指定范围的文件内容
        """
        # 参数验证
        if not self.exists():
            return ""
        if isinstance(num, str) and not re.match(r"\d+", num):
            return ""

        pyVersion = sys.version_info[0]
        max_len = 1024 * 1024 * 10
        try:
            start_line = (p - 1) * num
            count = start_line + num
            with open(self._filename, mode=mode, **kwargs) as fp:
                buf = ""
                fp.seek(-1, 2)
                if fp.read(1) == "\n":
                    fp.seek(-1, 2)
                data = []
                total_len = 0
                b = True
                n = 0
                for _ in range(count):
                    while True:
                        newline_pos = str.rfind(str(buf), "\n")
                        pos = fp.tell()
                        if newline_pos != -1:
                            if n >= start_line:
                                line = buf[newline_pos + 1 :]
                                line_len = len(line)
                                total_len += line_len
                                sp_len = total_len - max_len
                                if sp_len > 0:
                                    line = line[sp_len:]
                                with suppress(Exception):
                                    data.insert(0, line)
                            buf = buf[:newline_pos]
                            n += 1
                            break
                        else:
                            if pos == 0:
                                b = False
                                break
                            to_read = min(4096, pos)
                            fp.seek(-to_read, 1)
                            t_buf = fp.read(to_read)
                            if pyVersion == 3:
                                t_buf = t_buf.decode("utf-8", errors="ignore")

                            buf = t_buf + buf
                            fp.seek(-to_read, 1)
                            if pos - to_read == 0:
                                buf = "\n" + buf
                        if total_len >= max_len:
                            break
                    if not b:
                        break
            result = "\n".join(data)
        except Exception:
            if re.match(r"[`\$\&\;]+", self._filename):
                return ""
            result = subprocess.check_output(
                f"tail -n {num} {self._filename}", shell=True, stderr=subprocess.DEVNULL
            ).decode("utf-8", errors="ignore")
            if len(result) > max_len:
                result = result[-max_len:]

        return _get_num_lines_result(result, pyVersion)


def get_env_user_home():
    """Read the user in the system environment variable"""

    output = subprocess.check_output("echo ~", shell=True)
    return os.environ.get("HOME") or output.decode("utf-8").strip()


def get_env_user():
    """Read the user in the system environment variable"""

    output = subprocess.check_output("whoami", shell=True)
    return os.environ.get("USER") or output.decode("utf-8").strip()


def make_path(base_path: str, *args):
    """ """
    u_root = get_env_user_home()
    if len(args) > 0:
        return os.path.join(base_path.format(u_root), *args)
    return base_path.format(u_root)
