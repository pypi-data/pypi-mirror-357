import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def _get_git_username(project_path: str = ".") -> str:
    """
    获取 Git 用户名，优先仓库配置，其次全局配置。
    """
    try:
        if (Path(project_path) / ".git").exists():
            username = subprocess.check_output(
                ["git", "-C", project_path, "config", "--get", "user.name"],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=2
            ).strip()
            if username:
                return username
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass

    try:
        username = subprocess.check_output(
            ["git", "config", "--global", "--get", "user.name"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2
        ).strip()
        return username
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return ""


# 程序加载此模块时自动执行
GIT_USERNAME = _get_git_username()
